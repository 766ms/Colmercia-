"""
Management command: seed_productos
===================================
Crea las tiendas necesarias (si no existen) y carga todos los productos
que estaban hardcodeados en la landing, asociándolos a su tienda correcta.

Uso:
    python manage.py seed_productos

    # Para limpiar y volver a insertar:
    python manage.py seed_productos --flush

Coloca este archivo en:
    <tu_app>/management/commands/seed_productos.py

Y asegúrate de que exista el __init__.py en:
    <tu_app>/management/__init__.py
    <tu_app>/management/commands/__init__.py
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

# Ajusta el import según el nombre real de tu app
from tienda.models import Producto, Tienda, Usuario


# ─────────────────────────────────────────────────────────────────────────────
#  DATOS: tiendas y sus vendedores asociados
#  Si el vendedor no existe se crea uno de tipo vendedor (ya aprobado).
# ─────────────────────────────────────────────────────────────────────────────
TIENDAS = [
    {
        "nombre":      "Luxedrop Beauty",
        "categoria":   "Maquillaje",
        "ubicacion":   "Bogotá",
        "descripcion": "Tienda de maquillaje premium en Bogotá.",
        "vendedor_email": "luxedrop@colmercia.co",
        "vendedor_nombre": "Luxedrop",
    },
    {
        "nombre":      "Studio BH",
        "categoria":   "Carteras y Bolsos",
        "ubicacion":   "Medellín",
        "descripcion": "Carteras artesanales y accesorios de cuero en Medellín.",
        "vendedor_email": "studiobh@colmercia.co",
        "vendedor_nombre": "StudioBH",
    },
    {
        "nombre":      "Moda Propia",
        "categoria":   "Ropa y Accesorios",
        "ubicacion":   "Cali",
        "descripcion": "Ropa colombiana de diseño propio inspirada en el Pacífico.",
        "vendedor_email": "modapropia@colmercia.co",
        "vendedor_nombre": "ModaPropia",
    },
    {
        "nombre":      "Papel y Arte",
        "categoria":   "Papelería",
        "ubicacion":   "Barranquilla",
        "descripcion": "Papelería creativa y artículos de escritorio artesanales.",
        "vendedor_email": "papelarte@colmercia.co",
        "vendedor_nombre": "PapelArte",
    },
    {
        "nombre":      "TechPyme",
        "categoria":   "Tecnología",
        "ubicacion":   "Bogotá",
        "descripcion": "Accesorios tecnológicos para pymes colombianas.",
        "vendedor_email": "techpyme@colmercia.co",
        "vendedor_nombre": "TechPyme",
    },
    {
        "nombre":      "Paso Firme",
        "categoria":   "Calzado",
        "ubicacion":   "Bucaramanga",
        "descripcion": "Calzado artesanal de cuero genuino hecho en Bucaramanga.",
        "vendedor_email": "pasofirme@colmercia.co",
        "vendedor_nombre": "PasoFirme",
    },
    {
        "nombre":      "Glam Medellín",
        "categoria":   "Maquillaje",
        "ubicacion":   "Medellín",
        "descripcion": "Skincare y maquillaje con ingredientes naturales colombianos.",
        "vendedor_email": "glamedellin@colmercia.co",
        "vendedor_nombre": "GlamMedellin",
    },
    {
        "nombre":      "Essence CO",
        "categoria":   "Regalos",
        "ubicacion":   "Bucaramanga",
        "descripcion": "Perfumería y sets de bienestar artesanales.",
        "vendedor_email": "essenceco@colmercia.co",
        "vendedor_nombre": "EssenceCO",
    },
    {
        "nombre":      "r.e.m. beauty",
        "categoria":   "Maquillaje",
        "ubicacion":   "Bogotá",
        "descripcion": "Maquillaje de edición limitada con empaque biodegradable.",
        "vendedor_email": "rembeauty@colmercia.co",
        "vendedor_nombre": "RemBeauty",
    },
    {
        "nombre":      "Artesanías La Fuente",
        "categoria":   "Artesanías",
        "ubicacion":   "Tuchín",
        "descripcion": "Sombreros vueltiao y artesanías Zenú de Tuchín, Córdoba.",
        "vendedor_email": "lafuente@colmercia.co",
        "vendedor_nombre": "LaFuente",
    },
    {
        "nombre":      "Denim CO",
        "categoria":   "Ropa y Accesorios",
        "ubicacion":   "Bogotá",
        "descripcion": "Pantalones y prendas en denim premium colombiano.",
        "vendedor_email": "denimco@colmercia.co",
        "vendedor_nombre": "DenimCO",
    },
    {
        "nombre":      "Urban Style",
        "categoria":   "Ropa y Accesorios",
        "ubicacion":   "Bogotá",
        "descripcion": "Streetwear urbano colombiano.",
        "vendedor_email": "urbanstyle@colmercia.co",
        "vendedor_nombre": "UrbanStyle",
    },
    {
        "nombre":      "BagCo",
        "categoria":   "Carteras y Bolsos",
        "ubicacion":   "Cali",
        "descripcion": "Bolsos y accesorios para el día a día.",
        "vendedor_email": "bagco@colmercia.co",
        "vendedor_nombre": "BagCo",
    },
    {
        "nombre":      "Cuero MX",
        "categoria":   "Calzado",
        "ubicacion":   "Manizales",
        "descripcion": "Calzado formal en cuero genuino de Manizales.",
        "vendedor_email": "cueromx@colmercia.co",
        "vendedor_nombre": "CueroMX",
    },
    {
        "nombre":      "Craft Studio",
        "categoria":   "Papelería",
        "ubicacion":   "Bogotá",
        "descripcion": "Materiales creativos, washi tapes y stickers decorativos.",
        "vendedor_email": "craftstudio@colmercia.co",
        "vendedor_nombre": "CraftStudio",
    },
    {
        "nombre":      "PixelTech",
        "categoria":   "Tecnología",
        "ubicacion":   "Medellín",
        "descripcion": "Accesorios tecnológicos slim y inalámbricos.",
        "vendedor_email": "pixeltech@colmercia.co",
        "vendedor_nombre": "PixelTech",
    },
    {
        "nombre":      "Joyas Mompox",
        "categoria":   "Joyería",
        "ubicacion":   "Mompox",
        "descripcion": "Filigrana de oro y plata hecha a mano por artesanos de Mompox.",
        "vendedor_email": "joyasmompox@colmercia.co",
        "vendedor_nombre": "JoyasMompox",
    },
    {
        "nombre":      "Joyas Zenú",
        "categoria":   "Joyería",
        "ubicacion":   "Montería",
        "descripcion": "Accesorios bañados en oro inspirados en la cultura Zenú.",
        "vendedor_email": "joyaszenu@colmercia.co",
        "vendedor_nombre": "JoyasZenu",
    },
    {
        "nombre":      "Artesanías San Jacinto",
        "categoria":   "Artesanías",
        "ubicacion":   "San Jacinto",
        "descripcion": "Hamacas y tejidos artesanales de San Jacinto, Bolívar.",
        "vendedor_email": "sanjacinto@colmercia.co",
        "vendedor_nombre": "SanJacinto",
    },
    {
        "nombre":      "Wayuu Taya",
        "categoria":   "Artesanías",
        "ubicacion":   "Riohacha",
        "descripcion": "Mochilas y tejidos auténticos Wayuu de La Guajira.",
        "vendedor_email": "wayuutaya@colmercia.co",
        "vendedor_nombre": "WayuuTaya",
    },
    {
        "nombre":      "Tshirts",
        "categoria":   "Ropa y Accesorios",
        "ubicacion":   "Barranquilla",
        "descripcion": "Camisetas y accesorios con diseños del Caribe colombiano.",
        "vendedor_email": "tshirts@colmercia.co",
        "vendedor_nombre": "Tshirts",
    },
    {
        "nombre":      "Aroma Casa",
        "categoria":   "Regalos",
        "ubicacion":   "Bogotá",
        "descripcion": "Velas aromáticas de soya y productos para el hogar.",
        "vendedor_email": "aromacasa@colmercia.co",
        "vendedor_nombre": "AromaCasa",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  DATOS: todos los productos hardcodeados
#
#  Campos:
#    tienda       → nombre exacto de la tienda (debe coincidir con TIENDAS)
#    nombre       → nombre del producto
#    descripcion  → descripción completa
#    precio       → precio en pesos (sin formato, solo número)
#    precio_ant   → precio antiguo/tachado (None si no aplica)
#    stock        → "high" | "low" | "out"
#    cantidad     → unidades disponibles
#    categoria    → categoría de ColMercia
#    ocasion      → "todos" | "cumpleanos" | "amor" | "navidad" | "halloween"
#    seccion      → "" | "nuevos" | "destacados" | "region"
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTOS = [
    # ── NUEVOS PRODUCTOS ──────────────────────────────────────────────────
    {
        "tienda":      "Essence CO",
        "nombre":      "Perfume Dulce Miel 50ml",
        "descripcion": "Fragancia dulce y envolvente, elaborada con ingredientes naturales del Caribe colombiano. Presentación 50ml ideal para uso diario.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    14,
        "categoria":   "Regalos",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },
    {
        "tienda":      "Moda Propia",
        "nombre":      "Vestido Maxi Floral",
        "descripcion": "Diseño exclusivo inspirado en los jardines del Pacífico. Tela liviana y fresca, perfecta para el clima tropical colombiano.",
        "precio":      138000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },
    {
        "tienda":      "Paso Firme",
        "nombre":      "Zapatos Plataforma Beige",
        "descripcion": "Calzado artesanal de cuero genuino con plataforma de 4cm. Cómodo para largas jornadas y elegante para cualquier ocasión.",
        "precio":      162000,
        "precio_ant":  195000,
        "stock":       "low",
        "cantidad":    3,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Mini Bag Cadena Dorada",
        "descripcion": "Bolso mini en cuero sintético de alta calidad con cadena dorada ajustable. Capacidad para esenciales con diseño sofisticado.",
        "precio":      118000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    20,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Box Organizador Escritorio",
        "descripcion": "Set organizador de escritorio con 4 compartimentos, fabricado en cartón premium reciclado.",
        "precio":      48000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    35,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },
    {
        "tienda":      "Glam Medellín",
        "nombre":      "Sérum Vitamina C 30ml",
        "descripcion": "Sérum antioxidante con 15% de Vitamina C pura. Ilumina el tono de la piel y reduce manchas con uso diario de 30 días.",
        "precio":      62000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    22,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "nuevos",
    },

    # ── MÁS VENDIDOS (BESTSELLERS) ────────────────────────────────────────
    {
        "tienda":      "r.e.m. beauty",
        "nombre":      "Yours Truly Set Edición Limitada",
        "descripcion": "Set de edición limitada con base, rubor y labial en tonos cálidos. Presentación de lujo con empaque biodegradable.",
        "precio":      189900,
        "precio_ant":  230000,
        "stock":       "low",
        "cantidad":    5,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },
    {
        "tienda":      "Artesanías La Fuente",
        "nombre":      "Sombrero Vueltiao Tricolor",
        "descripcion": "Sombrero vueltiao fabricado en caña flecha por artesanos de la comunidad Zenú. Diseño tradicional con banda tricolor. Tallas S, M, L.",
        "precio":      245000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    23,
        "categoria":   "Artesanías",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },
    {
        "tienda":      "Paso Firme",
        "nombre":      "Sneakers Blancas Premium",
        "descripcion": "Sneakers en cuero genuino blanco con suela de goma vulcanizada. Plantilla anatómica para máxima comodidad.",
        "precio":      185000,
        "precio_ant":  210000,
        "stock":       "high",
        "cantidad":    11,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },
    {
        "tienda":      "TechPyme",
        "nombre":      "Parlante Bluetooth Portátil",
        "descripcion": "Parlante inalámbrico con 12h de batería, resistencia al agua IPX5 y sonido 360°.",
        "precio":      92000,
        "precio_ant":  None,
        "stock":       "out",
        "cantidad":    0,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Kit Planner Mensual + Stickers",
        "descripcion": "Kit completo con planner A5 mensual, 120 stickers decorativos y 3 marcadores brush.",
        "precio":      38500,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    34,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },
    {
        "tienda":      "Glam Medellín",
        "nombre":      "Paleta Sombras 12 Tonos Nude",
        "descripcion": "Paleta de 12 sombras en tonos nude y marrón, fórmula larga duración 24h.",
        "precio":      67000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    3,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "destacados",
    },

    # ── CATEGORÍA: MAQUILLAJE ─────────────────────────────────────────────
    {
        "tienda":      "Glam Medellín",
        "nombre":      "Base de Maquillaje SPF30",
        "descripcion": "Base de cobertura media-alta con SPF30.",
        "precio":      55000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    22,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "r.e.m. beauty",
        "nombre":      "Labial Líquido Matte Rojo",
        "descripcion": "Labial líquido de alta pigmentación en rojo intenso.",
        "precio":      38000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    40,
        "categoria":   "Maquillaje",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Luxedrop Beauty",
        "nombre":      "Paleta Iluminador 3 Tonos",
        "descripcion": "Paleta con 3 tonos iluminadores.",
        "precio":      78000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    6,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Glam Medellín",
        "nombre":      "Máscara de Pestañas Volume",
        "descripcion": "Máscara de pestañas con fórmula volumizadora.",
        "precio":      42000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    15,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "r.e.m. beauty",
        "nombre":      "Contorno en Polvo Bronze",
        "descripcion": "Polvo de contorno bronze.",
        "precio":      48000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    19,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Luxedrop Beauty",
        "nombre":      "Primer Poros Invisible",
        "descripcion": "Primer de base silicona.",
        "precio":      52000,
        "precio_ant":  None,
        "stock":       "out",
        "cantidad":    0,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },

    # ── CATEGORÍA: ROPA ───────────────────────────────────────────────────
    {
        "tienda":      "Moda Propia",
        "nombre":      "Suéter Oversize Tejido",
        "descripcion": "Suéter oversize en hilo tejido artesanalmente.",
        "precio":      89000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    18,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Moda Propia",
        "nombre":      "Camisa Lino Manga Larga",
        "descripcion": "Camisa 100% lino lavado.",
        "precio":      72000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    24,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Denim CO",
        "nombre":      "Pantalón Baggy Denim",
        "descripcion": "Pantalón baggy en denim premium.",
        "precio":      115000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    4,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Moda Propia",
        "nombre":      "Blusa Floral Manga Corta",
        "descripcion": "Blusa en tela viscosa con estampado floral.",
        "precio":      58000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    30,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Urban Style",
        "nombre":      "Chaqueta Bomber Negra",
        "descripcion": "Chaqueta bomber en nylon ripstop.",
        "precio":      145000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    9,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Denim CO",
        "nombre":      "Short Cargo Verde",
        "descripcion": "Short cargo en gabardina verde militar.",
        "precio":      68000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    3,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },

    # ── CATEGORÍA: CARTERAS ───────────────────────────────────────────────
    {
        "tienda":      "Studio BH",
        "nombre":      "Bolso Tote Canvas Natural",
        "descripcion": "Bolso tote en canvas 100% algodón natural.",
        "precio":      120000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    12,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Clutch Cuero Dorado",
        "descripcion": "Clutch en cuero sintético metalizado dorado.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    5,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "BagCo",
        "nombre":      "Mochila Urbana Negra",
        "descripcion": "Mochila urban con compartimento para laptop.",
        "precio":      135000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Cartera Baguette Beige",
        "descripcion": "Cartera estilo baguette en piel beige.",
        "precio":      145000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    16,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "BagCo",
        "nombre":      "Riñonera Mini Rosa",
        "descripcion": "Riñonera compacta en rosa nude.",
        "precio":      75000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    25,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },

    # ── CATEGORÍA: CALZADO ────────────────────────────────────────────────
    {
        "tienda":      "Paso Firme",
        "nombre":      "Botas Chelsea Café",
        "descripcion": "Botas Chelsea en cuero genuino café.",
        "precio":      210000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    10,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Paso Firme",
        "nombre":      "Sandalias Planas Nude",
        "descripcion": "Sandalias en tiras de cuero nude tejido.",
        "precio":      88000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    20,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Cuero MX",
        "nombre":      "Zapatos Oxford Negros",
        "descripcion": "Oxford clásico en cuero negro pulido.",
        "precio":      175000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    3,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Cuero MX",
        "nombre":      "Tacones Stiletto Rojo",
        "descripcion": "Stiletto en charol rojo con tacón de 10cm.",
        "precio":      145000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    11,
        "categoria":   "Calzado",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Paso Firme",
        "nombre":      "Alpargatas Trenzadas",
        "descripcion": "Alpargatas artesanales tejidas en fique natural.",
        "precio":      65000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    35,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },

    # ── CATEGORÍA: PAPELERÍA ──────────────────────────────────────────────
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Cuaderno Bullet Journal A5",
        "descripcion": "Bullet journal A5 con 200 páginas punteadas.",
        "precio":      28000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    50,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Set Lápices de Colores 24u",
        "descripcion": "Set 24 lápices de colores solubles en agua.",
        "precio":      22000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    60,
        "categoria":   "Papelería",
        "ocasion":     "cumpleanos",
        "seccion":     "",
    },
    {
        "tienda":      "Craft Studio",
        "nombre":      "Washi Tape Pack x10",
        "descripcion": "Pack 10 washi tapes de 15mm, diseños florales.",
        "precio":      18000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    80,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Planner Semanal Premium",
        "descripcion": "Planner semanal A5 sin fechas, 52 semanas.",
        "precio":      35000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    8,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Craft Studio",
        "nombre":      "Stickers Decorativos 200u",
        "descripcion": "200 stickers impresos en papel adhesivo matte.",
        "precio":      12000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    120,
        "categoria":   "Papelería",
        "ocasion":     "cumpleanos",
        "seccion":     "",
    },

    # ── CATEGORÍA: TECNOLOGÍA ─────────────────────────────────────────────
    {
        "tienda":      "TechPyme",
        "nombre":      "Hub USB-C 7 Puertos",
        "descripcion": "Hub USB-C con 7 puertos.",
        "precio":      85000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    14,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "TechPyme",
        "nombre":      "Soporte Laptop Aluminio",
        "descripcion": "Soporte ergonómico de aluminio.",
        "precio":      72000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    18,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "PixelTech",
        "nombre":      "Mouse Inalámbrico Slim",
        "descripcion": "Mouse inalámbrico 2.4GHz ultra-delgado.",
        "precio":      65000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    5,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "TechPyme",
        "nombre":      "Cable USB-C Trenzado 2m",
        "descripcion": "Cable USB-C trenzado en nylon de 2 metros.",
        "precio":      28000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    45,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },

    # ── CATEGORÍA: JOYERÍA ────────────────────────────────────────────────
    {
        "tienda":      "Joyas Mompox",
        "nombre":      "Aretes de Filigrana Dorados",
        "descripcion": "Aretes elaborados a mano en filigrana de oro 18k por artesanos de Mompox.",
        "precio":      85000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    15,
        "categoria":   "Joyería",
        "ocasion":     "amor",
        "seccion":     "region",
    },
    {
        "tienda":      "Joyas Mompox",
        "nombre":      "Aretes Filigrana Plateados Orquídea",
        "descripcion": "Aretes en filigrana de plata 950 con diseño inspirado en la orquídea, flor nacional de Colombia.",
        "precio":      72000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    12,
        "categoria":   "Joyería",
        "ocasion":     "amor",
        "seccion":     "region",
    },
    {
        "tienda":      "Joyas Mompox",
        "nombre":      "Brazalete de Filigrana",
        "descripcion": "Brazalete elaborado a mano en filigrana de plata 950 por artesanos de Mompox.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Joyería",
        "ocasion":     "amor",
        "seccion":     "region",
    },
    {
        "tienda":      "Joyas Zenú",
        "nombre":      "Set Accesorios Dorados",
        "descripcion": "Set con collar, aretes y pulsera bañados en oro 18k. Hipoalergénicos, presentación caja de terciopelo.",
        "precio":      75000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    22,
        "categoria":   "Joyería",
        "ocasion":     "amor",
        "seccion":     "",
    },

    # ── CATEGORÍA: ARTESANÍAS ─────────────────────────────────────────────
    {
        "tienda":      "Artesanías San Jacinto",
        "nombre":      "Hamaca Sanjacintana",
        "descripcion": "Hamaca tejida a mano en algodón 100% natural por tejedoras de San Jacinto, Bolívar.",
        "precio":      180000,
        "precio_ant":  220000,
        "stock":       "low",
        "cantidad":    6,
        "categoria":   "Artesanías",
        "ocasion":     "todos",
        "seccion":     "region",
    },
    {
        "tienda":      "Artesanías La Fuente",
        "nombre":      "Sombrero Vueltiao",
        "descripcion": "Sombrero vueltiao 21 vueltas fabricado en caña flecha por artesanos de la comunidad Zenú de Tuchín, Córdoba.",
        "precio":      245000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    10,
        "categoria":   "Artesanías",
        "ocasion":     "todos",
        "seccion":     "region",
    },
    {
        "tienda":      "Wayuu Taya",
        "nombre":      "Mochila Wayuu",
        "descripcion": "Mochila auténtica tejida a crochet por mujeres Wayuu de La Guajira. Cada mochila tarda entre 3 y 5 días en tejerse.",
        "precio":      135000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    20,
        "categoria":   "Artesanías",
        "ocasion":     "todos",
        "seccion":     "region",
    },
    {
        "tienda":      "Tshirts",
        "nombre":      "Camiseta blanca CARIBE",
        "descripcion": "Camiseta 100% algodón con diseño caribeño impreso.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Artesanías",
        "ocasion":     "todos",
        "seccion":     "region",
    },

    # ── PRODUCTOS DE REGIÓN (extras) ──────────────────────────────────────
    {
        "tienda":      "Tshirts",
        "nombre":      "Funda S26 Ultra CARIBE",
        "descripcion": "Funda artesanal para Samsung S26 Ultra con diseños del Caribe colombiano.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "region",
    },
    {
        "tienda":      "Tshirts",
        "nombre":      "Funda GalaxyBooks 3 CARIBE",
        "descripcion": "Funda protectora para Samsung Galaxy Book 3 con diseños del Caribe.",
        "precio":      54900,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "region",
    },
    {
        "tienda":      "Tshirts",
        "nombre":      "Pocillo Blanco CARIBE",
        "descripcion": "Pocillo blanco 350ml con diseño caribeño impreso a alta temperatura.",
        "precio":      19900,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    8,
        "categoria":   "Regalos",
        "ocasion":     "cumpleanos",
        "seccion":     "region",
    },

    # ── SECCIÓN REGALOS ───────────────────────────────────────────────────
    {
        "tienda":      "Essence CO",
        "nombre":      "Set Bienestar Mujer",
        "descripcion": "Set de bienestar con crema corporal, sales de baño y vela aromática. Presentación caja regalo biodegradable.",
        "precio":      120000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    12,
        "categoria":   "Regalos",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Kit Papelería Creativa",
        "descripcion": "Kit con cuaderno A5, 10 stickers decorativos, 3 marcadores brush y washi tape. Ideal para amantes del lettering.",
        "precio":      55000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    30,
        "categoria":   "Papelería",
        "ocasion":     "cumpleanos",
        "seccion":     "",
    },
    {
        "tienda":      "Glam Medellín",
        "nombre":      "Set Maquillaje Básico",
        "descripcion": "Set básico con labial matte, máscara de pestañas y rubor en polvo. Perfecto para regalo de cumpleaños.",
        "precio":      89000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    18,
        "categoria":   "Maquillaje",
        "ocasion":     "cumpleanos",
        "seccion":     "",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Mini Bolso de Fiesta",
        "descripcion": "Mini bolso clutch con cadena dorada desmontable. Interior forrado con espejo. Disponible en negro y nude.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "low",
        "cantidad":    5,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Aroma Casa",
        "nombre":      "Velas Aromáticas x3",
        "descripcion": "Pack de 3 velas de soya con fragancias: lavanda, vainilla y coco. Tiempo de quema: 25h cada una.",
        "precio":      48000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    40,
        "categoria":   "Regalos",
        "ocasion":     "navidad",
        "seccion":     "",
    },

    # ── TIENDAS DESTACADAS: productos extra de sus featured ───────────────
    # Luxedrop Beauty
    {
        "tienda":      "Luxedrop Beauty",
        "nombre":      "Set Glow Total",
        "descripcion": "Set completo para conseguir un glow perfecto: base, iluminador y fijador.",
        "precio":      125000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    15,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Luxedrop Beauty",
        "nombre":      "Labial Set x3",
        "descripcion": "Set de 3 labiales en tonos coral, rojo y nude.",
        "precio":      68000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    20,
        "categoria":   "Maquillaje",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Luxedrop Beauty",
        "nombre":      "Iluminador Duo",
        "descripcion": "Iluminador en dos tonos: dorado y champagne.",
        "precio":      54000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    18,
        "categoria":   "Maquillaje",
        "ocasion":     "todos",
        "seccion":     "",
    },
    # Studio BH featured extra
    {
        "tienda":      "Studio BH",
        "nombre":      "Bolso Tote Canvas",
        "descripcion": "Bolso tote en canvas resistente con asas reforzadas.",
        "precio":      120000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    12,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Clutch Cuero",
        "descripcion": "Clutch elegante en cuero genuino con cierre magnético.",
        "precio":      95000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    10,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "amor",
        "seccion":     "",
    },
    {
        "tienda":      "Studio BH",
        "nombre":      "Riñonera Mini",
        "descripcion": "Riñonera mini en cuero sintético con múltiples compartimentos.",
        "precio":      75000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    25,
        "categoria":   "Carteras y Bolsos",
        "ocasion":     "todos",
        "seccion":     "",
    },
    # Paso Firme featured extra
    {
        "tienda":      "Paso Firme",
        "nombre":      "Botas Chelsea",
        "descripcion": "Botas Chelsea en cuero genuino con elásticos laterales.",
        "precio":      210000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    10,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Paso Firme",
        "nombre":      "Sandalias Nude",
        "descripcion": "Sandalias planas en cuero nude con tiras cruzadas.",
        "precio":      88000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    20,
        "categoria":   "Calzado",
        "ocasion":     "todos",
        "seccion":     "",
    },
    # TechPyme featured extra
    {
        "tienda":      "TechPyme",
        "nombre":      "Auriculares Bluetooth",
        "descripcion": "Auriculares inalámbricos con cancelación de ruido y 20h de batería.",
        "precio":      98000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    12,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "TechPyme",
        "nombre":      "Mouse Slim",
        "descripcion": "Mouse inalámbrico ultra-delgado con scroll silencioso.",
        "precio":      65000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    18,
        "categoria":   "Tecnología",
        "ocasion":     "todos",
        "seccion":     "",
    },
    # Moda Propia featured extra
    {
        "tienda":      "Moda Propia",
        "nombre":      "Chaqueta Bomber",
        "descripcion": "Chaqueta bomber en tela resistente con forro interior.",
        "precio":      145000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    9,
        "categoria":   "Ropa y Accesorios",
        "ocasion":     "todos",
        "seccion":     "",
    },
    # Papel y Arte featured extra
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Bullet Journal A5",
        "descripcion": "Bullet journal A5 con cubierta rígida y páginas punteadas.",
        "precio":      28000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    50,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Papel y Arte",
        "nombre":      "Planner Semanal",
        "descripcion": "Planner semanal A5 con secciones para metas y hábitos.",
        "precio":      35000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    40,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
    {
        "tienda":      "Craft Studio",
        "nombre":      "Washi Tape x10",
        "descripcion": "Pack de 10 washi tapes con diseños variados.",
        "precio":      18000,
        "precio_ant":  None,
        "stock":       "high",
        "cantidad":    80,
        "categoria":   "Papelería",
        "ocasion":     "todos",
        "seccion":     "",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  COMMAND
# ─────────────────────────────────────────────────────────────────────────────
class Command(BaseCommand):
    help = "Puebla la BD con tiendas y productos hardcodeados del landing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina TODOS los productos y tiendas seed antes de insertar.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("⚠️  Eliminando productos y tiendas seed..."))
            emails_seed = [t["vendedor_email"] for t in TIENDAS]
            Usuario.objects.filter(email__in=emails_seed).delete()
            self.stdout.write(self.style.SUCCESS("   Limpieza completa."))

        with transaction.atomic():
            tiendas_map = self._crear_tiendas()
            creados, omitidos = self._crear_productos(tiendas_map)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Seed completado: {creados} productos creados, {omitidos} ya existían."
            )
        )

    # ── helpers ──────────────────────────────────────────────────────────

    def _crear_tiendas(self):
        """
        Crea (o recupera) un Usuario-vendedor y su Tienda para cada entrada
        en TIENDAS. Devuelve un dict {nombre_tienda: instancia_Tienda}.
        """
        tiendas_map = {}
        for td in TIENDAS:
            # Intentar recuperar por email primero
            vendedor = Usuario.objects.filter(email=td["vendedor_email"]).first()
            creado_u = False

            if not vendedor:
                # Generar username único basado en el email (parte antes del @)
                base_username = td["vendedor_email"].split("@")[0]
                username = base_username
                contador = 1
                while Usuario.objects.filter(username=username).exists():
                    username = f"{base_username}_{contador}"
                    contador += 1

                vendedor = Usuario(
                    email=td["vendedor_email"],
                    username=username,
                    first_name=td["vendedor_nombre"],
                    rol="vendedor",
                    aprobado=True,
                    is_active=True,
                )
                vendedor.set_password("ColMercia2025!")
                vendedor.save()
                creado_u = True
                self.stdout.write(f"   👤 Vendedor creado: {vendedor.email}")

            # Crear o recuperar tienda
            tienda, creada_t = Tienda.objects.get_or_create(
                vendedor=vendedor,
                defaults={
                    "nombre":      td["nombre"],
                    "descripcion": td["descripcion"],
                    "ubicacion":   td["ubicacion"],
                    "categoria":   td["categoria"],
                    "aprobada":    True,
                },
            )
            if creada_t:
                self.stdout.write(f"   🏪 Tienda creada: {tienda.nombre}")

            tiendas_map[td["nombre"]] = tienda

        return tiendas_map

    def _crear_productos(self, tiendas_map):
        """
        Inserta los productos usando get_or_create para ser idempotente.
        Retorna (creados, omitidos).
        """
        creados  = 0
        omitidos = 0

        for p in PRODUCTOS:
            tienda = tiendas_map.get(p["tienda"])
            if not tienda:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️  Tienda no encontrada: {p['tienda']} — omitiendo {p['nombre']}")
                )
                omitidos += 1
                continue

            prod, creado = Producto.objects.get_or_create(
                tienda=tienda,
                nombre=p["nombre"],
                defaults={
                    "descripcion":    p["descripcion"],
                    "precio":         Decimal(str(p["precio"])),
                    "precio_antiguo": Decimal(str(p["precio_ant"])) if p["precio_ant"] else None,
                    "stock":          p["stock"],
                    "cantidad":       p["cantidad"],
                    "categoria":      p["categoria"],
                    "ocasion_regalo": p["ocasion"],
                    "seccion_landing": p.get("seccion", ""),
                    "aprobado":       True,
                },
            )

            if creado:
                creados += 1
                self.stdout.write(f"   ✔ {prod.nombre} → {tienda.nombre}")
            else:
                omitidos += 1

        return creados, omitidos