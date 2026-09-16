# Phase 2: Task 03 - Environmental Data Model Report

The foundational Environmental Data Model for **EcoMind AI** has been successfully designed and implemented according to the Phase 2 requirements, strict anti-hallucination rules, and zero-logic constraints of the frozen `PROJECT_SCOPE.md`.

## 1. Files Created
- `backend/app/schemas/environmental.py`
- `backend/app/models/environmental.py`
- `backend/app/schemas/__init__.py`
- `tests/unit/test_environmental_models.py`

## 2. Files Modified
- `backend/app/models/__init__.py`

## 3. Environmental Models Created (SQLAlchemy)
A core `EnvironmentalObservation` table was created to serve as the unified root for environmental records. To avoid sparse columns and maintain maximum extensibility, the observation is linked via 1:1 relationships (with cascading deletes) to category tables:
- `LocationModel`
- `SoilModel`
- `ClimateModel`
- `LandModel`
- `BiodiversityModel`
- `HumanImpactModel`

## 4. Pydantic Schemas Created
Created heavily validated Pydantic models aligning exactly with the API expectations:
- `Location`, `Soil`, `Climate`, `Land`, `Biodiversity`, `HumanImpact`
- `EnvironmentalObservationCreate`
- `EnvironmentalObservation`

## 5. Validation Rules Implemented
- **Latitude / Longitude:** Restricted strictly to geographic bounds (`-90` to `90` and `-180` to `180`).
- **Soil pH:** Restricted to valid pH scale (`0.0` to `14.0`).
- **Species Richness & Rainfall:** Non-negative limits enforced (`ge=0`).
- **Confidence:** Capped to a percentage scale (`0.0` to `1.0`).
- *Note:* No arbitrary scientific thresholds (like `pH < 5 = degraded`) were hardcoded into the schema. Validation strictly isolates invalid data from environmentally "bad" data.

## 6. Unit Conventions
Units were explicitly documented in the Pydantic descriptions to prevent silent misinterpretation by the future reasoning layer:
- `temperature`: °C
- `rainfall`: mm
- `soil_ph`: pH scale
- `organic_carbon`: percentage
- `moisture`, `pollution`, `deforestation`: Original source units preserved.

## 7. Missing-Data Handling
Null vs Zero distinction is heavily enforced via Python `Optional` types. If a value is unknown, it remains `null` (None), ensuring the reasoning engine is never fed fake observations or accidental zero values.

## 8. Data-Source Traceability
Each `EnvironmentalObservation` includes mandatory temporal (`observed_at`) and traceability metadata:
- `source_name`, `source_type`, `source_reference`, `data_quality`, `confidence`.

## 9. Tests Added
Wrote Pytest coverage addressing:
1. Valid nested environmental observations.
2. Invalid latitude rejections.
3. Invalid longitude rejections.
4. Invalid soil pH formats/ranges.
5. Missing optional environmental variables (asserting `None`).
6. Distinguishing `null` from `0.0`.
7. Full model serialization logic.

## 10. Test Results
All 7 tests passed successfully (`7 passed in 0.05s`). Also cleared a Pydantic V2 class-based config deprecation warning, keeping the codebase fully clean.

## 11. API Preparation
The Pydantic schemas (especially `EnvironmentalObservationCreate` and `EnvironmentalObservation`) are completely decoupled from SQLAlchemy objects via `from_attributes=True` and are immediately ready for ingestion pipelines or CRUD endpoints.

## 12. Git Status
All modifications were successfully added and committed securely.
Commit Hash: `462098d`
Message: `feat(data): add environmental observation models`

## 13. Design Decisions
- **SQLAlchemy 1:1 Relationships vs Flat Table:** Elected for 1:1 foreign-key mappings linking categories back to the parent `EnvironmentalObservation`. This perfectly mimics the nested conceptual tree in the architecture prompt and prevents a single table from growing infinitely wide when more variables are added in future phases.

## 14. Intentionally Deferred
- **Reasoning & RAG:** No chatbot logic, vector embeddings, or recommendations were implemented.
- **API Endpoints:** The HTTP endpoints to ingest these observations were intentionally avoided to adhere to the strict boundaries of Task 03.
- **Complex GIS:** Basic Lat/Lon floats were used to establish location. PostGIS wasn't prematurely instantiated.
