-- database/seed/categorias.sql
-- Categorías base necesarias para el módulo de tareas.
-- Ejecutar una sola vez después de crear las tablas (ver database/scripts/acadex.sql).

INSERT INTO categorias (nombre_categoria) VALUES
  ('Backend'),
  ('Frontend'),
  ('Diseño'),
  ('Documentación')
ON CONFLICT (nombre_categoria) DO NOTHING;