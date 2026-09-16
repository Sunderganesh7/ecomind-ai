# EcoMind AI Backend

This is the FastAPI backend service for the EcoMind Environmental Intelligence System.

## API Purpose
The **Environmental Profile API** establishes a structured-input layer for receiving, storing, and retrieving environmental observations. This data forms the foundational inputs for future data processing, risk detection, and scientific reasoning pipelines.

## Endpoints
- `POST /api/v1/profiles` - Create a new environmental profile.
- `GET /api/v1/profiles/{id}` - Retrieve an environmental profile by ID.
- `PUT /api/v1/profiles/{id}` - Update an existing environmental profile by ID.

## Sample Request (`POST /api/v1/profiles`)
```json
{
  "soil": {
    "ph": 6.2,
    "organic_carbon": 0.3,
    "moisture": 18
  },
  "climate": {
    "temperature": 29,
    "rainfall": 500
  },
  "land": {
    "use": "agriculture",
    "crop": "wheat",
    "cropping_system": "monoculture"
  },
  "biodiversity": {
    "species_richness": 12,
    "habitat_diversity": "low"
  },
  "human_impact": {
    "pollution": "moderate",
    "deforestation": "low"
  }
}
```

## Sample Response (`201 Created` or `200 OK`)
```json
{
  "id": 1,
  "created_at": "2026-09-16T12:00:00Z",
  "observed_at": "2026-09-16T12:00:00Z",
  "soil": {
    "ph": 6.2,
    "organic_carbon": 0.3,
    "moisture": 18
  },
  "climate": {
    "temperature": 29.0,
    "rainfall": 500.0
  },
  "land": {
    "use": "agriculture",
    "crop": "wheat",
    "cropping_system": "monoculture"
  },
  "biodiversity": {
    "species_richness": 12,
    "habitat_diversity": "low"
  },
  "human_impact": {
    "pollution": "moderate",
    "deforestation": "low"
  },
  "location": null,
  "source_name": null,
  "source_type": null,
  "source_reference": null,
  "data_quality": null,
  "confidence": null
}
```

## Validation Behavior
- Inputs are strictly validated via Pydantic.
- `soil.ph` is constrained to scientifically valid ranges (0.0 to 14.0).
- `biodiversity.species_richness` and `climate.rainfall` cannot be negative.
- Invalid requests immediately return `422 Unprocessable Entity` with a structured JSON detailing the exact field errors.
- Non-existent profile lookups/updates return `404 Not Found`.

## Knowledge Search API

**Endpoint**: `POST /api/v1/knowledge/search`
Retrieves relevant scientific chunks from the ChromaDB knowledge base based on a semantic query.

### Request Body
```json
{
  "query": "relationship between soil carbon and biodiversity",
  "top_k": 5
}
```

### Success Response (200 OK)
```json
{
  "results": [
    {
      "text": "State of Knowledge of Soil Biodiversity...",
      "relevance": 0.8065,
      "source_id": "fao_soil_biodiversity_2020",
      "chunk_id": "fao_soil_biodiversity_2020_null_c000_339058b3e4b9",
      "url": "https://www.fao.org/documents/card/en/c/CB1928EN/",
      "topic": "soil_biodiversity",
      "topics": [
        "soil_health",
        "pollution"
      ],
      "relationships": [
        "Soil Health ↔ Biodiversity"
      ]
    }
  ]
}
```

## ChromaDB Knowledge Architecture

The RAG subsystem implements persistent vector storage for scientific evidence retrieval.

- **Storage Location**: `knowledge_base/chroma`
- **Collection Name**: `ecomind_scientific_knowledge`
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (Auto-downloaded, dimension 384)

### Indexing
Run the indexing pipeline to populate ChromaDB from the generated embeddings:
```bash
$env:PYTHONPATH="backend"
python -m app.rag.index
```

### Search Process & Relevance Interpretation
When a query hits the `/search` endpoint:
1. The `KnowledgeSearchService` embeds the query dynamically.
2. ChromaDB evaluates vector nearest-neighbors using cosine similarity.
3. Distances are mathematically transformed into a user-facing `relevance` metric (`1.0 - distance`). A score closer to `1.0` indicates high semantic overlap.
4. Rich arrays (`topics`, `relationships`) stored as flattened strings inside ChromaDB are seamlessly reconstructed into structured arrays before the API response is served.

**Provenance Guarantees**: The endpoint exclusively returns real passages extracted during the ingestion pipeline. No LLM generation or hallucination is performed during the search retrieval layer.

## Testing

Run the full suite using pytest from the repository root: the project root.
```bash
# Ensure PYTHONPATH is set so pytest can locate the 'app' module
$env:PYTHONPATH="backend" # Windows PowerShell
export PYTHONPATH="backend" # Linux/Mac

pytest tests/unit/
```
