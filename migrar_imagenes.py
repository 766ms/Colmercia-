import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import cloudinary.uploader
from tienda.models import Producto, BannerLanding, Usuario
from django.conf import settings

def subir_imagen(ruta_relativa, carpeta):
    ruta_absoluta = settings.MEDIA_ROOT / ruta_relativa
    if not ruta_absoluta.exists():
        print(f"  ⚠️  No existe: {ruta_absoluta}")
        return None
    resultado = cloudinary.uploader.upload(str(ruta_absoluta), folder=carpeta)
    return resultado['public_id']

def migrar(modelo, campo_imagen, carpeta, label):
    registros = modelo.objects.exclude(**{campo_imagen: ''})
    print(f"\n📦 Migrando {registros.count()} {label}...")
    ok, fail = 0, 0
    for obj in registros:
        imagen_actual = getattr(obj, campo_imagen)
        if 'cloudinary' in str(imagen_actual) or str(imagen_actual).startswith('http'):
            print(f"  ✅ Ya en Cloudinary: {imagen_actual}")
            ok += 1
            continue
        print(f"  ⬆️  Subiendo: {imagen_actual}")
        public_id = subir_imagen(imagen_actual.name, carpeta)
        if public_id:
            setattr(obj, campo_imagen, public_id)
            obj.save(update_fields=[campo_imagen])
            ok += 1
        else:
            fail += 1
    print(f"  ✔ {ok} subidos | ✘ {fail} fallidos")

migrar(Producto,      'imagen',      'productos', 'productos')
migrar(BannerLanding, 'imagen',      'banners',   'banners')

# Usuarios por separado para manejar None
registros = Usuario.objects.exclude(foto_perfil='').exclude(foto_perfil=None)
print(f"\n📦 Migrando {registros.count()} usuarios...")
ok, fail = 0, 0
for obj in registros:
    imagen_actual = obj.foto_perfil
    if not imagen_actual or not imagen_actual.name:
        continue
    if 'cloudinary' in str(imagen_actual) or str(imagen_actual).startswith('http'):
        print(f"  ✅ Ya en Cloudinary: {imagen_actual}")
        ok += 1
        continue
    ruta_absoluta = settings.MEDIA_ROOT / imagen_actual.name
    if not Path(ruta_absoluta).exists():
        print(f"  ⚠️  No existe: {ruta_absoluta}")
        fail += 1
        continue
    print(f"  ⬆️  Subiendo: {imagen_actual.name}")
    resultado = cloudinary.uploader.upload(str(ruta_absoluta), folder='perfiles')
    obj.foto_perfil = resultado['public_id']
    obj.save(update_fields=['foto_perfil'])
    ok += 1

print(f"  ✔ {ok} subidos | ✘ {fail} fallidos")
print("\n🎉 Migración completa")