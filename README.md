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

