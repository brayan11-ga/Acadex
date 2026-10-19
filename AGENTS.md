<!-- Ruta: AGENTS.md (raíz del repositorio Acadex, junto a backend/, frontend/, database/ y docs/) -->

# AGENTS.md — Reglas globales de Acadex

## 1. Qué es Acadex
Aplicación web de gestión de tareas académicas, tanto individuales como en grupo. Es un proyecto del SENA (Tecnólogo en Análisis y Desarrollo de Software) hecho por un equipo de 4 personas. Se va a presentar en una feria del SENA y debe quedar 100% terminado.

Funciones principales: registro e inicio de sesión (JWT), tareas individuales, grupos con líder e integrantes, tareas grupales con asignación y evidencias (archivos), notificaciones, cronómetro, panel (dashboard), perfil de usuario y calendario.

## 2. Con quién trabajas
- El usuario principal es **Sam**, aprendiz de desarrollo de software. Sabe HTML, CSS, JavaScript, Python, SQL, PostgreSQL, FastAPI y React, pero **todavía está aprendiendo**: no des por sentado que conoce un concepto.
- Habla en **español**. Responde siempre en español.
- Trabaja en **Linux y Windows** (PC distintas). No asumas el sistema operativo; si un comando cambia según el SO, indícalo.

## 3. Stack tecnológico
| Capa | Tecnología |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Base de datos | **PostgreSQL** (NO MySQL) |
| Frontend | React + TypeScript + Vite |
| Autenticación | JWT |
| Herramientas | Swagger UI (`/docs`), DBeaver, Git/GitHub |

## 4. Estructura del proyecto
```
Acadex/
├── backend/app/
│   ├── api/v1/endpoints/   # rutas (tareas, grupos, usuarios, perfiles, categorias, panel, sesiones_cronometro...)
│   ├── config/  core/  db/  dependencies/  middlewares/
│   ├── models/             # tablas (SQLAlchemy)
│   ├── schemas/            # validación de entrada/salida (Pydantic)
│   ├── repositories/       # acceso a la BD
│   ├── services/           # lógica de negocio
│   └── main.py
├── database/scripts/acadex.sql   # FUENTE DE VERDAD del esquema
├── docs/                   # DESIGN.md, GUIA_FRONTEND.md
│   ├── RF/                 # requisitos funcionales (1 archivo por RF, con historia y escenarios)
│   └── RNF/                # requisitos no funcionales (1 archivo por RNF, por categoría)
├── README.md  AGENTS.md  memory.md  database.md   # raíz del repo
└── frontend/src/
    ├── components/  contexts/  hooks/  layouts/  pages/
    ├── router/  services/  store/  styles/  types/  utils/
```

## 5. Archivos de contexto (léelos según la tarea)
- `memory.md` → estado actual de la app (qué está hecho, qué falta, decisiones). **Léelo al empezar cada sesión.**
- `database.md` → esquema de la BD y reglas de negocio. **Léelo antes de tocar modelos, SQL o endpoints que usen la BD.**
- Si `database.md` y `database/scripts/acadex.sql` no coinciden, **gana `acadex.sql`**.
- `docs/RF/RF-0XX.md` → cada requisito funcional con su historia de usuario y sus escenarios (Dado/Cuando/Entonces). **Antes de implementar una función, lee su RF**: los escenarios son los criterios de aceptación. El índice está en `docs/RF/README.md`.
- `docs/RNF/` → requisitos no funcionales (seguridad, desempeño, usabilidad...). Consúltalos cuando una tarea toque esos temas.
- `frontend/AGENTS.md` → reglas extra del frontend. **Léelo antes de cualquier tarea de interfaz.**
- `README.md` es para personas que visitan el repo. Si contradice a este archivo o a `database.md`, **mandan estos últimos**.

## 6. Convenciones de código
**Backend**
- Respeta la arquitectura por capas: `endpoint → service → repository → model`. Los endpoints no hablan directo con la BD y la lógica de negocio va en `services/`.
- Cada módulo nuevo lleva sus propios archivos en cada capa (model, schema, repository, service, endpoint) y su router se registra donde se agrupan los routers.
- Nombres de tablas, campos y variables del dominio en **español** (ej. `id_usuario`, `fecha_entrega`).
- Los errores se devuelven como `HTTPException` con códigos HTTP correctos.

**Frontend**
- CSS normal (archivos `.css`) dentro de `src/styles/`. **No usar Tailwind, shadcn ni sintaxis de Next.js.**
- Los colores y el estilo salen de las variables de `pixel-theme.css` (estilo pixel art, tema oscuro). No inventes colores sueltos.
- Las llamadas a la API van en `src/services/`, los tipos en `src/types/`, las páginas en `src/pages/` y los componentes en `src/components/`.
- Las rutas protegidas van dentro de `AppLayout` en el router.

## 7. Reglas de negocio que nunca debes romper
- Una tarea pertenece a **exactamente uno** entre `id_usuario` o `id_grupo` (nunca ambos, nunca ninguno). Es el constraint `chk_tarea_owner`.
- Acciones solo del líder de grupo: expulsar, eliminar grupo, crear tareas grupales. El líder no puede salir de su propio grupo.
- Desde el Perfil **no** se puede cambiar correo ni contraseña.
- El acceso es **solo con correo y contraseña** (no hay acceso con Google; fue descartado por el equipo).
- Panel de líder: solo el líder del grupo puede abrirlo (RF-053). La ruta `/admin`: solo usuarios con `es_admin` (RF-058).
- El frontend **no es seguridad**: toda validación de permisos va en el backend, aunque el botón o el enlace estén ocultos en la interfaz.

## 8. Cómo debes comportarte
1. **Antes de escribir código, explica brevemente el plan** y qué archivos vas a tocar.
2. **Cada archivo de código nuevo o modificado lleva arriba un comentario con su ruta exacta** (ej. `# Ruta: backend/app/services/grupo_service.py`).
3. **Explica qué hace cada parte o archivo** que entregues. Si el concepto es técnico, usa una **analogía sencilla de la vida diaria** que Sam pueda reutilizar para explicárselo a otra persona.
4. Haz cambios **pequeños y por pasos**. Una tarea a la vez; no refactorices cosas que no se pidieron.
5. Si algo es ambiguo, **pregunta** en vez de inventar. Si cambias el esquema de la BD, avisa que hay que actualizar `acadex.sql`.
6. No inventes endpoints, tablas ni campos: revisa primero el código real.
7. No hagas `git commit` ni `git push` salvo que Sam lo pida.
8. **Al terminar cada tarea, actualiza `memory.md`** (qué se hizo, qué quedó pendiente, decisiones nuevas). Mantenlo corto: máximo una o dos líneas por cambio.

## 9. Git, commits y secretos
- **Ramas:** el trabajo parte de `develop` (confirmar con el equipo). Cada tarea va en su propia rama: `feature/nombre`, `fix/nombre` o `docs/nombre`. Todo entra por **Pull Request**; nunca se hace push directo a `main`. Una tarea = un Issue = una rama.
- **Commits** (solo cuando Sam lo pida), con prefijo: `feat:` funcionalidad nueva, `fix:` corrección, `docs:` documentación, `refactor:`, `test:`, `chore:`. Ejemplo: `feat: agregar endpoint para listar integrantes`.
- **Secretos:** nunca escribas contraseñas, tokens ni claves de API (incluida la de Gemini) dentro del código. Van en `.env`, que no se sube.
- **No se versiona:** `venv/`, `__pycache__/`, `.env`, `.vscode/`, `*.pyc`, `node_modules/` y `backend/uploads/`.

## 10. Comandos útiles (verificar que coincidan con el proyecto)
```bash
# Backend (desde backend/)
python -m venv venv                # solo la primera vez
source venv/bin/activate           # Linux/Mac   |   Windows: venv\Scripts\activate
pip install -r requirements.txt    # solo la primera vez
uvicorn app.main:app --reload      # API en http://localhost:8000  |  Swagger en /docs  |  Redoc en /redoc

# Frontend (desde frontend/)
npm install
npm run dev                         # App en http://localhost:5173
```

## 11. Fuera de alcance por ahora
- Subagentes y skills: aún no se implementan.
- Cambio de idioma en el perfil: idea para más adelante.
