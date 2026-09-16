# SCIENTIFIC PROVENANCE AND PAGE TRACKING AUDIT

**Audit Date:** 2026-09-16
**Audited By:** EcoMind AI Agent
**Scope:** Document Ingestion Pipeline (Task 06)

This is a strict audit of the Task 06 Document Ingestion Pipeline, focusing on whether scientific provenance and page-level tracking are genuinely preserved without fabrication.

---

## 1. Executive Summary

Scientific provenance is **VERIFIED**.

The pipeline correctly binds `source_id`, `url`, `topics`, and `relationships` to each chunk in a deterministic manner. The previous page tracking defect for non-PDF sources has been completely resolved. The ingestion system now explicitly returns `page_number: null` for `.txt` sources, refusing to manufacture physical page boundaries where none exist, and correctly incorporates the `null` value into its deterministic ID generation.

## 2. Source Format Audit

Currently, there is exactly **1 source document** physically available in the ingestion input directory:
- `fao_soil_biodiversity_2020.txt` (Format: TXT)

## 3. Page Tracking Audit

| Source | Format | Page Boundaries Available | Page Tracking Verified | Status |
| ------ | ------ | ------------------------- | ---------------------- | ------ |
| `fao_soil_biodiversity_2020` | TXT | No | Yes (`null` correctly preserved) | **PASS** |

### Page Boundary Defect Analysis
1. The original source is a `.txt` file which natively lacks page boundaries.
2. The `extractor.py` module explicitly avoids faking sequential page numbers:
   ```python
   pages.append({"page_number": None, "text": chunk.strip()})
   ```
3. **Verdict:** `page_number` remains null as expected.

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
| page_number   | **PASS**      | Correctly registered as `null` for non-paginated files. |
| chunk_id      | **PASS**      | Deterministic SHA-256 implementation is correct. (e.g. `_null_c000_...`) |

## 5. Sample Traceability Tests

### Chunk Trace: `fao_soil_biodiversity_2020_null_c000_339058b3e4b9`
- **Original Source ID:** `fao_soil_biodiversity_2020`
- **Original Location:** `null`
- **Scientific Claim:** Mentions mechanisms by which soil organisms support ecosystem services.
- **URL Provenance:** Correctly binds to `https://www.fao.org/documents/card/en/c/CB1928EN/`.
- **Verdict:** Provenance chain holds true without fabricating fake physical boundaries.

## 6. Reproducibility Test

A deterministic hash collision and reproducibility check was executed via `scratch/audit_provenance.py`.

- **Deterministic ID:** PASS (Identical chunk ID generated across runs due to SHA-256 of text + metadata).
- **Collision check:** PASS
- **Algorithm correctly implemented:** PASS

Re-running the pipeline yields the exact same chunk file size, text, and IDs. 

## 7. Problems Found

- None. The previous TXT pagination issue has been addressed.

## 8. Required Corrections

- None.

## 9. Final Status

**PROVENANCE VERIFIED**

The pipeline accurately and deterministically traces scientific knowledge back to its exact source location without manufacturing fake metadata.
