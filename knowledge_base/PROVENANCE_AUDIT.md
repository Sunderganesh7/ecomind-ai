# SCIENTIFIC PROVENANCE AND PAGE TRACKING AUDIT

**Audit Date:** 2026-09-16
**Audited By:** EcoMind AI Agent
**Scope:** Document Ingestion Pipeline (Task 06)

This is a strict audit of the Task 06 Document Ingestion Pipeline, focusing on whether scientific provenance and page-level tracking are genuinely preserved without fabrication.

---

## 1. Executive Summary

Scientific provenance is **NOT VERIFIED**.

While the pipeline correctly binds `source_id`, `url`, `topics`, and `relationships` to each chunk in a deterministic manner, the **page tracking mechanism for non-PDF sources is fundamentally flawed.** 

Specifically, the pipeline extracts `.txt` documents and assigns synthetic `page_number`s by splitting the text at double newlines (`\n\n`). This manufactures false page numbers for documents that lack physical page boundaries, directly violating the requirement: *"If a TXT source is being used, do not pretend that it has PDF-style page provenance."*

## 2. Source Format Audit

Currently, there is exactly **1 source document** physically available in the ingestion input directory:
- `fao_soil_biodiversity_2020.txt` (Format: TXT)

## 3. Page Tracking Audit

| Source | Format | Page Boundaries Available | Page Tracking Verified | Status |
| ------ | ------ | ------------------------- | ---------------------- | ------ |
| `fao_soil_biodiversity_2020` | TXT | No | No (Synthetic assignment) | **FAILED** |

### Page Boundary Defect Analysis
1. The original source is a `.txt` file which natively lacks page boundaries.
2. The `extractor.py` module contains the following logic:
   ```python
   chunks = content.split("\n\n")
   for i, chunk in enumerate(chunks, 1):
       pages.append({"page_number": i, "text": chunk.strip()})
   ```
3. **Verdict:** `page_number` is being fabricated/assigned based on paragraph breaks. This manufactures a false provenance trail that cannot be traced back to a physical page.

## 4. Chunk Provenance Audit

For the generated chunks in `knowledge_chunks.jsonl`:

| Property      | Status        | Notes |
| ------------- | ------------- | ----- |
| source_id     | **PASS**      | Correctly mapped to `sources.json`. |
| source URL    | **PASS**      | Inherited accurately from metadata. |
| title         | **PASS**      | Correctly pulled from `sources.json`. |
| year          | **PASS**      | Correctly pulled from `sources.json`. |
| topics        | **PASS**      | Array matches source topics. |
| relationships | **PASS**      | Correctly filters relationships where this source is an evidentiary basis. |
| page_number   | **FAIL**      | Synthetic/manufactured for `.txt` files. Should be `N/A` or `null`. |
| chunk_id      | **PASS**      | Deterministic SHA-256 implementation is correct. |

## 5. Sample Traceability Tests

### Chunk Trace: `fao_soil_biodiversity_2020_p001_c000_0dddbdb15f65`
- **Original Source ID:** `fao_soil_biodiversity_2020`
- **Original Location:** "Page 1" (**FAILED** - TXT file has no Page 1. This points to the first paragraph).
- **Scientific Claim:** Mentions mechanisms by which soil organisms support ecosystem services.
- **URL Provenance:** Correctly binds to `https://www.fao.org/documents/card/en/c/CB1928EN/`.
- **Verdict:** Provenance chain breaks at the "Original Location" layer due to synthetic page tracking.

## 6. Reproducibility Test

A deterministic hash collision and reproducibility check was executed via `scratch/audit_provenance.py`.

- **Deterministic ID:** PASS (Identical chunk ID generated across runs due to SHA-256 of text + metadata).
- **Collision check:** PASS
- **Algorithm correctly implemented:** PASS

Re-running the pipeline yields the exact same chunk file size, text, and IDs. 

## 7. Problems Found

1. **Fabricated Page Numbers (Critical):** TXT files are assigned `page_number: 1, 2, 3` based on double newlines instead of leaving `page_number` as `null` or `N/A`.
2. **Missing PDF Validation:** Because no PDF sources were placed in the `sources/` directory, the PDF extraction (`pypdf` logic) page boundaries could not be empirically validated in this audit.

## 8. Required Corrections

1. **Modify `extractor.py`**: Update `_extract_txt` to NOT assign `page_number`. It should return `page_number: null` (or similar) to indicate that page-level provenance is inapplicable to this format.
2. **Modify `metadata.py` & `chunker.py`**: Ensure the ID generation and chunk logic gracefully handles `page_number = None` without crashing or injecting `"None"` into the hash.

## 9. Final Status

**PROVENANCE NOT VERIFIED**

The pipeline currently introduces a break in the provenance chain by manufacturing page numbers for format types that do not possess them. This must be corrected before the chunks can be safely ingested into a vector database.
