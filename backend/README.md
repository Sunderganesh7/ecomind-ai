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

## How to Run Tests
Tests are located in the `tests/` directory at the project root.
```bash
# Ensure PYTHONPATH is set so pytest can locate the 'app' module
$env:PYTHONPATH="backend" # Windows PowerShell
export PYTHONPATH="backend" # Linux/Mac

pytest tests/unit/
```
