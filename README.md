# EcoMind AI

EcoMind AI is an Environmental Intelligence System designed to combine environmental data, scientific knowledge, multi-variable reasoning, and evidence-based ecological interventions.

**This project is designed as an AI Environmental Scientist system, not a generic chatbot.**

## 1. Project Overview
EcoMind AI acts as a sophisticated decision-support system to analyze environmental metrics (like rainfall, soil organic carbon, species richness), assess ecological risks, and recommend actionable interventions backed by scientific research.

## 2. Core Objective
Use AI to understand environmental systems and support evidence-based ecological decisions without hallucinating data, relationships, or scientific literature.

## 3. Architecture
The system enforces a strict pipeline separation:
`Environmental Data ↓ Data Processing ↓ Feature / Metric Generation ↓ Relationship Analysis ↓ Risk Detection ↓ Scientific Retrieval ↓ Evidence ↓ Multi-Variable Reasoning ↓ Intervention ↓ Impact Assessment`

## 4. Repository Structure
- `backend/`: FastAPI Python application containing core reasoning and data processing logic.
- `frontend/`: React/Vite web application for interacting with the system.
- `knowledge_base/`: Repository for scientific literature, documents, and environmental data metadata.
- `tests/`: Unit and integration testing suites.
- `docs/`: Technical and architectural documentation.
- `scripts/`: Data ingestion, pre-processing, and evaluation utilities.

## 5. Technology Stack
- **Backend:** Python, FastAPI
- **Frontend:** React, TypeScript, Vite
- **Infrastructure:** Docker, Docker Compose

## 6. Local Development
*To be populated with exact run instructions.*

## 6.1 Grounded conversational API

`POST /api/v1/chat/` provides the conversational explanation layer. It does not
make environmental assessments independently. For a supplied profile it runs:

`profile → baseline → relationships → risks → intervention candidates → recommendation quality guard → LLM explanation`

The LLM receives a controlled, Pydantic-validated context rather than database
objects. Its response is strictly validated against the `EnvironmentalResponse` Pydantic schema, ensuring the output structure is always:

```json
{
  "schema_version": "1.0",
  "response_type": "environmental_assessment",
  "assessment": {
    "summary": "Natural language summary of the deterministic reasoning.",
    "status": "informational"
  },
  "drivers": [],
  "recommendations": [],
  "metrics": [],
  "time_horizon": {},
  "confidence": {},
  "evidence": [],
  "variables_used": [],
  "reasoning_trace": []
}
```

**Grounding Validation**: The API guarantees that unrecognised metrics, fabricated evidence, or invented interventions are strictly rejected. If the configured LLM provider is unavailable, or if the LLM output violates the strict schema or consistency rules, the API returns a deterministic recommendation fallback that maintains the same exact schema. Conversation memory is bounded to recent messages and retains its active profile ID.

Example request:

```json
{
  "conversation_id": "farm-1",
  "profile_id": "1",
  "message": "Why are you recommending intercropping?"
}
```

## 7. Environment Variables
See `.env.example` for the required configuration structure.

## 8. Testing
Test suites are located in the `tests/` directory.

## 9. Git Workflow
Follow standard pull request models. Keep commits atomic and descriptive.

## 10. Development Roadmap
Refer to Phase documents. Currently in Phase 1: Engineering Foundation.

## 11. Recommendation Architecture
EcoMind AI employs a deterministic, evidence-backed environmental recommendation pipeline to eliminate LLM hallucinations:
1. **Profile Generation**: Ingestion of raw environmental variables.
2. **Baseline Analysis**: Scientific thresholding of metrics.
3. **Relationships**: Evaluation of multi-metric ecosystem relationships.
4. **Risk Patterns**: Generation of formal composite pressures.
5. **Intervention Graph**: Deterministic condition-matching to generate candidate solutions.
6. **Recommendation Engine**: Synthesis of explicit mechanisms, metric impacts, constraints, and ChromaDB-verified scientific provenance. 

*(The LLM is strictly reserved for the final natural-language explanation of this deterministic payload).*
