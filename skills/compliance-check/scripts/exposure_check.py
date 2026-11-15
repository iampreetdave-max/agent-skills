"""Find secrets and internal endpoints that a crawler or scanner could reach.

    python exposure_check.py --dir public --dir out --url https://example.com

--dir   folders that get published as static files (public/, static/, the build output).
        Flags files that must never be public (.env, keys, service-account and Firebase admin
        JSON, .git, database dumps) and text files that contain secret-looking strings.
--url   the live site. Probes the paths scanners try every day (/.env, /.git/config,
        /google-credentials.json, /api/console/api_server ...). A path counts as exposed only
        if it answers 200 with something other than the site's normal not-found page.
        Also reads robots.txt, sitemap.xml and llms.txt for links to internal endpoints.

Stdlib only. Reads and fetches, never writes. Exits 1 if anything is EXPOSED.
"""
import argparse
import os
import re
import sys
import urllib.error
import urllib.request
import uuid

BAD_NAMES = [
    (r"(^|/)\.env($|\.)", "environment file"),
    (r"(^|/)\.git(/|$)", "git metadata"),
    (r"\.(pem|key|p12|pfx|jks|keystore)$", "private key or keystore"),
    (r"(^|/)id_(rsa|ed25519|ecdsa)$", "SSH private key"),
    (r"service[-_]?account.*\.json$", "service-account credentials"),
    (r"firebase.*(admin|adminsdk|credential).*\.json$", "Firebase admin credentials"),
    (r"google.*credential.*\.json$", "Google credentials"),
    (r"(^|/)(credentials|secrets?)\.(json|ya?ml|txt)$", "credentials file"),
    (r"(^|/)config\.env$", "environment file"),
    (r"(^|/)\.npmrc$", "npm config (may hold tokens)"),
    (r"\.(sql|sqlite3?|db|dump|bak)$", "database dump or backup"),
]
SECRET_TEXT = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r'"type"\s*:\s*"service_account"', "service-account JSON"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"sk-ant-[A-Za-z0-9_-]{20,}", "Anthropic API key"),
    (r"sk-(proj-)?[A-Za-z0-9]{32,}", "OpenAI-style API key"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub token"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API key (often public by design; check its restrictions)"),
    (r"xox[abprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"(sk|rk)_live_[A-Za-z0-9]{20,}", "Stripe live secret key"),
]
WARN_NAMES = [(r"\.map$", "source map (exposes original source; fine only if intended)")]
PROBE_PATHS = [
    "/.env", "/.env.local", "/.env.production", "/config.env", "/.git/config", "/.git/HEAD", "/.npmrc",
    "/.aws/credentials", "/credentials.json", "/google-credentials.json", "/google-service-account.json",
    "/service-account.json", "/sa.json", "/firebase-admin.json", "/firebase-credentials.json",
    "/backup.sql", "/db.sqlite", "/dump.sql", "/.DS_Store", "/phpinfo.php", "/server-status",
    "/actuator/env", "/api/console/api_server", "/v1/secret/data/", "/admin/.env", "/portal/.env",
]
INTERNAL = re.compile(r"/(api|admin|internal|debug|private|graphql|console|actuator|webhooks?|\.git)(/|$)|/\.env", re.I)

findings = []


def report(level, where, what):
    findings.append((level, where, what))


def scan_dir(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("node_modules",)]
        for name in files + [d for d in dirs if d == ".git"]:
            path = os.path.join(base, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            for pat, why in BAD_NAMES:
                if re.search(pat, rel, re.I):
                    report("EXPOSED", f"{root}/{rel}", f"{why} in a published folder")
            for pat, why in WARN_NAMES:
                if re.search(pat, rel, re.I):
                    report("CHECK", f"{root}/{rel}", why)
            if os.path.isfile(path) and os.path.getsize(path) < 2_000_000:
                try:
                    text = open(path, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                for pat, why in SECRET_TEXT:
                    if re.search(pat, text):
                        level = "CHECK" if why.startswith("Google API key") else "EXPOSED"
                        report(level, f"{root}/{rel}", f"contains {why}")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "exposure-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.headers.get("content-type", ""), r.read(200_000)
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("content-type", ""), b""
    except Exception:
        return 0, "", b""


def scan_url(base):
    base = base.rstrip("/")
    _, _, soft404 = fetch(f"{base}/{uuid.uuid4().hex}-not-here")  # what "not found" looks like here
    for path in PROBE_PATHS:
        status, ctype, body = fetch(base + path)
        if status != 200 or not body or body == soft404:
            continue
        if ctype.startswith("text/html"):  # often an app's catch-all page, not the file itself
            report("CHECK", base + path, f"answers 200 with an HTML page ({len(body)} bytes); open it and confirm it is not the real file")
        else:
            report("EXPOSED", base + path, f"answers 200 ({ctype or 'no type'}, {len(body)} bytes); a scanner can read it")
    for path in ("/robots.txt", "/sitemap.xml", "/llms.txt"):
        status, _, body = fetch(base + path)
        if status != 200:
            continue
        text = body.decode("utf-8", "ignore")
        listed = set(re.findall(r"(?:Disallow|Allow):\s*(\S+)", text)) | set(re.findall(r"https?://[^\s<>\"')]+", text))
        for item in sorted(listed):
            if INTERNAL.search(item):
                if path == "/robots.txt":
                    report("CHECK", base + path, f"lists {item}; a Disallow line hides nothing and advertises the path, so keep it only for public endpoints the site's own pages already call")
                else:
                    report("EXPOSED", base + path, f"lists internal endpoint {item}; take it out")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append", default=[], help="a published folder (repeatable)")
    ap.add_argument("--url", action="append", default=[], help="a live site to probe (repeatable)")
    a = ap.parse_args()
    if not a.dir and not a.url:
        sys.exit(__doc__)
    for d in a.dir:
        if os.path.isdir(d):
            scan_dir(d)
    for u in a.url:
        scan_url(u)
    if not findings:
        print("OK: nothing secret is reachable in the folders and sites checked.")
    for level, where, what in sorted(findings, key=lambda f: f[0] != "EXPOSED"):
        print(f"{level:8} {where}: {what}")
    return 1 if any(f[0] == "EXPOSED" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
