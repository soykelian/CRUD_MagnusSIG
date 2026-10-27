# Magnus SIG

Sistema web integrado de gestión para equipos de protección personal (EPP), seguridad y salud en el trabajo (SG-SST) y dotación laboral. Desarrollado con Django (arquitectura MVT) en el backend y persistencia directa sobre **MySQL 8.0** (base de datos `magnussig_inventario`), con soporte opcional de fallback a SQLite para entornos de desarrollo aislados.

---

## Descripción del sistema

Magnus SIG permite administrar el catálogo de productos y equipos de protección, controlar existencias físicas en bodega con ubicación detallada, gestionar compras a proveedores, despachos a clientes, catálogo de servicios de seguridad laboral (SG-SST) y mantener una trazabilidad atómica de todas las entradas y salidas.

El dashboard, las alertas de stock bajo y el gráfico de tendencia se calculan en tiempo real a partir de las transacciones registradas en la base de datos.

### Módulos del sistema

| Módulo | Ruta | Descripción |
| --- | --- | --- |
| **Dashboard** | `/dashboard/` | Métricas clave: valor total del inventario, productos bajo stock mínimo, compras, ventas y gráfica de tendencia de movimientos. |
| **Inventario** | `/` | Tabla operativa de existencias actuales, ubicación física en bodega y alertas de abastecimiento. |
| **Catálogo de Productos** | `/productos/` | Catálogo comercial con búsqueda en tiempo real, filtros por categoría y fichas técnicas. |
| **Nuevo / Editar Producto** | `/productos/nuevo/` | Alta y modificación con código/SKU, categoría, proveedor, precios de compra/venta, unidad de medida y stock inicial. |
| **Categorías** | `/categorias/` | Clasificación de productos (Camillas, Botiquines, Extintores, EPP, Dotaciones, Señalización, Emergencias). |
| **Servicios SG-SST** | `/servicios/` | Gestión de servicios de consultoría, capacitación, inspecciones y medicina ocupacional para clientes. |
| **Movimientos** | `/movimientos/` | Registro cronológico inmutable de entradas, salidas y ajustes con responsable y documento soporte. |
| **Entradas (Compras)** | `/movimientos/entrada/` | Recepción de mercancía de proveedores: incrementa automáticamente el inventario y genera trazabilidad. |
| **Salidas (Despachos)** | `/movimientos/salida/` | Despacho a clientes o áreas internas: valida existencias disponibles y descuenta inventario. |
| **Proveedores** | `/proveedores/` | Directorio de proveedores con documento (NIT/CC), contacto comercial, dirección y teléfono. |
| **Clientes** | `/clientes/` | Directorio de empresas y clientes vinculados con despachos y contratos de servicios. |
| **Reportes** | `/reportes/` | Métricas de rendimiento, desglose de inventario y exportación de datos en formato CSV. |
| **Configuración** | `/configuracion/` | Parámetros globales: nombre de la empresa, moneda y umbral configurable de stock mínimo. |
| **Panel Administrativo** | `/admin/` | Gestión avanzada de usuarios, grupos, permisos y auditoría interna de Django. |

---

## Modelo de Base de Datos (MySQL)

El sistema se acopla a la base de datos relacional `magnussig_inventario` compuesta por las siguientes tablas principales:

```
├── categorias               # Familias de productos
├── productos                # Ficha técnica, SKU, precios y estado
├── inventario               # Existencias físicas actuales y ubicación por producto
├── movimientos_inventario   # Trazabilidad atómica (tipo, cantidad, usuario, fecha)
├── proveedores              # Información fiscal y comercial de proveedores
├── clientes                 # Información fiscal y comercial de clientes
├── compras                  # Cabecera de órdenes de compra
├── detalle_compra           # Líneas de producto y costo unitario de compra
├── ventas                   # Cabecera de facturas y despachos
├── detalle_venta            # Líneas de producto despachadas
├── tipos_servicio           # Tipos de servicios SG-SST (consultoría, capacitación, etc.)
├── servicios                # Catálogo de servicios contratados por clientes
├── usuarios                 # Registro de personal y roles de auditoría
└── configuracion_inventario # Preferencias del sistema (nombre de empresa, moneda)
```

---

## Stack tecnológico

| Área | Tecnología | Uso en Magnus SIG |
| --- | --- | --- |
| **Backend** | Python 3 y Django 6.1 | Controladores, autenticación, validaciones, transacciones atómicas (`transaction.atomic`). |
| **Base de datos** | MySQL 8.0 (con conector PyMySQL) | Motor relacional principal. Soporta fallback local a SQLite vía `DJANGO_USE_SQLITE`. |
| **Arquitectura** | Django MVT + Servicios | Separación de lógica de dominio en `productos/services/stock.py`. |
| **Frontend y Estilos** | Tailwind CSS 4 y CSS nativo | Interfaz responsiva con paleta corporativa y modo oscuro/claro integrado. |
| **Interacciones** | HTMX | Búsqueda reactiva instantánea y filtrado asíncrono sin recarga de página completa. |
| **Animación y UX** | GSAP, AOS y Lenis | Transiciones fluidas, animaciones al scroll y microinteracciones visuales. |
| **Herramientas de build** | Node.js, npm y esbuild | Compilación de Tailwind CSS y empaquetado de librerías frontend. |

---

## Arquitectura y organización

```text
CRUD_MagnusSIG/
├── .env.example                     # Plantilla de variables de entorno (sin secretos)
├── .gitignore                       # Archivos ignorados por Git (.env, venv, db.sqlite3, etc.)
├── docs/                            # Documentación técnica, manuales y planeación
├── mockups/                         # Diseños de referencia
├── package.json                     # Scripts y dependencias de frontend (Tailwind, GSAP)
├── requirements.txt                 # Dependencias de Python (Django, PyMySQL, Cryptography)
├── README.md                        # Documentación principal del proyecto
└── magnus_sig/
    ├── manage.py                    # CLI de Django
    ├── magnussig_inventario.sql     # Script SQL con estructura y datos base
    ├── magnus_sig/                  # Configuración central
    │   ├── settings.py              # Ajustes de Django, BD y variables de entorno
    │   ├── urls.py                  # Rutas globales del proyecto
    │   └── wsgi.py / asgi.py
    └── productos/                   # Aplicación principal
        ├── admin.py                 # Configuración de Django Admin
        ├── forms.py                 # Formularios validados
        ├── models.py                # Modelos ORM sincronizados con las tablas MySQL
        ├── roles.py                 # Permisos y control de acceso (Admin vs. Vendedor)
        ├── urls.py / views.py       # Vistas y endpoints
        ├── services/stock.py        # Servicios transaccionales de inventario
        ├── templates/productos/     # Plantillas HTML
        └── static/productos/        # Assets compilados (CSS y JS)
```

---

## Instalación y puesta en marcha

Ejecuta todos los comandos desde la **raíz del repositorio** (`CRUD_MagnusSIG`), en una terminal de **PowerShell**.

### 1. Requisitos previos
* **Python 3.12+** instalado.
* **Node.js 18+ (LTS)** y **npm** instalados.
* **MySQL Server 8.0+** instalado y en ejecución (o XAMPP/WAMP con MySQL).

---

### 2. Primera instalación paso a paso

#### Paso A: Frontend (compilación de estilos)
```powershell
npm install
npm run css:build
npm run motion:build
```

#### Paso B: Entorno virtual de Python
```powershell
py -m venv .\venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### Paso C: Configurar credenciales locales (`.env`)
Copia la plantilla `.env.example` para crear tu archivo `.env` personal:
```powershell
copy .env.example .env
```

Abre tu archivo `.env` recién creado y ajusta tus credenciales locales de MySQL:
```env
MYSQL_DATABASE=magnussig_inventario
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña_local_de_mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

> [!IMPORTANT]
> El archivo `.env` está protegido en `.gitignore` y **NUNCA se comparte ni se sube a Git**. Cada desarrollador coloca allí su propia contraseña de MySQL local.

*(Si no dispones de MySQL instalado en tu máquina, puedes descomentar `DJANGO_USE_SQLITE=1` en tu archivo `.env` para trabajar temporalmente con SQLite local).*

#### Paso D: Crear la base de datos en MySQL
En tu gestor de MySQL (Workbench, phpMyAdmin o terminal), crea la base de datos e importa el script inicial:
```powershell
# En la consola de MySQL o PowerShell:
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS magnussig_inventario CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
mysql -u root -p magnussig_inventario < magnus_sig\magnussig_inventario.sql
```

#### Paso E: Migraciones y roles de Django
```powershell
.\venv\Scripts\python.exe .\magnus_sig\manage.py migrate
.\venv\Scripts\python.exe .\magnus_sig\manage.py preparar_roles
```

#### Paso F: Crear tu cuenta administradora local
```powershell
.\venv\Scripts\python.exe .\magnus_sig\manage.py createsuperuser
```
Ingresa el usuario, correo y la contraseña que prefieras. Cada compañero crea su propio administrador en su máquina.

---

### 3. Iniciar el servidor de desarrollo

Para arrancar la aplicación:
```powershell
.\venv\Scripts\python.exe .\magnus_sig\manage.py runserver
```

Abre en tu navegador:
* **Inventario / Inicio:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
* **Inicio de Sesión:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
* **Panel de Administración:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Para detener el servidor, presiona `Ctrl + C` en la terminal.

---

### 4. Actualizaciones posteriores (después de traer cambios de Git)

Cuando hagas `git pull` de la rama del equipo:
```powershell
npm install
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe .\magnus_sig\manage.py migrate
npm run css:build
npm run motion:build
```

---

## Guía de Git y GitHub para el equipo

Esta guía sirve para que cada integrante del equipo mantenga el proyecto actualizado en su computadora y comparta sus cambios de manera limpia y segura sin sobrescribir el trabajo de los demás.

* **Repositorio oficial en GitHub:** [CRUD_MagnusSIG](https://github.com/soykelian/CRUD_MagnusSIG)
* **URL de clonación:** `https://github.com/soykelian/CRUD_MagnusSIG.git`

---

### 1. Primera vez: Clonar y preparar el proyecto

Abre PowerShell en la carpeta donde guardas tus proyectos y ejecuta:

```powershell
git clone https://github.com/soykelian/CRUD_MagnusSIG.git
cd .\CRUD_MagnusSIG
```

Luego sigue los pasos de la sección **Instalación y puesta en marcha** (instalar frontend, crear `venv`, copiar `.env.example` a `.env`, importar base de datos y crear tu superusuario).

---

### 2. Flujo diario: Traer los cambios del equipo antes de programar

Siempre que vayas a comenzar a trabajar o a crear una nueva funcionalidad, asegúrate de tener la rama principal al día:

```powershell
# 1. Comprueba que no tengas cambios pendientes sin guardar
git status

# 2. Pásate a la rama principal
git switch main

# 3. Descarga las últimas actualizaciones que integró el equipo
git pull --ff-only origin main
```

> [!WARNING]
> Nunca uses `git reset --hard` a la ligera si tienes cambios propios sin guardar, ya que borrará tu trabajo local.

---

### 3. Crear una rama para tu tarea específica

**Nunca trabajes ni hagas commits directamente sobre la rama `main`**. Cada integrante debe crear una rama con un nombre descriptivo para la tarea que va a desarrollar:

```powershell
git switch -c feature/nombre-de-la-tarea
```

**Ejemplos de nombres de ramas recomendados:**
* `feature/gestion-ventas`
* `feature/modulo-clientes`
* `fix/calculo-stock-minimo`
* `fix/filtro-fechas-dashboard`
* `docs/actualizacion-manual`

---

### 4. Guardar tus cambios y subir tu rama a GitHub

Cuando termines una parte funcional o un bloque de trabajo:

```powershell
# 1. Revisa qué archivos modificaste o creaste
git status

# 2. Comprueba las líneas exactas que cambiaste
git diff

# 3. Agrega únicamente los archivos correspondientes a tu tarea
git add <archivo1> <archivo2>
# O si todos pertenecen a tu tarea:
git add .

# 4. Confirma el commit con un mensaje claro y descriptivo en español
git commit -m "Agrega validación de stock mínimo en formulario de salidas"

# 5. Sube tu rama a GitHub por primera vez
git push -u origin feature/nombre-de-la-tarea
```

En los siguientes envíos de esa misma rama, solo necesitarás escribir `git push`.

---

### 5. Integrar tu trabajo mediante Pull Request (PR)

1. Entra al repositorio en [CRUD_MagnusSIG en GitHub](https://github.com/soykelian/CRUD_MagnusSIG).
2. Verás una barra avisando que subiste una rama reciente. Haz clic en el botón verde **Compare & pull request**.
3. Escribe un título conciso y explica brevemente qué hace tu cambio y cómo probarlo.
4. Avisa a tus compañeros de equipo para que revisen el código.
5. Una vez aprobado, se integra con **Merge pull request** hacia `main`.

Cuando el Pull Request quede integrado en GitHub, regresa a tu terminal, actualiza tu `main` local y elimina la rama de la tarea terminada:

```powershell
git switch main
git pull --ff-only origin main
git branch -d feature/nombre-de-la-tarea
```

---

### 6. Si necesitas revisar o probar una rama que subió un compañero

Si un compañero subió una rama remota (por ejemplo `feature/reportes-csv`) y necesitas probarla en tu máquina:

```powershell
# 1. Actualiza la lista de ramas remotas
git fetch origin

# 2. Descarga la rama y cámbiate a ella
git switch --track -c feature/reportes-csv origin/feature/reportes-csv
```

Para volver a tu rama principal cuando termines de revisarla:
```powershell
git switch main
git pull --ff-only origin main
```

---

### 7. Qué comparte Git y qué NO comparte

| Elemento | ¿Se comparte en Git? | Explicación |
| --- | :---: | --- |
| **Código Python, HTML, CSS, JS** | ✅ Sí | Se versiona y sincroniza en el repositorio. |
| **Migraciones de Django (`migrations/`)** | ✅ Sí | Permiten que todos tengan el mismo esquema de base de datos. |
| **Script SQL base (`magnussig_inventario.sql`)** | ✅ Sí | Estructura y datos semilla de referencia. |
| **Plantilla de configuración (`.env.example`)** | ✅ Sí | Modelo de variables de entorno sin secretos. |
| **Archivo local `.env`** | ❌ **NUNCA** | Protegido en `.gitignore`. Contiene contraseñas personales. |
| **Registros y datos de tu MySQL local** | ❌ **NO** | Cada equipo corre su base de datos localmente. |
| **Superusuarios y contraseñas de admin** | ❌ **NO** | Cada desarrollador crea su propio admin con `createsuperuser`. |
| **Carpetas `venv/`, `node_modules/`, `db.sqlite3`** | ❌ **NO** | Excluidas por `.gitignore`. Cada entorno las genera localmente. |

---

### Comandos de consulta rápida de Git

```powershell
git status                      # Ver en qué rama estás y cambios pendientes
git branch                      # Listar ramas locales
git fetch origin                # Consultar novedades del repositorio remoto
git pull --ff-only origin main  # Actualizar main local de forma limpia
git diff                        # Ver cambios línea por línea antes de agregarlos
git log --oneline -5            # Ver el historial de los últimos 5 commits
```

---

## Roles y permisos en el sistema

El sistema cuenta con un control de acceso basado en grupos y roles de Django:

* **Administrador (Superusuario):**
  * Acceso total a todos los módulos: Productos, Categorías, Proveedores, Clientes, Servicios SG-SST, Entradas, Salidas, Movimientos, Reportes con exportación CSV y Configuración.
  * Acceso al panel administrativo de Django en `/admin/`.
* **Vendedor:**
  * Acceso operativo enfocado: consulta de existencias en Inventario y Catálogo, registro de clientes y ejecución de despachos (Salidas permitidas).
  * Restricción a módulos de configuración sensible, compras y panel administrativo.

Para asignar un vendedor, ingresa a `/admin/` con una cuenta administradora, crea el usuario y márcalo en el grupo **Vendedor** (dejando desmarcada la opción `is_staff`).

---

## Comandos de diagnóstico y pruebas

* **Comprobar la integridad de la configuración:**
  ```powershell
  .\venv\Scripts\python.exe .\magnus_sig\manage.py check
  ```

* **Ejecutar la suite completa de pruebas unitarias:**
  ```powershell
  .\venv\Scripts\python.exe .\magnus_sig\manage.py test productos
  ```

* **Modo observador de Tailwind (recompila estilos automáticamente al editar plantillas):**
  ```powershell
  npm run css:watch
  ```
