"""Audit a dataset before any modelling.

    python audit.py data.csv --target won [--time match_date] [--sep ";"]

Prints size, types, missing values, duplicates, constant and ID-like columns, target balance,
the time range, and leak suspects. Needs pandas (and pyarrow for .parquet). Reads, never writes.
"""
import argparse
import re
import sys

import pandas as pd

# Words that often mean "known only after the event". A hint for a human, not a verdict.
POST_EVENT = re.compile(r"final|result|outcome|closing|close_|_close|post|after|settled|winner|"
                        r"full_?time|\bft_|_ft\b|label|target|actual|resolved|churned", re.I)


def leak_suspects(df, target):
    y = df[target]
    out = []
    for col in df.columns:
        if col == target:
            continue
        x = df[col]
        why = []
        if POST_EVENT.search(col):
            why.append("name suggests post-event data")
        both = pd.concat([x, y], axis=1).dropna()
        if len(both) < 20:
            continue
        xs, ys = both.iloc[:, 0], both.iloc[:, 1]
        if pd.api.types.is_numeric_dtype(xs) and pd.api.types.is_numeric_dtype(ys) and xs.nunique() > 1 and ys.nunique() > 1:
            r = xs.corr(ys, method="spearman")
            if abs(r) >= 0.9:
                why.append(f"rank correlation with target {r:+.2f}")
        # does knowing this column's value pin down the target? (purity over repeated values)
        groups = both.groupby(xs.astype(str))[both.columns[1]].nunique()
        repeated = xs.astype(str).map(xs.astype(str).value_counts()) > 1
        if repeated.mean() > 0.5 and ys.nunique() <= 20:
            pure = xs.astype(str)[repeated].map(groups).eq(1).mean()
            base = ys.value_counts(normalize=True).iloc[0]
            if pure >= 0.98 and base < 0.95:
                why.append(f"each value maps to one target value in {pure:.0%} of rows")
        if why:
            out.append((col, "; ".join(why)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--target", required=True)
    ap.add_argument("--time")
    ap.add_argument("--sep", default=",")
    a = ap.parse_args()

    df = pd.read_parquet(a.path) if a.path.endswith(".parquet") else pd.read_csv(a.path, sep=a.sep, low_memory=False)
    if a.target not in df.columns:
        sys.exit(f"target {a.target!r} not in columns: {list(df.columns)[:30]}")
    n = len(df)
    print(f"# Audit: {a.path}\n\n{n:,} rows x {df.shape[1]} columns. Duplicate rows: {df.duplicated().sum():,}")
    if n < 1000:
        print(f"Small dataset ({n} rows): treat any model as a prototype.")

    y = df[a.target]
    print(f"\n## Target `{a.target}`\nmissing {y.isna().mean():.1%}, {y.nunique()} distinct values")
    if y.nunique() <= 20:
        share = y.value_counts(normalize=True)
        print(share.round(3).to_string())
        if share.iloc[0] > 0.8:
            print(f"IMBALANCED: majority class is {share.iloc[0]:.0%}. Accuracy is meaningless here.")
    else:
        print(y.describe().round(3).to_string())

    if a.time:
        t = pd.to_datetime(df[a.time], errors="coerce")
        print(f"\n## Time `{a.time}`\n{t.min()} to {t.max()}, unparseable {t.isna().mean():.1%}")
        print("rows per year:", t.dt.year.value_counts().sort_index().to_dict())

    print("\n## Columns")
    print("| column | type | missing | distinct | note |\n|---|---|---|---|---|")
    for col in df.columns:
        x = df[col]
        nu = x.nunique(dropna=True)
        note = ["time column"] if col == a.time else []
        if nu <= 1:
            note.append("constant")
        elif nu > 0.95 * n and not pd.api.types.is_float_dtype(x) and col != a.time:
            note.append("ID-like")
        if x.isna().mean() > 0.3:
            note.append("mostly missing")
        print(f"| {col} | {x.dtype} | {x.isna().mean():.0%} | {nu:,} | {', '.join(note)} |")

    sus = leak_suspects(df, a.target)
    print("\n## Leak suspects (check each against the prediction-time contract)")
    print("\n".join(f"- `{c}`: {w}" for c, w in sus) if sus else "None flagged. That does not prove there is no leak.")
    print("\nEvery column meaning above is ASSUMED until the user or the data docs confirm it.")


if __name__ == "__main__":
    main()
