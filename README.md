# 🎓 Acadex

Sistema inteligente para la gestión de tareas académicas y colaborativas.

---

## 📖 Descripción del Proyecto

Acadex es una plataforma web diseñada para facilitar la organización, planificación y seguimiento de tareas académicas y actividades colaborativas.

El sistema permitirá a los usuarios gestionar tareas, crear grupos de trabajo, administrar integrantes, registrar el tiempo invertido en actividades, compartir recursos y visualizar el progreso de los proyectos mediante herramientas de seguimiento y priorización inteligente.

---

## 🎯 Objetivo General

Desarrollar una aplicación web que permita gestionar de forma eficiente tareas académicas y actividades colaborativas, optimizando la organización del trabajo individual y en equipo.

---

## 🚀 Funcionalidades Principales

### Gestión de Usuarios

- Registro de usuarios.
- Inicio de sesión.
- Recuperación de contraseña.
- Gestión de perfil.

### Gestión de Tareas

- Crear tareas.
- Editar tareas.
- Eliminar tareas.
- Cambiar estado de tareas.
- Buscar tareas.
- Filtrar tareas.
- Adjuntar archivos.

### Gestión de Grupos

- Crear grupos de trabajo.
- Generar códigos de acceso.
- Unirse a grupos mediante código.
- Gestionar integrantes.
- Expulsar integrantes.
- Abandonar grupos.

### Seguimiento y Productividad

- Registro de tiempo invertido.
- Seguimiento de progreso.
- Priorización inteligente de tareas.
- Sistema de notificaciones.
- Estadísticas de avance.

---

## 🛠️ Tecnologías Utilizadas

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- FastAPI

### Base de Datos

- MySQL

### Control de Versiones

- Git
- GitHub

### Gestión del Proyecto

- GitHub Projects
- GitHub Issues
- Pull Requests

---

## 📂 Estructura del Proyecto

```text
Acadex/
│
├── .github/
├── docs/
├── src/
│   ├── controllers/
│   ├── database/
│   ├── frontend/
│   │   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── index.html
│   │
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── tests/
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## 📌 Descripción de Carpetas

### `.github/`

Contiene configuraciones relacionadas con GitHub, automatizaciones y flujos de trabajo.

### `docs/`

Documentación técnica y funcional del proyecto.

### `src/`

Contiene todo el código fuente de la aplicación.

### `src/frontend/`

Contiene la interfaz de usuario desarrollada con HTML, CSS y JavaScript.

### `src/controllers/`

Controladores encargados de gestionar las solicitudes realizadas por el usuario.

### `src/routes/`

Definición de rutas y endpoints de la API REST.

### `src/models/`

Modelos que representan las entidades del sistema.

### `src/schemas/`

Esquemas de validación de datos mediante Pydantic.

### `src/services/`

Contiene la lógica de negocio del sistema.

### `src/database/`

Configuración de conexión y acceso a la base de datos.

### `src/utils/`

Funciones auxiliares reutilizables.

### `tests/`

Pruebas unitarias e integración.

---

## ⚙️ Instalación del Proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/brayan11-ga/Acadex.git
```

### 2. Ingresar al proyecto

```bash
cd Acadex
```

### 3. Crear entorno virtual

```bash
python -m venv venv
```

### 4. Activar entorno virtual

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6. Ejecutar el servidor

```bash
uvicorn src.main:app --reload
```

### 7. Acceder a la documentación de la API

Swagger:

```text
http://127.0.0.1:8000/docs
```

Redoc:

```text
http://127.0.0.1:8000/redoc
```

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
git checkout -b feature/base-datos
git checkout -b feature/login
git checkout -b feature/crud-tareas
```

### Guardar cambios

```bash
git add .
git commit -m "feat: descripción del cambio"
```

### Subir cambios

```bash
git push origin nombre-rama
```

### Crear Pull Request

Todos los cambios deben integrarse mediante Pull Request antes de fusionarse con la rama principal.

---

## 📝 Convención de Commits

| Prefijo | Descripción |
|----------|----------|
| feat: | Nueva funcionalidad |
| fix: | Corrección de errores |
| docs: | Documentación |
| refactor: | Refactorización |
| test: | Pruebas |
| chore: | Mantenimiento |

### Ejemplos

```bash
git commit -m "feat: crear módulo de autenticación"
git commit -m "fix: corregir validación de usuarios"
git commit -m "docs: actualizar README"
```

---

## 🚫 Archivos que No Deben Subirse

Estos archivos están excluidos mediante `.gitignore`:

```text
venv/
__pycache__/
.env
.vscode/
*.pyc
```

Nunca subir:

- Contraseñas.
- Tokens.
- Claves API.
- Variables de entorno.

---

## 📊 Gestión del Proyecto

El seguimiento del desarrollo se realiza mediante GitHub Projects.

### Flujo de trabajo

```text
Product Backlog
        ↓
Sprint Backlog / Todo
        ↓
In Progress
        ↓
In Review / QA
        ↓
Done
```

Cada tarea debe estar asociada a un Issue y desarrollarse en una rama independiente.

---

## 📅 Estado Actual del Proyecto

### Fase Actual

Diseño y construcción de la base de datos.

### Actividades en Desarrollo

- Definición de cardinalidades.
- Normalización del modelo entidad-relación.
- Construcción del modelo relacional.
- Elaboración del diccionario de datos.
- Creación del primer script SQL.

---

## 👥 Equipo de Desarrollo

Proyecto académico desarrollado por el equipo Acadex dentro del proceso de formación en Análisis y Desarrollo de Software.

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia MIT.