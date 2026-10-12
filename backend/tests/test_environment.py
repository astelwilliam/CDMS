from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_fastapi_test_client_works():
    """Verify the test stack without importing CDMS or accessing its database."""
    app = FastAPI()

    @app.get("/probe")
    def probe():
        return {"status": "ok"}

    with TestClient(app) as client:
        response = client.get("/probe")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
