# Bolivia KPIs – Data Platform

A monolithic, open-source data platform that aggregates, visualises, and
exposes Bolivia's political, economic, social, technological, environmental,
and security indicators through a REST API and an interactive map UI.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Browser                                                     │
│  Next.js 14  ←  MapLibre GL + Deck.gl layers                 │
└──────────────┬───────────────────────────────────────────────┘
               │  HTTP / REST
┌──────────────▼───────────────────────────────────────────────┐
│  FastAPI (Python 3.11)  –  /api/v1/*                         │
│  Auth · Economy · Politics · Technology · Society            │
│  Environment · Security                                      │
└──────┬──────────────────────────┬────────────────────────────┘
       │ SQLAlchemy async         │ Redis cache
┌──────▼──────┐           ┌──────▼──────┐
│  PostgreSQL │           │    Redis    │
│  + PostGIS  │           │  (hashes,   │
│  (15-3.3)  │           │   tiles)    │
└─────────────┘           └─────────────┘
       ▲
       │ psycopg2
┌──────┴──────────────────────────────────────────────────────┐
│  Scrapy + Playwright spiders (scheduled via GitHub Actions)  │
│  ETL pipelines (hash-based change detection)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Docker & Docker Compose | 24+ |
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL + PostGIS | 15 + 3.3 (handled by Docker) |

---

## Quick Start with Docker

```bash
# 1. Clone the repo
git clone https://github.com/your-org/bolivia-kpis.git
cd bolivia-kpis

# 2. Copy and edit environment variables
cp .env.example .env
# Edit .env with your secrets (JWT_SECRET_KEY, Google OAuth, etc.)

# 3. Start all services
docker compose up --build

# 4. Apply initial seed data (in a second terminal)
docker compose exec postgres psql -U bolivia -d bolivia_kpis \
  -f /docker-entrypoint-initdb.d/001_initial_schema.sql
docker compose exec postgres psql -U bolivia -d bolivia_kpis \
  -f /docker-entrypoint-initdb.d/002_users_schema.sql

# 5. Open the app
# Frontend:  http://localhost:3000
# API docs:  http://localhost:8000/docs
```

---

## Manual Installation

### Backend (FastAPI)

```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables (see .env.example)
export DATABASE_URL="postgresql+asyncpg://bolivia:bolivia@localhost:5432/bolivia_kpis"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your-secret"

uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm ci
cp ../.env.example .env.local   # adjust NEXT_PUBLIC_* vars
npm run dev   # http://localhost:3000
```

### Scraper (Scrapy + Playwright)

```bash
cd backend/scraper
pip install -r requirements.txt
playwright install chromium

# Run the OEP elections spider
scrapy crawl oep_elections
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async PostgreSQL URL (asyncpg driver) |
| `REDIS_URL` | Redis connection URL |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens |
| `JWT_ALGORITHM` | HS256 (default) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 1440 = 24 h) |
| `GOOGLE_CLIENT_ID` | Google OAuth2 app client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth2 app client secret |
| `GOOGLE_REDIRECT_URI` | OAuth2 callback URL |
| `NEXT_PUBLIC_API_URL` | Full base URL of the backend API |
| `NEXT_PUBLIC_MAPLIBRE_STYLE` | MapLibre style JSON URL |
| `SCRAPER_USER_AGENT` | HTTP User-Agent string for scrapers |

---

## API Documentation

Interactive Swagger UI is available at **`/docs`** once the backend is running.

Base path: `/api/v1`

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, Google OAuth |
| Economy | `/economy/gdp`, `/economy/inflation`, `/economy/exports`, `/economy/contracts` |
| Politics | `/politics/elections`, `/politics/conflicts`, `/politics/tioc`, `/politics/democracy-index` |
| Technology | `/technology/internet-penetration`, `/technology/coverage`, `/technology/rd-spending` |
| Society | `/society/hdi`, `/society/census`, `/society/gender-gap`, `/society/basic-services` |
| Environment | `/environment/deforestation`, `/environment/protected-areas`, `/environment/mining`, `/environment/fires` |
| Security | `/security/crime`, `/security/drug-seizures`, `/security/roads`, `/security/healthcare` |

All geospatial endpoints return **GeoJSON FeatureCollection** objects.
Tabular endpoints return paginated JSON (`total`, `page`, `page_size`, `items`).

---

## Data Modules

| Module | Key Indicators | Sources |
|--------|---------------|---------|
| **Economy** | GDP per capita, inflation, unemployment, exports, public contracts (SICOES) | INE, BCB, SICOES |
| **Politics** | Election results (OEP), social conflicts (CEDIB), TIOC territories, Democracy & Corruption Index | OEP, CEDIB, EIU, TI |
| **Technology** | Internet penetration, 4G/5G coverage zones, R&D spending, digital literacy | ATT, ITU, RICYT |
| **Society** | HDI by municipality, life expectancy, nutrition, census data, gender gap, basic services | UDAPE, INE, WEF |
| **Environment** | Deforestation zones, protected areas, mining concessions, lithium salars, CO₂, forest fires (NASA FIRMS) | ABT, SERNAP, NASA |
| **Security** | Crime rates, FELCN drug seizures, road network, prisons, healthcare facilities | FELCN, MINJUS, SNIS |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Open a Pull Request against `develop`

Please ensure:
- Python code passes `pytest`
- Frontend passes `tsc --noEmit` and `next build`
- New API endpoints have at least one test

---

## License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) for details.
Bolivia-KPIs: Open-source dashboard tracking Bolivia's national KPIs across economy (GDP, inflation), politics (democracy index, corruption), technology (internet penetration, R&amp;D), society (HDI, education), environment (deforestation, renewables), and security (crime rates, infrastructure).
