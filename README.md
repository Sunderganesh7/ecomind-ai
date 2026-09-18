
# EcoMind AI

## AI Environmental Scientist

EcoMind AI is an environmental intelligence system that combines environmental data, scientific knowledge, multi-variable reasoning, risk analysis, and evidence-backed recommendations.

It is designed as an **AI Environmental Scientist, not a generic chatbot**.

## Features

- Environmental data management
- Soil, climate, biodiversity, land and human-impact analysis
- Multi-metric environmental relationship analysis
- Environmental risk detection
- Scientific knowledge retrieval using RAG
- Hugging Face embeddings + ChromaDB
- Evidence & reasoning visualization
- Evidence-backed recommendations
- AI Environmental Scientist conversational interface
- Structured and validated AI responses
- Deterministic reasoning and fallback mechanisms

## Architecture

```text
Environmental Data
        ↓
Baseline Analysis
        ↓
Multi-Metric Relationships
        ↓
Risk Detection
        ↓
Scientific Retrieval
        ↓
Evidence
        ↓
Recommendation
        ↓
LLM Explanation
````

## Technology Stack

* **Frontend:** React, TypeScript, Vite
* **Backend:** Python, FastAPI, Pydantic
* **AI:** Hugging Face Sentence Transformers, RAG
* **Vector Store:** ChromaDB
* **Infrastructure:** Docker, Docker Compose
* **CI/CD:** GitHub Actions

## Project Structure

```text
backend/          FastAPI backend
frontend/         React frontend
knowledge_base/   Scientific knowledge
tests/            Tests
docs/             Documentation
scripts/          Supporting utilities
.github/          GitHub Actions
```

## Local Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

Backend: `http://127.0.0.1:8000`

API Docs: `http://127.0.0.1:8000/docs`

## Environmental Reasoning

EcoMind AI analyzes multiple variables together, for example:

```text
Organic Carbon + Moisture → Habitat Quality
Rainfall + Temperature → Species Pressure
Land Use + Cropping System → Species Richness Pressure
Deforestation + Habitat Diversity → Biodiversity Pressure
```

## Recommendation Pipeline

```text
Profile
 ↓
Baseline
 ↓
Relationships
 ↓
Risks
 ↓
Interventions
 ↓
Scientific Evidence
 ↓
Validated Recommendation
```

The LLM is used for controlled natural-language explanation of the validated environmental reasoning rather than acting as the sole source of environmental knowledge.

## Scientific Grounding

Scientific documents are processed, chunked, embedded and stored for semantic retrieval. Retrieved evidence is connected to environmental reasoning and recommendations to improve traceability.

## Current Status

Implemented:

* Environmental intelligence dashboard
* Soil, climate, biodiversity, land and human-impact modules
* Risk Profile
* AI Scientist
* Evidence & Reasoning
* RAG knowledge retrieval
* Multi-metric reasoning
* Recommendation pipeline
* Structured API responses
* Testing and GitHub Actions foundation

Further improvements:

* Enhanced clarification workflow
* Expanded multi-turn memory
* Broader scientific corpus
* Evidence-supported quantitative impact estimates
* Production deployment

## Repository

[https://github.com/Sunderganesh7/ecomind-ai](https://github.com/Sunderganesh7/ecomind-ai)

## License

Developed for the Darukaa.Earth AI Biodiversity Intelligence Challenge.

