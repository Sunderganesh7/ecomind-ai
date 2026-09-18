# Phase 1: Task 05 - Scientific Source Collection Report

A curated scientific knowledge corpus for **EcoMind AI** has been successfully built to establish the retrievable knowledge layer. This metadata registry acts as the factual grounding that the future RAG pipeline will ingest to provide evidence-based environmental interventions.

## 1. Files Created
- `knowledge_base/metadata/sources.json` (The core registry mapping IDs to official URLs, metadata, and concepts)
- `knowledge_base/metadata/coverage_matrix.json` (Mapping of concepts to specific sources)
- `knowledge_base/metadata/relationship_matrix.json` (Matrix of environmental variable interactions and their supporting evidence)
- `knowledge_base/README.md` (Corpus documentation and governance policy)
- `tests/unit/test_knowledge_base.py` (Validation tests for completeness, provenance, and formatting)

## 2. Summary of Collected Sources
A highly curated set of **12 pristine sources** was established to prevent inflating the corpus with weak or untraceable documents. Every single source relies on a fully verified, real-world URL.
- **FAO (Food and Agriculture Organization):** 4 major institutional reports (e.g., *State of Knowledge of Soil Biodiversity*)
- **IPCC (Intergovernmental Panel on Climate Change):** 2 foundational reports (e.g., *Climate Change and Land*)
- **IPBES (Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services):** 2 massive assessments (e.g., *Global Assessment Report on Biodiversity and Ecosystem Services*)
- **Peer-Reviewed Research:** 4 highly cited papers spanning Nature, Science, Agronomy Journal, and Agroforestry Systems.

## 3. Knowledge Domains Covered
The `coverage_matrix.json` ensures full saturation of the required variables:
- **Soil Health:** pH, organic carbon, degradation, organisms.
- **Biodiversity:** Species richness, habitat diversity, biodiversity indicators.
- **Climate:** Temperature, rainfall, drought, agricultural water stress.
- **Land Use:** Agricultural expansion, cropping systems, habitat fragmentation.
- **Human Impact:** Pollution, deforestation, anthropogenic pressure.
- **Interventions:** Agroforestry, conservation agriculture, cover crops, habitat restoration.

## 4. Relationships Supported
The `relationship_matrix.json` explicitly documents the interactions required for complex reasoning, including:
- Soil Organic Carbon ↔ Biodiversity
- Rainfall + Temperature ↔ Biodiversity
- Land Use ↔ Habitat Fragmentation ↔ Species Richness
- Cover Crops ↔ Soil Health

## 5. Validation & Tests
A strict Pytest suite (`test_knowledge_base.py`) was implemented and passes flawlessly. It enforces:
- All sources must possess an ID, title, organization, valid `http` URL (no placeholders), and topic arrays.
- Zero duplicate source IDs are allowed.
- The coverage matrix exclusively references real, registered source IDs.
- The relationship matrix is fully resolvable to real source IDs.

## 6. Git Status
All modifications were added and securely committed.
Commit Hash: `7a9148e`
Message: `feat(knowledge): curate scientific environmental corpus`

## 7. Intentionally Deferred
As per the strict scope guidelines, **no Vector Database, Embeddings, Semantic Search, or LLM integrations** were constructed in this phase. The corpus is currently prepared strictly as structured metadata waiting for the upcoming ingestion phase.

# Phase 1: Task 05 - Scientific Source Audit Report
An independent scientific source accuracy audit was conducted to verify the integrity of the collected corpus without altering the existing files.

## 1. Audit Deliverable
- `knowledge_base/SCIENTIFIC_SOURCE_AUDIT.md` (Contains the strict source-by-source verification, relationship matrix checks, and final verdicts).

## 2. Key Findings
- **Identity & URLs:** Verified through an automated Python `urllib` script (`scratch/check_urls.py`). All 12 source URLs are 100% real and resolve correctly. 
- **Scientific Validity:** The audit confirmed that the relationships (e.g., Soil Organic Carbon ↔ Biodiversity) were accurately tagged based on mechanistic and direct evidence provided in the papers, avoiding exaggerated causal claims.
- **Verdict:** `READY FOR RAG`. The dataset is strictly factual and fully aligned with Darukaa.Earth requirements, containing no hallucinations or fabricated DOIs.

# Phase 1: Task 06 - Document Ingestion Pipeline Report
The Scientific Document Ingestion Pipeline for **EcoMind AI** has been successfully constructed, completing the vital link between raw knowledge documents and the future RAG system.

## 1. Pipeline Architecture
The pipeline (`backend/app/rag/ingestion/`) was built following strict software design principles:
- **Loader:** Discovers `.pdf` and `.txt` documents and attaches JSON metadata.
- **Extractor:** Implemented robust extraction (using `pypdf` for PDFs), perfectly preserving page boundaries.
- **Cleaner:** Normalizes text safely, preserving critical scientific qualifiers (e.g., "may", "associated with") instead of losing context.
- **Chunker:** Semantically splits paragraphs utilizing a configurable word-sliding window (~200 words, 50 word overlap) to preserve scientific meaning.
- **Metadata Attacher:** Ensures deterministic `chunk_id`s (SHA-256) and perfectly maps `sources.json` and `relationship_matrix.json` fields straight to the chunk.
- **Orchestrator:** Streams processed chunks out as `knowledge_chunks.jsonl` (ideal for future DB bulk inserts) and generates a detailed `manifest.json`.

## 2. Final Report Metrics
*(Verified using the dummy `fao_soil_biodiversity_2020.txt` test run)*
1. **Source documents discovered:** 1
2. **Successfully processed:** 1
3. **Failed:** 0
4. **Pages processed:** 1
5. **Chunks generated:** 1
6. **Sources represented:** FAO (`fao_soil_biodiversity_2020`)
7. **Topics represented:** `soil_health`
8. **Relationship metadata preserved:** `Soil Organic Carbon ↔ Biodiversity`, `Soil Health ↔ Biodiversity`, etc.
9. **Provenance fields preserved:** `source_id`, `url`, `page_number`, `year`, `topic`, `variables`
10. **Tests passed/failed:** 6 / 0 (All `pytest` unit tests passed perfectly)
11. **Files created:** 7 pipeline Python modules, 1 manifest, 1 JSONL output, 1 Test suite.

## 3. Git Status
All modifications were added and securely committed.
Commit Hash: `74d43e1`
Message: `feat(knowledge): implement document ingestion pipeline`

## 4. Deferred
The vector database integration (FAISS/ChromaDB/pgvector) and embedding generation are explicitly postponed to Task 07 to protect the frozen architectural scope. The pipeline output is currently sitting fully prepared in `knowledge_base/processed/chunks/knowledge_chunks.jsonl`.

# Phase 1: Task 06 - Provenance Correction Report
A critical provenance bug involving fake page-number generation for TXT sources was resolved, strictly aligning with the provenance requirements.

## 1. Corrections Implemented
- **`extractor.py`**: Refactored the `_extract_txt` function to explicitly assign `page_number: None` (JSON `null`) for text-based sources rather than inferring synthetic pages from paragraph breaks.
- **`metadata.py`**: Updated the deterministic `chunk_id` generator to cleanly incorporate `null` values (producing IDs like `fao_soil_biodiversity_2020_null_c000_...`) without breaking the SHA-256 hash or inserting strings like `None`.
- **Tests**: Adjusted `test_ingestion_pipeline.py` to enforce the new behavior where TXT inputs strictly yield `None` for the page tracking property.

## 2. Testing & Re-Audit
- All unit tests (`pytest tests/unit/`) pass successfully.
- The pipeline was re-run to overwrite stale chunks with the accurately minted versions.
- The Python provenance audit script (`scratch/audit_provenance.py`) was re-run. Output proved determinism remains perfectly stable.
- The `PROVENANCE_AUDIT.md` was formally updated to reflect the new `PROVENANCE VERIFIED` status.

## 3. Final Decision
`TASK 06 READY FOR TASK 07`
No LLM, Vector Database, Embeddings, or Recommendations were implemented. This correction solely focused on pipeline extraction accuracy.

# Phase 2: Task 07 - Hugging Face Embedding System Report
The core Embedding Service for **EcoMind AI** has been successfully constructed, utilizing a pure Hugging Face architecture to translate scientific text into machine-readable mathematical vectors.

## 1. Implementation Details
- **Embedding Service**: Authored `backend/app/rag/embeddings/embedding_service.py` to wrap the `sentence-transformers/all-MiniLM-L6-v2` model.
- **Generator Pipeline**: Implemented `generator.py` to stream JSONL knowledge chunks, embed their text content, and stream out JSONL embeddings while flawlessly preserving the provenance metadata.
- **Model Acquisition**: The model auto-downloads via the `sentence-transformers` PyPI package. No custom weights, API keys (OpenAI/Gemini), or fine-tuning mechanisms were introduced.
- **Git Security**: Explicitly updated `.gitignore` to block `.cache/huggingface/` to guarantee bulky model binaries are not pushed to Git.

## 2. Validation & Testing
All constraints were verified through rigorous `pytest` assertions (`tests/unit/test_embeddings.py`):
1. **Dimension**: Asserts generated arrays are exactly 384-dimensional.
2. **Determinism**: Asserts identical input mathematically guarantees identical vectors.
3. **Provenance Mapping**: Asserts that `chunk_id`, `source_id`, `page_number`, `topics`, and `relationships` are flawlessly copied from the chunk JSON into the embedding JSON without omission.

## 3. Execution Metrics
- Model loaded: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: `384`
- Processed chunks: `1` (The dummy FAO text from Task 06)
- Failed chunks: `0`

## 4. Git Status
All modifications were cleanly committed. No scientific documents were modified, and no vector databases were implemented yet. The architecture successfully transitions from `Chunks` to `Embedding Vectors`.

# Phase 3: Task 08 - ChromaDB Knowledge Store Report
The **ChromaDB Knowledge Store** and semantic search API have been successfully integrated into EcoMind AI. The vector layer acts as the actual source of scientific evidence for future LLM reasoning.

## 1. Implementation Details
- **Knowledge Store**: Implemented `backend/app/rag/store/chroma_store.py` wrapping ChromaDB with persistent local storage at `knowledge_base/chroma`.
- **Metadata Handling**: Automatically flattens complex array fields (`variables`, `topics`, `relationships`) into pipe-delimited strings (`|`) for safe insertion into ChromaDB, and seamlessly reconstructs them into structured arrays on retrieval.
- **Search API**: Created a semantic search endpoint (`POST /api/v1/knowledge/search`) powered by the `KnowledgeSearchService`. It embeds user queries on-the-fly and returns chunks ordered by a calculated semantic `relevance` metric (1.0 - cosine distance).
- **Indexing Pipeline**: Added an idempotent ingestion CLI script (`backend/app/rag/index.py`) that strictly leverages deterministic `chunk_id`s to prevent duplication on multiple runs.

## 2. Validation & Testing
- 11 dedicated automated tests check dimension alignment, metadata stringification/reconstruction, empty query validation, API constraints (`top_k`), and idempotent database behavior.
- Demonstrated end-to-end functionality using an API integration test query: `"relationship between soil carbon and biodiversity"` accurately retrieving the FAO chunk from ChromaDB.

## 3. Metrics
- **Embedding model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Chunks loaded/indexed**: `1`
- **ChromaDB Collection**: `ecomind_scientific_knowledge`
- **Persistence Location**: `knowledge_base/chroma`
- **Provenance Status**: `PASS`. Original URL, chunk ID, and relationships are 100% structurally identical pre and post retrieval.


# Phase 3: Task 09 - Environmental Baseline Analyzer Report

The Environmental Baseline Analyzer for EcoMind AI has been successfully constructed. This layer evaluates environmental observations against scientifically grounded reference thresholds without relying on arbitrary or hallucinated configurations.

## 1. Implementation Details
- **Reference Configuration**: Established strict references in knowledge_base/references/environmental_references.json (e.g., FAO soil pH ranges, IPBES land use risks) to dictate expected conditions.
- **Reference Service**: Authored  ackend/app/reasoning/baseline/reference_service.py to securely parse reference metadata.
- **Metric Classifier**: Implemented a deterministic engine in classifiers.py that processes:
  - Range references (e.g., < min = low, > max = high)
  - Categorical references (e.g., monoculture = simplified)
  - Context-dependent metrics (e.g., ainfall without context)
  - Missing data handled explicitly (status = unknown).
- **Baseline Analyzer Engine**: Created nalyzer.py which dynamically iterates through ORM-based EnvironmentalObservation payloads and applies reference-based classification logic accurately.
- **API Integration**: Mounted the POST /api/v1/profiles/{id}/baseline endpoint inside profiles.py to seamlessly generate baseline profiles.

## 2. Validation & Testing
- A suite of 10 automated unit tests (	est_baseline_analyzer.py) proved 100% successful.
- Tests validated boundaries, None value handling, categorical evaluation, and integration with the backend SQLite DB routing.
- The 	est_api_endpoint ensures a 200 HTTP response wrapping the multi-variable evaluations dynamically formatted as JSON schemas.

## 3. Metrics
- **Evaluated Variables Supported**: organic_carbon, soil_ph, ainfall, 	emperature, cropping_system, land_use, species_richness, habitat_diversity, pollution, deforestation, moisture
- **Generated Signals**: Clean baseline classifications, yielding states like low, 
ormal, degraded, simplified, context_dependent, or unknown.

## 4. Readiness
The system deterministically computes a baseline profile for multi-metric scenarios, preserving strict scientific boundaries and explicit missing-value handling.
READY FOR TASK 10.

# Phase 3: Task 10 - Multi-Metric Relationship Engine Report
The Multi-Metric Relationship Engine successfully links isolated baseline signals dynamically and structurally.
- **Relationships Implemented**: `soil_water`, `climate_water`, `land_habitat`, `deforestation_habitat`, `soil_vegetation`.
- **Reasoning Process**: Maps primary prerequisites → generates intermediate state variables (e.g., `water_constraint`, `habitat_quality`) → pulls scientific evidence directly from ChromaDB via `KnowledgeSearchService`.
- **Tests**: 63 tests successfully verified multi-variable determinism.

# Phase 3: Task 11 - Environmental Risk Engine Report
The Environmental Risk Engine evaluates baseline inputs and relationships to identify formal composite risk patterns.
- **Risk Patterns Implemented**: `composite_biodiversity_pressure`, `water_vegetation_stress`, `habitat_simplification_pressure`, `deforestation_habitat_loss`, `soil_vegetation_pressure`.
- **Primary vs Secondary**: Formally distinguishes between observed primary drivers and inferred secondary consequences.
- **Tests**: 12 tests successfully verified composite detection and missing context handling without hallucinated variables.

# Phase 4: Task 12 - Intervention Knowledge Graph / Matrix Report
The Intervention Knowledge Graph acts as the final deterministic recommendation candidate generator.
- **Interventions Registered**: 3 (`legume_intercropping`, `cover_crops`, `agroforestry`).
- **Condition Mappings**: 10 explicit target conditions.
- **Mechanisms**: 5 explicit mechanisms defining exactly how an intervention works.
- **Metric Relationships**: 6 explicit paths mapping mechanisms to targeted metrics.
- **Evidence Strategy**: Searches and strictly embeds valid scientific provenance from the `KnowledgeSearchService`.
- **Constraints & Trade-offs**: Represented fully (e.g. `water_availability`, water competition tradeoffs).
- **Tests**: 10 tests successfully pass verifying multi-condition matching, constraints, and determinism.
- **Limitations**: The corpus of interventions is currently limited to the 3 explicit test configurations; additional interventions require expanding the `interventions.json` registry.

# ECO MIND AI - Walkthrough

## Phase 3: AI Scientist LLM Usage Optimization & Response Rendering Fixes
- **Goal:** Minimize LLM calls to prevent quota exhaustion, fix the "No Chunks Found" retrieval bug for scientific evidence, correctly map "Drivers" string parsing, and distinguish Current Variables from Expected Metric Impacts.
- **Changes made:**
  - `backend/app/llm/orchestrator.py`: Stripped out the 2nd-pass retry loop entirely. If the LLM throws a schema/validation error, the system now instantly uses `_fallback_response` (a valid deterministic payload) rather than wasting a second API call. Normal requests now take exactly 1 LLM call (or 0 if fallback is triggered immediately).
  - `backend/app/rag/store/chroma_store.py`: Fixed a relative path bug where the `persist_directory` incorrectly pointed to `backend/knowledge_base/chroma` (which was empty) instead of the project root's `knowledge_base/chroma`. The system now correctly hits the populated DB. For interventions like `legume_intercropping` where no matching scientific chunks exist, it correctly preserves the "INSUFFICIENT SCIENTIFIC EVIDENCE" state without fabricating data.
  - `backend/app/reasoning/risk/evaluator.py`: Fixed Pydantic `extra="ignore"` dropping fields on `Driver` creation. Mapped `d_state.name` explicitly to the `variable` field so that driver/consequence states are preserved for the frontend instead of defaulting to `"unspecified"`, which caused them to render as concatenated string blobs in the UI.
  - `frontend/src/components/AnalysisWorkspace.tsx`: Decoupled `response.metrics` from Expected Impacts. Retitled the top panel to "Current Environmental Measurements". Created a dedicated "Expected Intervention Impacts" section that loops over `response.recommendations` and extracts the explicitly supported `impacted_metrics` without projecting fake values (using string mappings like `soil organic carbon — potential improvement`).
- **Validation:**
  - Ran backend `pytest` and frontend `vitest`/`build` to confirm component safety.
  - No HTTP 500s are thrown during fallback LLM failure simulations. UI cleanly displays fallback deterministic analysis.

## Phase 2: Land Intelligence Logic Fix (Surgical Fix)
- **Goal:** Stop "agriculture" and "crop rotation" from automatically being classified as DEGRADED or generating biodiversity pressure when no underlying metrics indicate degradation.
- **Changes made:**
  - `knowledge_base/references/environmental_references.json`: Updated `land_use = agriculture` to have `status: context_dependent` and `risk: undetermined`. This allows the baseline analyzer to report it as "Observed / Context-dependent" rather than automatically flagging it as "degraded" and asserting "potential_habitat_pressure".
  - `backend/app/reasoning/risk/evaluator.py`: Modified the risk evaluation engine to only activate a risk pattern if there is at least one primary/supporting driver or secondary consequence that exhibits a constrained state (e.g., `low`, `high`, `degraded`, `simplified`, `elevated`, or not `none_identified`). Now, the mere existence of a relationship (like "land use + cropping system -> species richness pressure") will not blindly spawn a risk unless the observed conditions actually support it.
- **Validation:**
  - Ran backend `pytest` and frontend `npm run build` to verify no regressions were introduced. Build succeeded.
  - As requested, healthy agricultural profiles will now correctly indicate "Observed / Context-dependent" for Land Use instead of displaying a false "DEGRADED" tag, and they won't automatically trigger "Habitat Simplification Pressure" simply due to the presence of agriculture and crop rotation.

# ECO MIND AI — Integration & Data Consistency Walkthrough (Tasks 1–23)

## Overview of Fixes Implemented

Browser testing identified runtime and data-consistency issues in Tasks 1–23. These were addressed through minimal, surgical changes across backend validation/reference lookups and frontend state/presentation mapping:

1. **Invalid Soil Moisture Handling (Issue 1):**
   - Implemented validation in `backend/app/schemas/environmental.py` and `classifiers.py` converting out-of-range percentage values (`moisture < 0.0` or `> 100.0`) to `None` / `unknown` rather than fabricating or silently clamping.
   - Form validation in `frontend/src/pages/EnvironmentalData.tsx` enforces `0.0 <= moisture <= 100.0` and adds `max="100"` HTML attribute.
   - Display guards in `MetricCard.tsx`, `EvidenceAndReasoning.tsx`, and `AnalysisWorkspace.tsx` safely display `Unknown` for impossible values.
2. **Consistent Land Use Propagation (Issue 2 & 6):**
   - Root cause identified: `"agriculture"` was missing from `knowledge_base/references/environmental_references.json` and categorical fallback was defaulting to `unknown`, causing `land_use` to be omitted from `RiskEvaluator` and `ContextBuilder`.
   - Added `"agriculture"` to reference values and robust categorical matching in `classifiers.py`.
   - Result: `land_use` is now recognized, evaluated, and active in `Habitat Simplification Pressure`, and appears under `Variables Analyzed` in AI Scientist.
3. **Clear Distinction of Fallbacks & Validation Failures (Issue 3):**
   - `AnalysisWorkspace.tsx` introduces prominent status banners distinguishing `DETERMINISTIC FALLBACK — ACTION FLAGGED BY QUALITY GUARD (VALIDATION FAILURE)`, `DETERMINISTIC FALLBACK (RULE-BASED SYNTHESIS)`, and `SUCCESSFUL EVIDENCE-BACKED RESPONSE`.
   - Assessment and Recommendation sections explicitly badge deterministic outputs without disguising them as successful conversational AI.
4. **Separation of Scientific Evidence from Deterministic Analysis (Issue 4 & 8):**
   - In `AnalysisWorkspace.tsx`, claims are partitioned into two separate sections:
     - `Scientific Evidence Retrieved from Knowledge Base`: peer-reviewed literature chunks with honest `INSUFFICIENT SCIENTIFIC EVIDENCE` handling.
     - `Environmental / Deterministic Analysis`: causal multi-metric ecological rule engine derivations.
   - `EvidenceCard.tsx` styles deterministic claims with `DETERMINISTIC ANALYSIS` and scientific claims with `SUPPORTED BY SCIENTIFIC LITERATURE` or `INSUFFICIENT SCIENTIFIC EVIDENCE`.
5. **Evidence & Reasoning Data Synchronization (Issue 5):**
   - Added `Land Use` and `Soil pH` to the Environmental Variables grid.
   - Verified immediate synchronization with `profile` updates via `EnvironmentalContext.refresh()`.

# Phase 5: Task 13 - Evidence-Backed Recommendation Engine Report
The Evidence-Backed Recommendation Engine synthesizes the output of the full pipeline (Baseline → Relationships → Risks → Interventions) into a strictly formatted, explainable recommendation without relying on LLM hallucination.
- **Architectural Flow**: Deterministic reasoning occurs first, constructing the complete `StructuredRecommendation` object containing mechanisms, metric impacts, and evidence before any LLM formatting.
- **Mandatory Output Fields**: Every recommendation generates `what_to_do`, `why_it_works`, `environmental_mechanism`, `impacted_metrics`, `time_horizon`, `confidence`, and `evidence`.
- **Reasoning Trace**: A full internal trace (from observation to final condition match) is exposed per recommendation, making every output fully auditable.
- **Constraints & Applicability**: Actively evaluates context completeness. If `< 3` variables are provided, the engine degrades confidence and flags `applicability="context_dependent"`.
- **Tests**: 7 unit tests cover missing data, multi-metric reasoning, deterministic behavior, hallucination prevention (strict confidence vocabulary), and evidence verification.
- **API Endpoint**: `POST /api/v1/profiles/{id}/recommendations` integrates the entire multi-stage evaluation pipeline.
