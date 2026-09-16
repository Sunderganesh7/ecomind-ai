# Phase 1: Task 04 - Environmental Profile API Report

The Environmental Profile API for **EcoMind AI** has been successfully implemented, establishing the structured-input foundation necessary for the subsequent AI layers without violating the frozen `PROJECT_SCOPE.md`.

## 1. Files Created
- `backend/app/api/v1/profiles.py` (API router defining POST, GET, PUT)
- `backend/app/services/profile_service.py` (Business logic for database handling)
- `backend/app/services/__init__.py`
- `tests/unit/test_profiles_api.py` (Test suite for the API)
- `backend/README.md` (Detailed API documentation)

## 2. Files Modified
- `backend/app/api/v1/router.py` (Registered the `/profiles` router)
- `backend/app/schemas/environmental.py` (Added field aliases `ph` and `use` to match the exact JSON payload requirement, and configured `observed_at` to default safely to `datetime.utcnow()`)
- `tests/unit/test_environmental_models.py` (Updated previous tests to accommodate new categorical strings)

## 3. Endpoints Implemented
- `POST /api/v1/profiles`: Creates a profile.
- `GET /api/v1/profiles/{id}`: Retrieves a profile. Returns `404 Not Found` if missing.
- `PUT /api/v1/profiles/{id}`: Updates a profile. Returns `404 Not Found` if missing.
*Note:* These endpoints successfully appear in the FastAPI OpenAPI specification.

## 4. Architecture & Validation
A strict separation of concerns was maintained:
`API Router` $\to$ `Pydantic Schema Validation` $\to$ `Profile Service` $\to$ `SQLAlchemy Model` $\to$ `Database`

Validation correctly prevents negative `organic_carbon`, `rainfall`, and `moisture`, while keeping missing values as `null` instead of converting them to zero. The API absolutely does **not** hardcode arbitrary biodiversity risk judgements, delegating that strictly to the future phases.

## 5. Testing & Verification
A complete API test suite was authored utilizing FastAPI `TestClient` alongside an in-memory SQLite database setup.
The following scenarios were verified:
1. **Create profile**: (Successfully matched requested structured JSON payload)
2. **Retrieve profile**: (Successfully extracted matched data)
3. **Update profile**: (Updated individual environmental sectors successfully)
4. **Nonexistent profile**: (Returned `404`)
5. **Invalid data**: (Returned `422 Validation Error` successfully when negative pH was tested)
6. **Missing required structure**: (Returned `422 Validation Error`)

All 6 new API tests, plus the 7 data-model tests, pass successfully. 

## 6. Git Status
All modifications were added and committed securely.
Commit Hash: `7539c61`
Message: `feat(api): add environmental profile endpoints`

## 7. Intentionally Deferred
- LLM reasoning, conversational chat, RAG, and biodiversity/risk scoring were avoided to strictly protect the scope boundaries. The API only saves and loads factual observations.
