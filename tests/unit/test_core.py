from app.core.config import settings

def test_settings_loaded():
    assert settings.APP_NAME == "EcoMind AI"
    assert settings.API_PREFIX == "/api/v1"
    assert settings.APP_ENV in ["development", "production", "test"]
