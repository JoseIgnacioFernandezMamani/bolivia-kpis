-- Seed Bolivia's 9 departments with approximate centroid points
-- Full boundary polygons should be loaded separately from official shapefiles.
-- Here we insert simplified bounding-box polygons for development/testing.

INSERT INTO departments (name, code, source, last_updated) VALUES
  ('La Paz',      'LP', 'INE Bolivia seed data', NOW()),
  ('Cochabamba',  'CB', 'INE Bolivia seed data', NOW()),
  ('Santa Cruz',  'SC', 'INE Bolivia seed data', NOW()),
  ('Oruro',       'OR', 'INE Bolivia seed data', NOW()),
  ('Potosí',      'PT', 'INE Bolivia seed data', NOW()),
  ('Chuquisaca',  'CH', 'INE Bolivia seed data', NOW()),
  ('Tarija',      'TJ', 'INE Bolivia seed data', NOW()),
  ('Beni',        'BE', 'INE Bolivia seed data', NOW()),
  ('Pando',       'PA', 'INE Bolivia seed data', NOW())
ON CONFLICT (name) DO NOTHING;

-- Update with approximate simplified WKT polygons (degree coordinates)
UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-70.0 -10.0, -65.5 -10.0, -65.5 -17.0, -70.0 -17.0, -70.0 -10.0))'
) WHERE name = 'La Paz';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-67.5 -16.0, -64.5 -16.0, -64.5 -18.5, -67.5 -18.5, -67.5 -16.0))'
) WHERE name = 'Cochabamba';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-64.0 -13.0, -57.5 -13.0, -57.5 -20.5, -64.0 -20.5, -64.0 -13.0))'
) WHERE name = 'Santa Cruz';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-69.5 -17.0, -66.5 -17.0, -66.5 -19.5, -69.5 -19.5, -69.5 -17.0))'
) WHERE name = 'Oruro';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-68.5 -19.0, -65.0 -19.0, -65.0 -22.5, -68.5 -22.5, -68.5 -19.0))'
) WHERE name = 'Potosí';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-65.5 -18.5, -63.0 -18.5, -63.0 -21.5, -65.5 -21.5, -65.5 -18.5))'
) WHERE name = 'Chuquisaca';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-65.5 -21.0, -62.5 -21.0, -62.5 -23.0, -65.5 -23.0, -65.5 -21.0))'
) WHERE name = 'Tarija';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-68.5 -10.0, -63.0 -10.0, -63.0 -15.5, -68.5 -15.5, -68.5 -10.0))'
) WHERE name = 'Beni';

UPDATE departments SET geometry = ST_GeogFromText(
  'POLYGON((-70.5 -9.5, -65.5 -9.5, -65.5 -11.5, -70.5 -11.5, -70.5 -9.5))'
) WHERE name = 'Pando';

-- Copy simplified geometry from geometry column
UPDATE departments SET geom_simplified = geometry WHERE geom_simplified IS NULL;
