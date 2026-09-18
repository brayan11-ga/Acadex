-- seed.sql – datos de ejemplo de Acadex
-- ------------------------------------------------------------
INSERT INTO public.usuario (nombre, correo, hash_contrasena, rol)
VALUES
    ('Ana Admin', 'admin@example.com', crypt('Demo123!', gen_salt('bf')), 'admin'),
    ('Luis Lider', 'lider@example.com', crypt('Demo123!', gen_salt('bf')), 'lider'),
    ('Carlos Colab', 'colaborador@example.com', crypt('Demo123!', gen_salt('bf')), 'colaborador');

INSERT INTO public.categoria (nombre, descripcion)
VALUES
    ('Desarrollo', 'Tareas relacionadas con desarrollo de software'),
    ('Diseño', 'Tareas de UI/UX y diseño gráfico'),
    ('Testing', 'Pruebas y QA');

-- Crear algunas tareas asignadas a los usuarios de ejemplo
INSERT INTO public.tarea (nombre, descripcion, fecha_entrega, prioridad, dificultad_estimada, tiempo_estimado, id_categoria, id_usuario, estado)
VALUES
    ('Implementar login', 'Crear endpoint /auth y UI de login', '2026-10-01', 2, 3, 8, 1, 2, 'pendiente'),
    ('Diseñar dashboard', 'Mockup del panel de estadísticas', '2026-09-20', 1, 2, 5, 2, 1, 'completada'),
    ('Escribir tests', 'Cobertura del 80% para la capa de servicios', '2026-09-25', 3, 4, 6, 3, 3, 'pendiente');

-- Estadísticas iniciales (se calcularán después)
INSERT INTO public.estadistica_categoria (id_categoria, total_tareas, tareas_completadas, promedio_tiempo_estimado)
SELECT id, 0, 0, 0 FROM public.categoria;
