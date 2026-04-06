---
name: code-formatting
description: >
  Enforces industry-standard naming conventions, clean code principles (SOLID,
  DRY, KISS), and automatic formatting on every file created or modified in this
  project. Use when creating or editing Python, TSX/TS, SQL, Docker, or config
  files. Triggers: "create", "add", "new", "edit", "refactor", "component",
  "route", "model", "migration", "spider", "hook", "service", "Dockerfile".
---

# Code Formatting, Naming & Clean Code Standards

## Goal

Every file generated or modified must:

1. Follow project-consistent naming conventions for its file type.
2. Apply SOLID, DRY, and KISS principles in its internal structure.
3. Be automatically formatted — **after the user approves changes** — by running
   `.agent/skills/code-formatting/scripts/format.sh` scoped only to the files that were touched.

---

## Formatter Pipeline

| File type        | Tool     | Scope in format.sh                              |
| ---------------- | -------- | ----------------------------------------------- |
| `.py`            | Ruff     | `ruff format <file> && ruff check --fix <file>` |
| `.sql`           | SQLFluff | `sqlfluff fix <file> --dialect postgres`        |
| `.ts` / `.tsx`   | Prettier | `pnpm dlx prettier@3 --write <file>`            |
| `.json` / `.css` | Prettier | `pnpm dlx prettier@3 --write <file>`            |
| `Dockerfile.*`   | Prettier | `pnpm dlx prettier@3 --write <file>`            |
| `.yml` / `.yaml` | Prettier | `pnpm dlx prettier@3 --write <file>`            |

### Virtual Environment

All Python tools (Ruff, SQLFluff) live in `backend/.venv`:

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install ruff sqlfluff
```

The `.agent/skills/code-formatting/scripts/format.sh` script activates this venv automatically before running Python formatters.

### .agent/skills/code-formatting/scripts/format.sh — Scoped to Modified Files

```bash
#!/bin/bash
# Usage: .agent/skills/code-formatting/scripts/format.sh path/to/file1.py path/to/file2.tsx
# Formats ONLY the files passed as arguments.
# With no args: formats the entire project (fallback).

set -e

if [ -f "backend/.venv/bin/activate" ]; then
  source backend/.venv/bin/activate
fi

FILES=("$@")

if [ ${#FILES[@]} -eq 0 ]; then
  echo "⚠️  No files specified. Formatting entire project..."
  ruff format . && ruff check --fix .
  sqlfluff fix database/ --dialect postgres || true
  pnpm dlx prettier@3 --write "**/*.{ts,tsx,json,css,yml,yaml}" "Dockerfile*"
  exit 0
fi

for FILE in "${FILES[@]}"; do
  echo "🔧 Formatting: $FILE"
  case "$FILE" in
    *.py)
      ruff format "$FILE" && ruff check --fix "$FILE" ;;
    *.sql)
      sqlfluff fix "$FILE" --dialect postgres || true ;;
    *.ts|*.tsx|*.json|*.css|*.yml|*.yaml|Dockerfile*)
      pnpm dlx prettier@3 --write "$FILE" ;;
  esac
done

echo "✅ Done."
```

---

## Instructions

### Step 1 — Detect Scope

Infer file type and domain from the user's request:

| User says                              | File type    | Target folder                    |
| -------------------------------------- | ------------ | -------------------------------- |
| "component", "page", "UI", "layout"    | `.tsx`       | `frontend/components/` or `app/` |
| "hook"                                 | `.ts`        | `frontend/hooks/`                |
| "route", "endpoint"                    | `.py`        | `backend/api/routes/`            |
| "model", "schema" (Python)             | `.py`        | `backend/api/models/`            |
| "scraper", "spider", "pipeline", "ETL" | `.py`        | `backend/scraper/`               |
| "migration", "table", "index"          | `.sql`       | `database/migrations/`           |
| "Dockerfile", "container"              | `Dockerfile` | `docker/`                        |
| "config", "settings"                   | `.py`        | `backend/api/config.py`          |

### Step 2 — Apply Naming Conventions (see sections below)

### Step 3 — Apply Clean Code Principles (see section below)

### Step 4 — Generate the File

### Step 5 — After User Approves, Run Formatter Immediately

**Do not ask.** Run without prompting:

```bash
.agent/skills/code-formatting/scripts/format.sh <path/to/file1> <path/to/file2>
```

List only the exact files created or modified in this interaction. Never pass the
entire project path unless explicitly asked.

---

## Clean Code Principles (apply to ALL file types)

### SOLID

- **S — Single Responsibility**: Each file, class, and function does one thing only.
  - ❌ `def fetch_and_save_economy_data():`
  - ✅ `def fetch_economy_data():` + `def save_economy_data():`
- **O — Open/Closed**: Add behavior by extending, not modifying. Use abstract
  base classes in Python. Use composition in React components.
- **L — Liskov Substitution**: Subclasses must honor their parent's contract.
  Never override a method to silently break its behavior.
- **I — Interface Segregation**: Keep interfaces small and focused. One router
  per domain in FastAPI. One concern per React component.
- **D — Dependency Inversion**: Depend on abstractions. Use `Depends()` in
  FastAPI. Pass data via props/hooks in React, not hardcoded globals.

### DRY (Don't Repeat Yourself)

- Extract repeated logic into `backend/api/utils/` or `frontend/hooks/`.
- Never duplicate SQL fragments — use CTEs or views instead.
- Shared TypeScript types go in `frontend/types/`.

### KISS (Keep It Simple)

- Prefer flat over nested. Max 2 levels of nesting in conditionals.
- Prefer early returns over deep if/else chains.
- Prefer explicit names over clever abbreviations.

### Hard Limits

- Max function/method length: **30 lines**. Extract if longer.
- Max file length: **300 lines**. Split by responsibility if longer.
- No magic numbers — always use named constants.
- Every public function and component must have a docstring or JSDoc comment.

---

## Python Standards (FastAPI / Scraper)

### Naming

| Element      | Convention         | Example               |
| ------------ | ------------------ | --------------------- |
| Files        | `snake_case.py`    | `economy_routes.py`   |
| Folders      | `snake_case/`      | `bolivia_scraper/`    |
| Classes      | `PascalCase`       | `EconomyIndicator`    |
| Functions    | `snake_case()`     | `get_gdp_by_region()` |
| Variables    | `snake_case`       | `gdp_value`           |
| Constants    | `UPPER_SNAKE_CASE` | `MAX_RETRIES`         |
| Private      | `_prefix`          | `_parse_row()`        |
| Type aliases | `PascalCase`       | `RegionId = int`      |

### Import Order (enforced by Ruff)

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Internal
from api.database import get_db
from api.models.economy import EconomyIndicator
```

### FastAPI Route Template

```python
"""
Economy routes — /api/v1/economy
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.economy import EconomyIndicator

router = APIRouter(prefix="/economy", tags=["economy"])


@router.get("/", summary="List economy indicators")
async def list_economy_indicators(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return all economy indicators."""
    ...
```

### Scraper / Spider Template

```python
"""
Bolivia <domain> spider.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
BASE_URL = "https://example.gov.bo"


@dataclass
class RawRecord:
    """Represents a single scraped record before ETL."""

    source_url: str
    raw_data: dict


class BoliviaSpider:
    """Crawls <domain> data from the Bolivia government portal."""

    async def run(self) -> list[RawRecord]:
        """Entry point. Returns list of raw records."""
        ...
```

### Ruff Config (`backend/pyproject.toml`)

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## TSX / TypeScript Standards (Next.js 15)

### Naming

| Element            | Convention         | Example                        |
| ------------------ | ------------------ | ------------------------------ |
| Component files    | `PascalCase.tsx`   | `EconomyChart.tsx`             |
| Hook files         | `useCamelCase.ts`  | `useEconomyData.ts`            |
| Utility files      | `camelCase.ts`     | `formatIndicator.ts`           |
| Page files         | `page.tsx`         | `app/economy/page.tsx`         |
| Interfaces / Types | `PascalCase`       | `EconomyIndicator`, `MapLayer` |
| Constants          | `UPPER_SNAKE_CASE` | `API_BASE_URL`                 |
| Component folders  | `PascalCase/`      | `components/EconomyChart/`     |
| Feature folders    | `kebab-case/`      | `app/economy-dashboard/`       |

### Component Template

```tsx
// components/Economy/EconomyChart.tsx
import type { FC } from "react";

interface EconomyChartProps {
  /** Chart title displayed at the top */
  title: string;
  data: EconomyIndicator[];
}

/**
 * Renders economy indicators as a chart.
 * Single responsibility: display only, no data fetching.
 */
const EconomyChart: FC<EconomyChartProps> = ({ title, data }) => {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h2 className="text-lg font-semibold">{title}</h2>
      {/* chart content */}
    </div>
  );
};

export default EconomyChart;
```

### Hook Template

```ts
// hooks/useEconomyData.ts
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

/**
 * Fetches economy indicators from /api/v1/economy.
 * Single responsibility: data fetching only.
 */
export function useEconomyData() {
  const { data, error, isLoading } = useSWR("/api/v1/economy", fetcher);
  return { data, error, isLoading };
}
```

### Prettier Config (`frontend/.prettierrc`)

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

---

## SQL Standards (PostgreSQL + PostGIS)

### Naming

| Element      | Convention             | Example                           |
| ------------ | ---------------------- | --------------------------------- |
| Tables       | `snake_case` plural    | `economy_indicators`              |
| Columns      | `snake_case`           | `gdp_value`, `recorded_at`        |
| Primary keys | `id`                   | `id SERIAL PRIMARY KEY`           |
| Foreign keys | `<table_singular>_id`  | `region_id`, `user_id`            |
| Indexes      | `idx_<table>_<column>` | `idx_economy_indicators_date`     |
| Migrations   | `NNN_description.sql`  | `003_add_security_incidents.sql`  |
| SQL keywords | `UPPERCASE`            | `SELECT`, `FROM`, `WHERE`, `JOIN` |

### Migration Template

```sql
-- database/migrations/NNN_<description>.sql
-- Description: <what this migration does>
-- Date: YYYY-MM-DD

BEGIN;

CREATE TABLE IF NOT EXISTS economy_indicators (
    id          SERIAL PRIMARY KEY,
    region_id   INTEGER REFERENCES regions(id) ON DELETE CASCADE,
    gdp_value   NUMERIC(15, 2),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    geom        GEOMETRY(Point, 4326),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_economy_indicators_recorded_at
    ON economy_indicators (recorded_at);

COMMIT;
```

### SQLFluff Config (`.sqlfluff` at project root)

```ini
[sqlfluff]
dialect = postgres
templater = raw
max_line_length = 88

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper

[sqlfluff:rules:capitalisation.identifiers]
capitalisation_policy = lower
```

---

## Docker Standards

### Naming

| Element               | Convention                   | Example                       |
| --------------------- | ---------------------------- | ----------------------------- |
| Dockerfile names      | `Dockerfile.<service>`       | `Dockerfile.backend`          |
| Compose service names | `snake_case`                 | `bolivia_db`, `bolivia_api`   |
| Image tags            | `<project>-<service>:latest` | `bolivia-kpis-backend:latest` |

### Dockerfile Template

```dockerfile
# docker/Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# Dependencies first — leverages layer caching
COPY backend/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Constraints

- **Never** generate a file without applying naming rules for its type.
- **Never** mix naming styles (camelCase in Python, snake_case in TSX components).
- **Never** skip import ordering in Python files.
- **Never** write SQL without uppercase keywords and snake_case identifiers.
- **Never** ask the user if they want formatting — run it automatically after approval.
- **Never** run `.agent/skills/code-formatting/scripts/format.sh` without scoped file paths when only specific
  files were changed. Only use no-args (full project) when explicitly asked.
- **Always** keep functions under 30 lines and files under 300 lines.
- **Always** add a docstring or JSDoc comment to every public function/component.

---

## Examples

**User**: "Create a new route for GDP data"
**Agent**: Detects → Python / FastAPI → `backend/api/routes/economy.py`. Applies
Python naming + SOLID (one function per action). After approval runs:

```bash
.agent/skills/code-formatting/scripts/format.sh backend/api/routes/economy.py
```

**User**: "Add a map component for political events"
**Agent**: Detects → TSX → `frontend/components/Politics/PoliticalEventsLayer.tsx`.
PascalCase, typed props interface, Tailwind only, JSDoc. After approval runs:

```bash
.agent/skills/code-formatting/scripts/format.sh frontend/components/Politics/PoliticalEventsLayer.tsx
```

**User**: "Create a migration for the security_incidents table"
**Agent**: Detects → SQL → `database/migrations/003_security_incidents.sql`.
Uppercase keywords, snake_case columns, PostGIS geom, named index. After approval runs:

```bash
.agent/skills/code-formatting/scripts/format.sh database/migrations/003_security_incidents.sql
```

**User**: "Add a spider for economy ministry data"
**Agent**: Detects → Python / Scraper → `backend/scraper/bolivia_scraper/economy_spider.py`.
Dataclass for raw records, single-responsibility methods, module-level logger.
After approval runs:

```bash
.agent/skills/code-formatting/scripts/format.sh backend/scraper/bolivia_scraper/economy_spider.py
```
