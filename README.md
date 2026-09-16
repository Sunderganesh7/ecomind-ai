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

## 7. Environment Variables
See `.env.example` for the required configuration structure.

## 8. Testing
Test suites are located in the `tests/` directory.

## 9. Git Workflow
Follow standard pull request models. Keep commits atomic and descriptive.

## 10. Development Roadmap
Refer to Phase documents. Currently in Phase 1: Engineering Foundation.
