import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)

carpeta = 'static/images'

for archivo in os.listdir(carpeta):
    ruta = os.path.join(carpeta, archivo)
    nombre = os.path.splitext(archivo)[0]
    print(f'Subiendo {archivo}...')
    resultado = cloudinary.uploader.upload(
        ruta,
        public_id=f'colmercia/{nombre}',
        overwrite=True
    )
    print(f'  ✓ {resultado["secure_url"]}')

print('¡Listo!')