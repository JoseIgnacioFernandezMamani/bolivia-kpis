"""Basic smoke tests for the FastAPI application."""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    # Import here to avoid DB connection at module load
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    """GET /health should return 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


@pytest.mark.anyio
async def test_openapi_schema(client: AsyncClient):
    """OpenAPI schema should be reachable."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Bolivia KPIs API"


@pytest.mark.anyio
async def test_docs_endpoint(client: AsyncClient):
    """Swagger UI docs page should be reachable."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_economy_gdp_route(client: AsyncClient):
    """GDP route should return a paginated response structure."""
    response = await client.get("/api/v1/economy/gdp")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "items" in body


@pytest.mark.anyio
async def test_politics_elections_route(client: AsyncClient):
    """Elections route should return a paginated response."""
    response = await client.get("/api/v1/politics/elections")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "items" in body


@pytest.mark.anyio
async def test_auth_register_missing_fields(client: AsyncClient):
    """Registering without required fields should return 422."""
    response = await client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_auth_login_invalid(client: AsyncClient):
    """Logging in with non-existent credentials should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
