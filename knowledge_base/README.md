# EcoMind AI Scientific Knowledge Corpus

## 1. Purpose of the Knowledge Base
This corpus serves as the authoritative scientific grounding for EcoMind AI. Rather than relying on untraceable LLM hallucinations, future AI reasoning pipelines (RAG) will retrieve mechanisms, effects, and ecological relationships directly from these documented sources to generate evidence-based environmental interventions.

## 2. Source Selection Criteria
Every source in this repository has been strictly curated to guarantee:
- **High Credibility:** Only authoritative institutional reports or highly-cited peer-reviewed research.
- **Direct Relevance:** Content explicitly addresses soil health, climate, land use, biodiversity, and human impact.
- **Traceability:** URLs and metadata accurately map back to the original publication without fabrication.

## 3. Source Hierarchy
1. **Tier 1 (Authoritative Institutions):** FAO (Food and Agriculture Organization), IPCC (Intergovernmental Panel on Climate Change), IPBES (Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services).
2. **Tier 2 (Peer-Reviewed Research):** Nature, Science, and specialized agronomic/ecological journals (e.g., Agronomy Journal, Agroforestry Systems).

## 4. Covered Environmental Variables
- **Soil:** Soil pH, organic carbon, moisture, structure, degradation.
- **Climate:** Temperature, rainfall, drought, water availability.
- **Land:** Land use, agricultural expansion, cropping systems.
- **Biodiversity:** Species richness, habitat diversity, fragmentation.
- **Human Impact:** Pollution, deforestation, anthropogenic pressure.

## 5. Covered Relationships
The corpus provides traceable evidence for critical multi-variable ecological relationships, including but not limited to:
- Soil Health ↔ Biodiversity
- Rainfall + Temperature ↔ Biodiversity (Climate pressure)
- Land Use ↔ Habitat Fragmentation ↔ Species Richness
- Deforestation / Pollution ↔ Biodiversity

*(See `metadata/relationship_matrix.json` for the exact mapping)*

## 6. Intervention Coverage
The curated knowledge includes evidence regarding specific actionable interventions:
- Agroforestry
- Conservation agriculture
- Cover crops & Crop rotation
- Habitat restoration & ecological connectivity
- Organic amendments

## 7. Provenance Policy
Zero tolerance for synthetic data or fabricated sources. All metadata fields (`source_id`, `url`, `title`, `publication_year`) represent real-world publications. When new sources are added, their exact origin must be fully documented.

## 8. Uncertainty Policy
Scientific findings must be represented with appropriate qualifiers. Relationships in the matrix are summarized as supported evidence, but future reasoning layers must read the underlying text to determine if an intervention "may" work or "will" work based on contextual constraints.

## 9. Consumption by Future RAG Pipeline
In upcoming phases, this metadata registry will guide a document ingestion pipeline. The vector database will index the underlying text of these sources. The LLM reasoning agent will query the vector database, utilizing the provided source IDs to cite its recommendations and prove scientific grounding.

## 10. Document Ingestion Pipeline (Phase 1, Task 06)
The backend now features a robust ingestion pipeline (`backend/app/rag/ingestion/`) designed to cleanly extract, chunk, and index this scientific corpus while mathematically guaranteeing provenance.

### Ingestion Architecture
- **Loader:** Scans `knowledge_base/sources/` and cross-references files with `sources.json`.
- **Extractor:** Uses `pypdf` to parse PDFs, strictly preserving page boundaries and structures. Supports TXT and PDF.
- **Cleaner:** Normalizes whitespace and artifacts without removing critical scientific qualifiers (e.g., "may", "associated with").
- **Chunker:** Uses semantic paragraph/word-window boundaries. Configurable chunk size (~200 words) and overlap (~50 words).
- **Metadata:** Attaches deterministic SHA-256 chunk IDs, source mappings, environmental variables, and verified relationships.
- **Output:** Writes to `knowledge_base/processed/chunks/knowledge_chunks.jsonl` (JSON Lines format for seamless streaming to a future Vector DB).

### CLI Usage
```bash
$env:PYTHONPATH="backend"
python -m backend.app.rag.ingestion.pipeline --input knowledge_base/sources --metadata knowledge_base/metadata --output knowledge_base/processed/chunks
```

### Validation
The pipeline handles failures safely. Duplicate document ingestion is prevented natively via SHA-256 chunk deterministic hashing, ensuring idempotency.

