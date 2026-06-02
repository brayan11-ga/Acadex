# 🎨 Guía de Desarrollo Frontend - Acadex

## Objetivo

Esta guía define los estándares de desarrollo frontend para el proyecto Acadex.

Todos los integrantes deben seguir estas reglas para garantizar consistencia visual, facilidad de mantenimiento e integración del código.

---

# 📂 Estructura de Carpetas

Toda la interfaz debe desarrollarse dentro de:

```text
src/frontend/
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── logo/
│
├── css/
│   ├── global.css
│   ├── login.css
│   ├── register.css
│   ├── dashboard.css
│   └── profile.css
│
├── js/
│
├── index.html
├── login.html
├── register.html
├── dashboard.html
└── profile.html
```

---

---

# 🎨 Paleta de Colores Oficial

Todos los desarrolladores deben utilizar exclusivamente las variables definidas en:

```css
global.css
```

Variables principales:

```css
:root {

    --background: #10131a;

    --surface: #1d2027;

    --surface-high: #272a31;

    --primary: #adc6ff;

    --primary-container: #4d8eff;

    --secondary: #4edea3;

    --text: #e1e2ec;

    --text-muted: #c2c6d6;

    --outline: #424754;
}
```

❌ No crear colores nuevos.

❌ No utilizar colores aleatorios.

---

# ✍️ Tipografía Oficial

## Títulos

```css
font-family: 'Manrope', sans-serif;
```

## Texto

```css
font-family: 'Inter', sans-serif;
```

---

# 📏 Espaciado

Mantener suficiente espacio entre elementos.

Recomendaciones:

| Elemento | Espaciado |
|-----------|-----------|
| Componentes pequeños | 8px |
| Componentes normales | 16px |
| Secciones | 24px |
| Bloques principales | 40px |

Evitar interfaces saturadas.

---

# 🔲 Bordes

| Elemento | Radio |
|-----------|-----------|
| Inputs | 8px |
| Cards | 12px |
| Botones | 16px |

---

# 🧩 Componentes Compartidos

Antes de crear estilos nuevos, revisar si ya existen en:

```text
css/global.css
```

Ejemplos:

- Botones
- Cards
- Contenedores
- Variables
- Tipografía

No duplicar estilos.

---

# 🖼️ Recursos Gráficos

## Logos

Ubicación:

```text
assets/logo/
```

Ejemplo:

```text
logo.png
logo-white.png
logo-icon.png
```

---

## Iconos

Ubicación:

```text
assets/icons/
```

Formato recomendado:

```text
SVG
```

Ejemplos:

```text
task.svg
user.svg
group.svg
notification.svg
```

---

## Imágenes

Ubicación:

```text
assets/images/
```

Ejemplos:

```text
hero.png
dashboard-preview.png
empty-state.png
```

---

# 📄 Páginas Asignadas

## Landing Page

Archivos:

```text
index.html
global.css
```

Responsable:

Equipo base del proyecto.

---

## Login

Archivos:

```text
login.html
login.css
```

Debe incluir:

- Logo Acadex
- Correo
- Contraseña
- Botón iniciar sesión
- Recuperar contraseña
- Enlace a registro

---

## Registro

Archivos:

```text
register.html
register.css
```

Debe incluir:

- Nombre
- Correo
- Contraseña
- Confirmar contraseña
- Botón registrarse
- Enlace a iniciar sesión

---

## Dashboard

Archivos:

```text
dashboard.html
dashboard.css
```

Debe incluir:

- Sidebar
- Tareas
- Estadísticas
- Grupos
- Notificaciones

Por ahora únicamente diseño visual.

---

# 📱 Diseño Responsive

Toda página debe funcionar en:

## Desktop

```text
≥ 1024px
```

## Tablet

```text
768px - 1023px
```

## Móvil

```text
≤ 767px
```

Utilizar Media Queries.

---

# 🧹 Buenas Prácticas

## HTML

- Utilizar etiquetas semánticas.
- Mantener indentación correcta.
- Nombrar clases claramente.

Ejemplo:

```html
<section class="dashboard">
```

No:

```html
<section class="caja1">
```

---

## CSS

Utilizar nombres descriptivos.

Ejemplo:

```css
.task-card
.dashboard-sidebar
.user-profile
```

No:

```css
.box
.card2
.contenedor
```

---

# 🌳 Flujo de Trabajo Git

Antes de comenzar:

```bash
git checkout develop
git pull origin develop
```

Crear rama:

```bash
git checkout -b feature/login
```

Ejemplos:

```bash
git checkout -b feature/register
git checkout -b feature/dashboard
```

Guardar cambios:

```bash
git add .
git commit -m "feat: crear interfaz login"
```

Subir cambios:

```bash
git push origin feature/login
```

---

# 🔀 Pull Requests

Todo cambio debe pasar por Pull Request.

No hacer push directo a:

```text
main
```

Destino de los Pull Request:

```text
develop
```

---

# 🚫 No Subir al Repositorio

Nunca subir:

```text
venv/
.env
__pycache__/
.vscode/
```

Ni tampoco:

- Contraseñas
- Tokens
- Claves API
- Variables de entorno

---

# ✅ Checklist Antes de Subir Cambios

- [ ] Código funcionando.
- [ ] Diseño responsive.
- [ ] Uso de variables de global.css.
- [ ] Sin errores en consola.
- [ ] Commit semántico.
- [ ] Rama feature creada correctamente.
- [ ] Pull Request realizado.

---

# Acadex Frontend Standards

Todos los desarrolladores deben seguir esta guía para mantener una interfaz consistente y profesional en todo el sistema.
