-- ============================================================
-- 001_initial_schema.sql
-- Bolivia KPIs – complete initial schema for all 6 modules
-- ============================================================

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ── Shared ENUM types ────────────────────────────────────────────────────────
DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('admin', 'editor', 'public');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- MODULE 0: Departments (shared lookup)
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    code            VARCHAR(10),
    geometry        geography(POLYGON, 4326),
    geom_simplified geography(POLYGON, 4326),
    source          VARCHAR(512),
    last_updated    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_departments_geometry        ON departments USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_departments_geom_simplified ON departments USING GIST(geom_simplified);

-- ============================================================
-- MODULE 1: Economy
-- ============================================================
CREATE TABLE IF NOT EXISTS gdp_per_capita (
    id             SERIAL PRIMARY KEY,
    department_id  INTEGER REFERENCES departments(id),
    year           INTEGER NOT NULL,
    value_usd      DOUBLE PRECISION NOT NULL,
    source         VARCHAR(512),
    last_updated   TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gdp_year          ON gdp_per_capita(year);
CREATE INDEX IF NOT EXISTS idx_gdp_department    ON gdp_per_capita(department_id);

CREATE TABLE IF NOT EXISTS inflation (
    id           SERIAL PRIMARY KEY,
    year         INTEGER NOT NULL,
    month        INTEGER,
    rate         DOUBLE PRECISION NOT NULL,
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_inflation_year ON inflation(year);

CREATE TABLE IF NOT EXISTS unemployment (
    id            SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    year          INTEGER NOT NULL,
    rate          DOUBLE PRECISION NOT NULL,
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_unemployment_year       ON unemployment(year);
CREATE INDEX IF NOT EXISTS idx_unemployment_department ON unemployment(department_id);

CREATE TABLE IF NOT EXISTS exports (
    id                SERIAL PRIMARY KEY,
    product           VARCHAR(255) NOT NULL,
    year              INTEGER NOT NULL,
    value_usd         BIGINT NOT NULL,
    percentage_of_total DOUBLE PRECISION,
    source            VARCHAR(512),
    last_updated      TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_exports_year ON exports(year);

CREATE TABLE IF NOT EXISTS public_contracts (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(512) NOT NULL,
    amount        DOUBLE PRECISION,
    contractor    VARCHAR(255),
    department_id INTEGER REFERENCES departments(id),
    geometry      geography(POINT, 4326),
    date          DATE,
    sicoes_id     VARCHAR(100) UNIQUE,
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contracts_geometry   ON public_contracts USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_contracts_department ON public_contracts(department_id);
CREATE INDEX IF NOT EXISTS idx_contracts_date       ON public_contracts(date);

-- ============================================================
-- MODULE 2: Politics
-- ============================================================
CREATE TABLE IF NOT EXISTS election_results (
    id            SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    election_type VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    party         VARCHAR(200),
    candidate     VARCHAR(200),
    votes         INTEGER,
    percentage    DOUBLE PRECISION,
    geometry      geography(POLYGON, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_elections_year       ON election_results(year);
CREATE INDEX IF NOT EXISTS idx_elections_department ON election_results(department_id);
CREATE INDEX IF NOT EXISTS idx_elections_geometry   ON election_results USING GIST(geometry);

CREATE TABLE IF NOT EXISTS democracy_index (
    id           SERIAL PRIMARY KEY,
    year         INTEGER NOT NULL,
    score        DOUBLE PRECISION NOT NULL,
    category     VARCHAR(100),
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_democracy_year ON democracy_index(year);

CREATE TABLE IF NOT EXISTS corruption_index (
    id           SERIAL PRIMARY KEY,
    year         INTEGER NOT NULL,
    cpi_score    DOUBLE PRECISION NOT NULL,
    rank         INTEGER,
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_corruption_year ON corruption_index(year);

CREATE TABLE IF NOT EXISTS social_conflicts (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(512) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    geometry      geography(POINT, 4326),
    start_date    DATE,
    end_date      DATE,
    type          VARCHAR(100),
    description   TEXT,
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_conflicts_geometry   ON social_conflicts USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_conflicts_department ON social_conflicts(department_id);
CREATE INDEX IF NOT EXISTS idx_conflicts_start_date ON social_conflicts(start_date);

CREATE TABLE IF NOT EXISTS tioc_territories (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(300) NOT NULL,
    ethnicity  VARCHAR(200),
    area_ha    DOUBLE PRECISION,
    geometry   geography(MULTIPOLYGON, 4326),
    source     VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tioc_geometry ON tioc_territories USING GIST(geometry);

-- ============================================================
-- MODULE 3: Technology
-- ============================================================
CREATE TABLE IF NOT EXISTS internet_penetration (
    id                    SERIAL PRIMARY KEY,
    year                  INTEGER NOT NULL,
    department_id         INTEGER REFERENCES departments(id),
    percentage            DOUBLE PRECISION NOT NULL,
    fixed_broadband_per_100 DOUBLE PRECISION,
    mobile_per_100        DOUBLE PRECISION,
    source                VARCHAR(512),
    last_updated          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_internet_year       ON internet_penetration(year);
CREATE INDEX IF NOT EXISTS idx_internet_department ON internet_penetration(department_id);

CREATE TABLE IF NOT EXISTS coverage_zones (
    id         SERIAL PRIMARY KEY,
    operator   VARCHAR(100),
    technology VARCHAR(10) NOT NULL,
    geometry   geography(MULTIPOLYGON, 4326),
    source     VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_coverage_geometry ON coverage_zones USING GIST(geometry);

CREATE TABLE IF NOT EXISTS rd_spending (
    id                SERIAL PRIMARY KEY,
    year              INTEGER NOT NULL,
    percentage_of_gdp DOUBLE PRECISION,
    amount_usd        DOUBLE PRECISION,
    source            VARCHAR(512),
    last_updated      TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rd_year ON rd_spending(year);

CREATE TABLE IF NOT EXISTS digital_literacy (
    id            SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    rate          DOUBLE PRECISION NOT NULL,
    age_group     VARCHAR(50),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_digital_literacy_year ON digital_literacy(year);

-- ============================================================
-- MODULE 4: Society
-- ============================================================
CREATE TABLE IF NOT EXISTS hdi_index (
    id            SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    municipality  VARCHAR(200),
    department_id INTEGER REFERENCES departments(id),
    hdi_score     DOUBLE PRECISION NOT NULL,
    geometry      geography(POLYGON, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_hdi_year       ON hdi_index(year);
CREATE INDEX IF NOT EXISTS idx_hdi_geometry   ON hdi_index USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_hdi_department ON hdi_index(department_id);

CREATE TABLE IF NOT EXISTS life_expectancy (
    id            SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    years         DOUBLE PRECISION NOT NULL,
    gender        VARCHAR(10),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_life_expectancy_year ON life_expectancy(year);

CREATE TABLE IF NOT EXISTS nutrition_indicators (
    id                        SERIAL PRIMARY KEY,
    year                      INTEGER NOT NULL,
    department_id             INTEGER REFERENCES departments(id),
    chronic_malnutrition_rate DOUBLE PRECISION,
    acute_malnutrition_rate   DOUBLE PRECISION,
    source                    VARCHAR(512),
    last_updated              TIMESTAMPTZ,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_nutrition_year ON nutrition_indicators(year);

CREATE TABLE IF NOT EXISTS census_data (
    id                SERIAL PRIMARY KEY,
    year              INTEGER NOT NULL,
    department_id     INTEGER REFERENCES departments(id),
    total_population  INTEGER,
    urban_population  INTEGER,
    rural_population  INTEGER,
    literacy_rate     DOUBLE PRECISION,
    source            VARCHAR(512),
    last_updated      TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_census_year       ON census_data(year);
CREATE INDEX IF NOT EXISTS idx_census_department ON census_data(department_id);

CREATE TABLE IF NOT EXISTS gender_gap_index (
    id              SERIAL PRIMARY KEY,
    year            INTEGER NOT NULL,
    overall_score   DOUBLE PRECISION,
    economic_score  DOUBLE PRECISION,
    education_score DOUBLE PRECISION,
    health_score    DOUBLE PRECISION,
    political_score DOUBLE PRECISION,
    source          VARCHAR(512),
    last_updated    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gender_gap_year ON gender_gap_index(year);

CREATE TABLE IF NOT EXISTS basic_services (
    id                 SERIAL PRIMARY KEY,
    year               INTEGER NOT NULL,
    department_id      INTEGER REFERENCES departments(id),
    water_access_rate  DOUBLE PRECISION,
    sanitation_rate    DOUBLE PRECISION,
    electricity_rate   DOUBLE PRECISION,
    gas_rate           DOUBLE PRECISION,
    source             VARCHAR(512),
    last_updated       TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_basic_services_year       ON basic_services(year);
CREATE INDEX IF NOT EXISTS idx_basic_services_department ON basic_services(department_id);

-- ============================================================
-- MODULE 5: Environment
-- ============================================================
CREATE TABLE IF NOT EXISTS deforestation_zones (
    id            SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    area_ha       DOUBLE PRECISION,
    department_id INTEGER REFERENCES departments(id),
    geometry      geography(MULTIPOLYGON, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_deforestation_geometry ON deforestation_zones USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_deforestation_year     ON deforestation_zones(year);

CREATE TABLE IF NOT EXISTS protected_areas (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(300) NOT NULL,
    category     VARCHAR(100),
    area_ha      DOUBLE PRECISION,
    geometry     geography(MULTIPOLYGON, 4326),
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_protected_areas_geometry ON protected_areas USING GIST(geometry);

CREATE TABLE IF NOT EXISTS mining_concessions (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(300),
    mineral      VARCHAR(100),
    company      VARCHAR(300),
    area_ha      DOUBLE PRECISION,
    geometry     geography(POLYGON, 4326),
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mining_geometry ON mining_concessions USING GIST(geometry);

CREATE TABLE IF NOT EXISTS lithium_salt_flats (
    id                    SERIAL PRIMARY KEY,
    name                  VARCHAR(200) NOT NULL,
    estimated_reserves_mt DOUBLE PRECISION,
    geometry              geography(MULTIPOLYGON, 4326),
    source                VARCHAR(512),
    last_updated          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lithium_geometry ON lithium_salt_flats USING GIST(geometry);

CREATE TABLE IF NOT EXISTS co2_emissions (
    id           SERIAL PRIMARY KEY,
    year         INTEGER NOT NULL,
    sector       VARCHAR(100),
    value_mt     DOUBLE PRECISION NOT NULL,
    source       VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_co2_year ON co2_emissions(year);

CREATE TABLE IF NOT EXISTS forest_fires (
    id            SERIAL PRIMARY KEY,
    detected_date DATE NOT NULL,
    confidence    INTEGER,
    frp           DOUBLE PRECISION,
    satellite     VARCHAR(50),
    geometry      geography(POINT, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fires_geometry     ON forest_fires USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_fires_detected_date ON forest_fires(detected_date);

-- ============================================================
-- MODULE 6: Security
-- ============================================================
CREATE TABLE IF NOT EXISTS crime_rates (
    id              SERIAL PRIMARY KEY,
    year            INTEGER NOT NULL,
    department_id   INTEGER REFERENCES departments(id),
    crime_type      VARCHAR(200),
    count           INTEGER,
    rate_per_100k   DOUBLE PRECISION,
    source          VARCHAR(512),
    last_updated    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_crime_rates_year       ON crime_rates(year);
CREATE INDEX IF NOT EXISTS idx_crime_rates_department ON crime_rates(department_id);

CREATE TABLE IF NOT EXISTS drug_seizures (
    id            SERIAL PRIMARY KEY,
    date          DATE,
    drug_type     VARCHAR(100),
    quantity_kg   DOUBLE PRECISION,
    department_id INTEGER REFERENCES departments(id),
    geometry      geography(POINT, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_drug_seizures_geometry ON drug_seizures USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_drug_seizures_date     ON drug_seizures(date);

CREATE TABLE IF NOT EXISTS road_segments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(300),
    road_type   VARCHAR(50),
    condition   VARCHAR(50),
    length_km   DOUBLE PRECISION,
    geometry    geography(LINESTRING, 4326),
    source      VARCHAR(512),
    last_updated TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_road_segments_geometry ON road_segments USING GIST(geometry);

CREATE TABLE IF NOT EXISTS prisons (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(300) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    capacity      INTEGER,
    population    INTEGER,
    geometry      geography(POINT, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prisons_geometry ON prisons USING GIST(geometry);

CREATE TABLE IF NOT EXISTS healthcare_facilities (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(300) NOT NULL,
    facility_type VARCHAR(100),
    department_id INTEGER REFERENCES departments(id),
    beds          INTEGER,
    geometry      geography(POINT, 4326),
    source        VARCHAR(512),
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_healthcare_geometry   ON healthcare_facilities USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_healthcare_department ON healthcare_facilities(department_id);
