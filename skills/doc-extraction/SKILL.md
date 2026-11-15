---
name: doc-extraction
description: Build or fix a document extraction pipeline (OCR of PDFs, scans, bank statements, invoices, receipts, cheques, forms) whose numbers you can trust. Text layer first, OCR or a vision model only where needed, page-to-page context for OCR, deterministic validators that decide what is correct, one adapter per layout, and a human review step. Use when the user is extracting data from documents, choosing an OCR engine, or chasing wrong extracted values.
---

# Document extraction you can trust

The rule: **the model reads, code decides.** An OCR engine or vision model proposes values; deterministic checks decide whether they are right. OCR is never 100% accurate, whichever engine you use, free or paid, so design for review from day one.

## 0. Never assume anything

- Never assume the layout. Open 5 to 10 real samples per source before writing a parser, and list what varies: columns, date formats, multi-line descriptions, tables that break across pages, totals printed only on the last page.
- Never assume a field's meaning from its label. "Balance" can be running or available; "Amount" can be signed, or split into debit and credit columns. Confirm against the document's own totals.
- Never assume a page is digital or scanned. Check every page.

## 1. Text layer first

Many PDFs are born digital and already contain exact text. Read it before running any OCR.

- PyMuPDF: `page.get_text("words")` returns words with coordinates, so tables can be rebuilt by x position. pdfplumber is an alternative for table-heavy documents.
- A page with no text, a handful of characters, or one full-page image is scanned. Send only that page to OCR.
- Text-layer values are the source of truth for numbers. OCR fills what the text layer cannot give: handwriting, stamps, scanned cheques and receipts.

## 2. Choosing an OCR engine

- **Free, self-hosted:** PaddleOCR (from Baidu), Tesseract, docTR, Surya. Good on printed text. Most want a GPU for speed at volume, and handwriting is their weak spot.
- **Vision-language models** (Mistral's Pixtral, Qwen-VL and the large hosted multimodal models) read handwriting and messy layouts better, and they take instructions and context.
- **Hosted OCR APIs** (Mistral OCR, Google Document AI, AWS Textract, Azure Document Intelligence) are the fastest way to start.
- **Sensitive data:** read the provider's data-retention and training terms for your plan before sending a single page. When data safety matters, Mistral is a strong default. Never log full account numbers, IDs or card numbers.
- Benchmark on your own 20 hardest pages, not on the vendor's demo.

## 3. Give the OCR context, page by page

OCR gets better when the model knows what it is looking at. For a multi-page document read with a vision model:

- **Page 1:** send the page with a short brief: the document type, the fields expected, and the exact output schema.
- **Page N:** also send the context carried from page N-1: the table's column headers, the last few rows read, the running balance, and any section or table that continues. This fixes rows split across pages, headers that only appear on page 1, and running totals.
- Keep the carried context small and structured (headers, last 3 rows, carried totals), not the whole previous output.
- Engines that take no prompt cannot use this. Apply the same context in your parsing step instead.

## 4. Focus every call

- Render scans at 300 DPI. Deskew, then crop to the region that matters (a cheque's payee line, a signature box, the totals block). A focused crop beats a full page.
- Ask for one field set per call against a fixed JSON schema, and validate the JSON.
- Cache results by file hash, page and prompt version, so re-runs and tests cost nothing.

## 5. Validators decide what is done

Write checks that need no model, and run them on every document:

- **Totals reconcile:** opening balance plus credits minus debits equals the closing balance; line items sum to the invoice total; tax equals rate times base, within rounding.
- **Running balance:** recompute it row by row. The last row must equal the printed closing balance to the cent. If it does not, the document is not done.
- **Checksums and formats:** routing and MICR checksums, IBAN mod-97, card numbers (Luhn), India's IFSC, PAN and GSTIN formats, and dates inside the statement period.
- **Cross-field:** amount in words equals amount in figures; a cheque has a payee; the currency is consistent.
- A value that fails a check goes to review with the reason attached. The model never silently "fixes" a number.

## 6. One adapter per source

Each bank, vendor or form type gets its own small adapter (layout rules, column map, date format, known quirks) behind one shared interface, discovered automatically. Adding a source means one new file plus its golden test, never another branch in a giant if-chain.

## 7. Human review is part of the product

- Show each extracted value next to the image crop it came from, with its validator result and confidence.
- Failed or low-confidence fields are highlighted, the reviewer edits in place, and every edit is logged.
- Cursive handwriting on poor scans will always need a person. Tell the user that up front instead of promising full automation.

## 8. Test before shipping

- **Golden tests:** for each adapter, a sample document and its expected output, or at least its closing balance. The gate is a reconciliation difference of exactly 0.00.
- Stub the OCR and vision calls in tests, so they run offline and cost nothing.
- Real documents carry personal data. Never commit them; use synthetic or redacted samples in any repo.

## Report

For each document: which pages came from the text layer and which from OCR, the validators that passed and failed, the fields sent to review, and the reconciliation difference.
