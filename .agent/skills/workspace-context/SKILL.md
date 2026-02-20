---
name: workspace-context
description: Analyzes the local codebase to provide technically accurate answers grounded in the current workspace. Use when the user asks about project structure, how to implement features, the function of a specific file, or debugging within this specific repo.
---

# Workspace Context Architect

## Goal

Provide technical assistance strictly grounded in the current project's codebase, reading **only the files relevant to the user's question**. Never read files outside the detected scope.

## Instructions

### 1. Detect Scope First

Before reading anything, infer the user's scope from their question:

| Keyword / Intent                                | Scope          |
| ----------------------------------------------- | -------------- |
| "frontend", "UI", "component", "page", "style"  | Frontend only  |
| "backend", "API", "endpoint", "route", "model"  | Backend only   |
| "scraper", "scraping", "spider", "crawl", "ETL" | Scraper only   |
| "database", "migration", "schema", "table"      | Database only  |
| "deploy", "docker", "CI/CD", "container", "env" | DevOps only    |
| "project", "architecture", "overview", "setup"  | Global context |

### 2. Read Only Scope-Relevant Files

**Frontend scope** → Read only:

- `frontend/package.json`
- `frontend/next.config.js` (or equivalent bundler config)
- `frontend/tsconfig.json`
- `frontend/app/layout.tsx` + the specific page/component mentioned

**Backend scope** → Read only:

- `backend/api/main.py` (router wiring)
- `backend/api/config.py`
- The specific route or model file the user mentions (e.g., `routes/economy.py`)

**Scraper scope** → Read only:

- `backend/scraper/requirements.txt`
- The specific spider or pipeline file mentioned

**Database scope** → Read only:

- The specific migration file(s) relevant to the domain mentioned

**DevOps scope** → Read only:

- `docker-compose.yml`
- The specific `Dockerfile.*` for the service in question

**Global / Architecture scope** → Read only:

- `README.md`
- `docker-compose.yml`
- `.env.example`

### 3. Synthesize and Respond

- Reference only what you actually read.
- Match naming conventions, libraries, and patterns found in those files.
- Never suggest a library not present in the relevant `package.json` or `requirements.txt`.

### 4. Response Formatting

Always cite the file you read: _"According to `frontend/package.json`, you are using Next.js 15..."_

---

## Constraints

- **Minimal reads**: Read the fewest files necessary to answer accurately. Do not load the entire project.
- **Scope lock**: If the user asks about frontend, do not read backend files, and vice versa.
- **No secrets**: Never display values from `.env` files.
- **File integrity**: Do not modify config files unless explicitly asked.
- **Out-of-scope disclosure**: If a question falls outside the current stack, state it's a general suggestion, not project-specific.

---

## Examples

**User**: "How do I add a new map component?"
**Agent**: _Detects scope → Frontend. Reads `frontend/package.json`, `frontend/app/layout.tsx`, scans `frontend/components/Map/`_ → "You're using MapLibre GL + Deck.gl 9. Create a new file in `frontend/components/Map/` following the pattern of existing layer components..."

**User**: "How do I add a new API endpoint for the economy module?"
**Agent**: _Detects scope → Backend. Reads `backend/api/main.py`, `backend/api/routes/economy.py`_ → "Register your new route in `economy.py` following the existing pattern, then confirm it's mounted in `main.py` under `/api/v1/economy`..."

**User**: "What does the scraper use to crawl pages?"
**Agent**: _Detects scope → Scraper. Reads `backend/scraper/requirements.txt`_ → "The scraper depends on Crawlee as its crawling framework..."

**User**: "Give me an overview of the whole project."
**Agent**: _Detects scope → Global. Reads `README.md`, `docker-compose.yml`, `.env.example`_ → "The project runs 4 services: PostgreSQL+PostGIS, Redis, FastAPI, and Next.js..."
