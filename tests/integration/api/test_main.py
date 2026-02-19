from video_service.infrastructure.adapters.input.api.main import create_app


def test_create_app_basic_configuration(monkeypatch):
    async def _fake_init_db():
        return None

    monkeypatch.setattr("video_service.infrastructure.adapters.input.api.main.init_db", _fake_init_db)

    app = create_app()

    assert app.title == "Video Service"
    assert app.version == "0.1.0"
    assert app.router is not None
