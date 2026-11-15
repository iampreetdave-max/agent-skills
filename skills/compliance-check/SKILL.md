---
name: compliance-check
description: Catch compliance gaps before a vibe-coded product ships. Reads the codebase to learn what the product does, what personal data it touches and which third parties see it, asks only the questions code cannot answer (where users are, minors, payments, health or financial data, AI decisions about people), maps that to the laws and standards that likely apply (India's DPDP Act, GDPR, the EU AI Act, CCPA, COPPA, HIPAA, PCI DSS, accessibility, email and SMS consent), finds the concrete gaps with file:line evidence, and pushes a prioritised fix list. Use when the user is building or launching a product, says "is this compliant", "what laws apply", "privacy policy", "GDPR", "DPDP", "HIPAA", "can I launch this", or adds payments, accounts, analytics, AI features or user data. Not legal advice.
---

# Compliance check

Vibe-coded products ship fast and skip compliance until a regulator, a payment provider, an app store or an enterprise customer's security review stops them. This skill finds the gaps early, while they are cheap to fix.

**Not legal advice.** It spots what likely applies and what is missing. For anything high-risk (health data, children, money, AI deciding about people), tell the user to confirm with a lawyer.

## 0. Never assume anything

Not the users' countries, not their ages, not what a database column holds, not that a vendor is compliant. Everything is VERIFIED (seen in the code or confirmed by the user) or ASSUMED, and every ASSUMED item becomes a question.

## 1. Read the code first

Build a product profile before asking anything:

- **What it does and for whom:** README, routes and pages, onboarding flows, pricing pages.
- **Personal data:** database schemas, models, migrations and forms. Flag names, emails, phones, addresses, dates of birth, location, government IDs (Aadhaar, PAN, SSN, passport), health, financial and card data, biometrics (face, voice, fingerprint), children's data, and anything the user uploads.
- **Third parties that see data:** dependencies and API calls (analytics, error tracking, email and SMS, payments, auth, LLM APIs, CRMs), third-party scripts in pages, cookies and browser storage.
- **Where data lives:** hosting region, database region, backups, and logs (PII or secrets in logs is a common gap).
- **User rights in code:** can users export their data and delete their account? Is there consent capture, unsubscribe, or an age gate?
- **AI features:** what user data goes to which model provider, whether users are told they are talking to AI, and whether AI output decides anything about a person (hiring, credit, insurance, housing, education, health).
- **Basics:** a privacy policy and terms that match what the code actually does, secrets out of the repo, auth hardening, rate limits.

## 2. Ask only what the code cannot answer

Seven questions at most, in one message. Skip any the code already answered.

1. Where are the users: India, the EU or UK, the US (which states), elsewhere?
2. Can anyone under 18 use it? Under 13?
3. Consumers, businesses, or both? Will you sell to enterprises (they will ask for SOC 2 or ISO 27001)?
4. Does it take payments, and who processes them?
5. Does it handle health, financial, biometric or government-ID data, or precise location?
6. Does AI make or shape decisions about people?
7. Do you send marketing email, SMS or WhatsApp messages?

## 3. Map to what likely applies

Show a table: regime, trigger, **Applies / Likely / Check / No**, and why.

| Area | Regimes to weigh |
|---|---|
| Personal data, India | Digital Personal Data Protection Act 2023 and its Rules: notice and consent, purpose limits, data principal rights, breach reporting, verifiable parental consent for under-18s, penalties up to ₹250 crore. CERT-In directions: report cyber incidents within 6 hours and keep logs. |
| Personal data, EU and UK | GDPR / UK GDPR: lawful basis, notice, data subject rights, DPAs with processors, cross-border transfers, breach notice within 72 hours, fines up to €20M or 4% of global turnover. ePrivacy / PECR: consent before non-essential cookies and tracking. |
| Personal data, US | CCPA/CPRA and other state privacy laws (notice, opt-out of sale or sharing, deletion). COPPA for under-13s. Illinois BIPA for biometrics. GLBA for financial institutions, FERPA for student records. |
| Health | HIPAA if handling PHI for US covered entities or business associates: BAAs with every vendor that touches PHI, including the LLM provider. In India, DPDP plus telemedicine and health-data guidance. |
| Payments | PCI DSS: never store or log card numbers; use hosted checkout or tokenisation. RBI rules in India (payment data stored in India, KYC, digital lending guidelines for credit products). |
| AI | EU AI Act (risk tiers, prohibited uses, transparency when people talk to AI or see synthetic content). NYC Local Law 144 for AI in hiring. Colorado AI Act for consequential decisions. FTC rules on deceptive AI claims. Model providers' usage policies. |
| Messaging | CAN-SPAM, TCPA (consent for US SMS and calls), India TRAI DLT registration for commercial SMS, WhatsApp Business policy, GDPR and PECR consent for marketing. |
| Accessibility | WCAG 2.1 / 2.2 AA as the practical bar. ADA (US), the European Accessibility Act (EU), India's Rights of Persons with Disabilities Act for many services. |
| Platforms | App Store and Play rules: privacy labels and data-safety forms, in-app account deletion. EU Digital Services Act and UK Online Safety Act for user-generated content. |
| Restricted domains | Real-money gaming and betting (heavily restricted or banned in many places, India included), lending, insurance, crypto, healthcare advice, and legal advice each have their own regulators. Flag them and recommend a lawyer. |
| Selling to businesses | SOC 2 or ISO 27001, a DPA template, a security page, vendor lists, and incident response. Enterprises ask before they buy. |
| Open source | Licences of dependencies and copied code (GPL and AGPL obligations), and attribution. |

Verify anything time-sensitive (effective dates, thresholds, new rules) against the official source before stating it as fact. Laws change.

## 4. Find the concrete gaps

For each gap: what is wrong, the evidence at `file:line`, which regime it breaks, and the fix. Common ones:

- Analytics or ad scripts loading before consent.
- Card numbers or full IDs stored, or written to logs.
- No account deletion or data export.
- A privacy policy that is missing, or that doesn't match what the code collects and shares.
- Personal data sent to an LLM or other third party with no notice, and no DPA or BAA in place.
- No age gate on a product children may use.
- Marketing messages with no consent record or unsubscribe link.
- Secrets in the repo. Passwords stored without hashing. No rate limit on auth.
- Data stored in a region the law or the customer doesn't allow.

## 5. Prioritise and nudge

Sort fixes into **Before launch**, **Before scaling or selling to businesses**, and **Later**. Be direct about why each matters, using the concrete consequence: fines, payment-provider termination, app-store rejection, a lost enterprise deal. Offer to implement the code fixes now. Policies and agreements are drafts for the user, or their lawyer, to finalise.

## 6. Record it

Write or update `COMPLIANCE.md` in the repo:

- the product profile (VERIFIED and ASSUMED)
- the answers to the questions
- the applicability table
- the gaps and their status
- the date

Re-run this check when the product adds payments, accounts, AI features, a new country or a new data type.
