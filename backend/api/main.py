from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routes import (
    auth as auth_router,
    economy as economy_router,
    politics as politics_router,
    technology as technology_router,
    society as society_router,
    environment as environment_router,
    security as security_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Bolivia KPIs API",
    description=(
        "Monolithic data platform exposing political, economic, social, "
        "technological, environmental and security KPIs for Bolivia."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix=f"{PREFIX}/auth", tags=["Auth"])
app.include_router(economy_router.router, prefix=f"{PREFIX}/economy", tags=["Economy"])
app.include_router(politics_router.router, prefix=f"{PREFIX}/politics", tags=["Politics"])
app.include_router(technology_router.router, prefix=f"{PREFIX}/technology", tags=["Technology"])
app.include_router(society_router.router, prefix=f"{PREFIX}/society", tags=["Society"])
app.include_router(environment_router.router, prefix=f"{PREFIX}/environment", tags=["Environment"])
app.include_router(security_router.router, prefix=f"{PREFIX}/security", tags=["Security"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
