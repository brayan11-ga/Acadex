# 🎓 Acadex

Sistema inteligente para la gestión de tareas académicas y colaborativas.

---

## 📖 Descripción del Proyecto

Acadex es una plataforma web diseñada para facilitar la organización, planificación y seguimiento de tareas académicas y actividades colaborativas.

El sistema permitirá a los usuarios gestionar tareas, crear grupos de trabajo, administrar integrantes, registrar el tiempo invertido en actividades, compartir recursos y visualizar el progreso de los proyectos mediante herramientas de seguimiento y priorización inteligente. Además, incorpora funcionalidades potenciadas por Inteligencia Artificial para el análisis y organización de contenidos.

---

## 🎯 Objetivo General

Desarrollar una aplicación web que permita gestionar de forma eficiente tareas académicas y actividades colaborativas, optimizando la organización del trabajo individual y en equipo.

---

## 🚀 Funcionalidades Principales

### Gestión de Usuarios

- Registro e inicio de sesión seguro (JWT).
- Recuperación de contraseña.
- Gestión de perfil de usuario.

### Gestión de Tareas y Productividad

- Creación, edición y eliminación de tareas.
- Cambio de estado y priorización de tareas.
- Cronómetro y registro de tiempo invertido.
- Estadísticas de avance y rendimiento.

### Gestión de Grupos

- Creación de grupos de trabajo.
- Códigos de acceso para unirse a grupos.
- Administración de integrantes (expulsar, abandonar).

### Integración de Inteligencia Artificial

- Procesamiento de documentos (PDF).
- Asistencia inteligente con Google Gemini.

---

## 🛠️ Tecnologías Utilizadas

### Frontend

- React 19
- TypeScript
- Vite
- Redux Toolkit (Gestión de estado global)
- React Router DOM
- Bootstrap 5 y CSS3
- Chart.js (Gráficos)

### Backend

- Python
- FastAPI
- SQLAlchemy (ORM)
- Pydantic
- JWT (Autenticación)
- Google Generative AI (Gemini)

### Base de Datos

- PostgreSQL

### Control de Versiones y Gestión

- Git y GitHub
- GitHub Projects y Issues

---

## 📂 Estructura del Proyecto

```text
Acadex/
│
├── backend/                  # API RESTful y lógica de negocio
│   ├── app/                  # Código principal (controladores, modelos, servicios)
│   ├── requirements.txt      # Dependencias de Python
│   └── .env.example          # Variables de entorno de ejemplo
│
├── frontend/                 # Interfaz de usuario (SPA)
│   ├── src/                  # Código fuente (componentes, vistas, servicios)
│   ├── package.json          # Dependencias de Node.js
│   └── vite.config.mts       # Configuración de Vite
│
├── database/                 # Scripts y recursos de base de datos
├── docs/                     # Documentación técnica
├── STRUCTURE.md              # Detalle profundo de la arquitectura
└── README.md                 # Información general del proyecto
```

Para más detalles sobre la arquitectura interna de cada directorio, consulta el archivo [`STRUCTURE.md`](./STRUCTURE.md).

---

## ⚙️ Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/brayan11-ga/Acadex.git
cd Acadex
```

### 2. Configuración del Backend

1. Ingresar al directorio del backend:
   ```bash
   cd backend
   ```
2. Crear y activar un entorno virtual:
   - **Windows:** `python -m venv .venv` y luego `.venv\Scripts\activate`
   - **Linux/Mac:** `python -m venv .venv` y luego `source .venv/bin/activate`
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configurar las variables de entorno:
   Copiar `.env.example` a `.env` y ajustar los valores (base de datos, clave secreta JWT, API Key de Gemini).
5. Ejecutar el servidor de desarrollo:
   ```bash
   uvicorn app.main:app --reload
   ```
   *La API estará disponible en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva en `http://127.0.0.1:8000/docs`.*

### 3. Configuración del Frontend

1. Ingresar al directorio del frontend:
   ```bash
   cd ../frontend
   ```
2. Instalar las dependencias:
   ```bash
   npm install
   ```
3. Ejecutar el servidor de desarrollo:
   ```bash
   npm run dev
   ```
   *La aplicación estará disponible en la URL que indique la consola (usualmente `http://localhost:5173`).*

---

## 🌳 Flujo de Trabajo con Git

### Actualizar rama develop

```bash
git checkout develop
git pull origin develop
```

### Crear una rama para una nueva funcionalidad

```bash
git checkout -b feature/nombre-funcionalidad
```

Ejemplos:

```bash
git checkout -b feature/integracion-gemini
git checkout -b feature/dashboard-estadisticas
```

### Guardar y subir cambios

```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-funcionalidad
```

### Crear Pull Request

Todos los cambios deben integrarse mediante Pull Request antes de fusionarse con la rama principal.

---

## 📝 Convención de Commits

| Prefijo | Descripción |
|----------|----------|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de errores |
| `docs:` | Documentación |
| `refactor:` | Refactorización de código existente |
| `test:` | Creación o actualización de pruebas |
| `chore:` | Mantenimiento, actualizaciones de dependencias |

---

## 🚫 Archivos que No Deben Subirse

Asegúrate de no versionar archivos sensibles o generados localmente:

- Carpetas de dependencias: `node_modules/`, `.venv/`, `__pycache__/`
- Archivos de entorno: `.env`
- Configuraciones locales de IDEs: `.vscode/`, `.idea/`
- Archivos compilados: `dist/`, `*.pyc`

Nunca subir: Contraseñas, tokens, claves de API, ni variables de entorno productivas.

---

## 👥 Equipo de Desarrollo

Proyecto académico desarrollado por el equipo Acadex dentro del proceso de formación en Análisis y Desarrollo de Software.

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia MIT.
