# Colmercia

Colmercia es una tienda en línea construida con Django (interfaz en español) que ofrece catálogo de productos, carrito de compras y gestión de imágenes en la nube (Cloudinary). Está pensada para desplegarse tanto en desarrollo con SQLite como en producción usando PostgreSQL y Gunicorn/WhiteNoise para servir estáticos.

## Captura rápida — ¿Qué hace?
- Sitio ecommerce simple con app principal `tienda` (usuarios, productos, vistas, formularios).
- Gestión de imágenes mediante Cloudinary.
- Carrito de compras independiente en `carrito/` (módulo JavaScript con package.json).
- Scripts auxiliares para subir/migrar imágenes: `subir_imagenes.py`, `migrar_imagenes.py`.

---

## Stack
- Lenguajes principales: Python (Django), HTML, CSS, JavaScript
- Framework: Django 6.0
- Bibliotecas notables:
  - cloudinary + django-cloudinary-storage (almacenamiento de media)
  - whitenoise (servir archivos estáticos en producción)
  - djangorestframework (API)
  - psycopg2-binary (Postgres)
  - pytest & pytest-django (tests)

---

## Estructura del proyecto (resumen)

```
manage.py                # Entrypoint de Django
config/                  # Configuración del proyecto (settings, urls, wsgi, asgi)
tienda/                  # App principal: modelos, vistas, formularios, templates
  admin.py
  models.py
  views.py
  urls.py
  forms.py
  templates/             # plantillas HTML de la app
carrito/                 # módulo de carrito (JS) con package.json
static/                  # CSS y JS públicos (style.css, app.js)
media/                   # imágenes subidas (vacío en repo)
migrar_imagenes.py       # script para migrar imágenes (local -> Cloudinary u otro)
subir_imagenes.py        # script para subir imágenes
requirements.txt         # dependencias
db.sqlite3               # base de datos por defecto (SQLite) - archivo incluido en repo
pytest.ini, conftest.py  # configuración de pruebas
```

Cómo encaja: `config` define las URLs y settings; `tienda` es la app Django que maneja la lógica de negocio y las vistas; `static` contiene los assets servidos por WhiteNoise en producción; `carrito` contiene lógica del cliente para manejar el carrito.

---

## Requisitos
- Python 3.11+ (recomendado)
- Node.js/npm (solo si vas a trabajar en `carrito`)
- Entorno virtual (recomendado)
- Credenciales Cloudinary para almacenamiento de media (si usas Cloudinary en producción)
- (Opcional) PostgreSQL si vas a usar `DATABASE_URL` en producción

Variables de entorno importantes (.env)
- SECRET_KEY (obligatorio)
- DEBUG (True/False)
- DATABASE_URL (opcional, si no existe usa SQLite por defecto)
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

---

## Instalación y ejecución (desarrollo)

1. Clona el repositorio y crea un entorno virtual:
```bash
git clone https://github.com/766ms/Colmercia-.git
cd Colmercia-
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea un archivo `.env` en la raíz con al menos:
```
SECRET_KEY=tu_secret_key
DEBUG=True
# Opcional:
# DATABASE_URL=postgres://user:pass@host:port/dbname
# CLOUDINARY_CLOUD_NAME=...
# CLOUDINARY_API_KEY=...
# CLOUDINARY_API_SECRET=...
```

3. Migraciones y datos iniciales:
```bash
python manage.py migrate
python manage.py createsuperuser   # (opcional) crea un admin
```

4. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
# Abre http://127.0.0.1:8000
```

5. Si trabajas en la parte de carrito (JS):
```bash
cd carrito
npm install
# si hay scripts definidos en package.json:
npm run build   # o npm run dev (si aplica)
```

---

## Ejecutar en producción (ejemplo mínimo)
- Recomendado: usar Gunicorn + WhiteNoise para archivos estáticos; Cloudinary para media.

Ejemplo:
```bash
# instalar (en virtualenv)
pip install -r requirements.txt
# exportar variables de entorno (SECRET_KEY, DEBUG=False, DATABASE_URL, CLOUDINARY_*)
python manage.py migrate
python manage.py collectstatic --noinput
# ejecutar con gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Asegúrate de configurar ALLOWED_HOSTS en `.env` o en settings antes de desplegar.

---

## Base de datos
- Por defecto el proyecto usa SQLite (archivo db.sqlite3 incluido).
- Si `DATABASE_URL` está presente en el .env, se configura PostgreSQL automáticamente.
- `config/settings.py` contiene la lógica de conexión (parseo de DATABASE_URL).

---

## Tests
Este proyecto incluye configuración para pytest / pytest-django.
Ejecuta:
```bash
pytest
```

---

## Scripts auxiliares
- migrar_imagenes.py — script para migrar imágenes (revisar y ejecutar con cuidado).
- subir_imagenes.py — sube imágenes a Cloudinary (ver variables de entorno y comentario en el script).

Revisa los scripts antes de ejecutarlos para entender los paths y la operación que realizan.

---

## Tareas pendientes / recomendaciones
- El repo contiene el archivo `db.sqlite3` — normalmente no se suben bases de datos al control de versiones; considera removerlo y añadirlo a .gitignore si corresponde.
- Añadir un archivo LICENSE (no se encontró licencia en el repo).
- Incluir un README.md (este) en la raíz del repo y un CONTRIBUTING.md para guiar contribuciones.
- Añadir CI (p. ej. GitHub Actions) para ejecutar tests automáticamente.
- Revisar y limpiar `node_modules` en `carrito` (no es recomendable subir node_modules al repo).

---

## Cómo contribuir
1. Haz fork del repo y crea una rama feature/bugfix.
2. Añade tests para cambios funcionales.
3. Abre un Pull Request describiendo los cambios y por qué.
4. Mantén el estilo de código existente (PEP8 para Python).

---

## Contacto
Si necesitas ayuda para configurar el entorno o para que cree el README directamente en el repositorio, dímelo y te lo preparo.
