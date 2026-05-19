from django.db import models
from django.contrib.auth.models import AbstractUser


# ─────────────────────────────────────────────
#  USUARIO PERSONALIZADO
# ─────────────────────────────────────────────
class Usuario(AbstractUser):
    ROLES = [
        ("comprador", "Comprador"),
        ("vendedor", "Vendedor"),
        ("admin", "Administrador"),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default="comprador")
    aprobado = models.BooleanField(default=False)
    telefono = models.CharField(max_length=20, blank=True, default="")

    def es_vendedor_aprobado(self):
        return self.rol == "vendedor" and self.aprobado

    def __str__(self):
        return f"{self.email} ({self.rol})"


# ─────────────────────────────────────────────
#  TIENDA  (se crea automáticamente al registrar un vendedor)
# ─────────────────────────────────────────────
class Tienda(models.Model):
    vendedor = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="tienda"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, default="")
    ubicacion = models.CharField(max_length=100, blank=True, default="")
    categoria = models.CharField(max_length=50, blank=True, default="")
    aprobada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# ─────────────────────────────────────────────
#  PRODUCTO
# ─────────────────────────────────────────────
class Producto(models.Model):
    STOCK_CHOICES = [
        ("high", "Disponible"),
        ("low", "Poco stock"),
        ("out", "Agotado"),
    ]

    OCASION_CHOICES = [
        ("todos",      "Todas las ocasiones"),
        ("cumpleanos", "Cumpleaños"),
        ("amor",       "Amor y Amistad"),
        ("navidad",    "Navidad"),
        ("halloween",  "Halloween"),
    ]

    tienda          = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    nombre          = models.CharField(max_length=100)
    descripcion     = models.TextField()
    precio          = models.DecimalField(max_digits=10, decimal_places=2)
    precio_antiguo  = models.DecimalField(
                        max_digits=10, decimal_places=2, null=True, blank=True
                      )
    stock           = models.CharField(max_length=10, choices=STOCK_CHOICES, default="high")
    cantidad        = models.PositiveIntegerField(default=0)
    imagen          = models.ImageField(upload_to="productos/", blank=True)
    ocasion_regalo  = models.CharField(          # ← NUEVO CAMPO
                        max_length=20,
                        choices=OCASION_CHOICES,
                        default="todos",
                        blank=True,
                      )
    creado_en       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    def precio_formateado(self):
        """Devuelve el precio con formato colombiano: $55.000"""
        return f"${self.precio:,.0f}".replace(",", ".")


# ─────────────────────────────────────────────
#  PEDIDO
# ─────────────────────────────────────────────
class Pedido(models.Model):
    ESTADOS = [
        ("procesando", "Procesando"),
        ("preparando", "Preparando"),
        ("en_camino",  "En camino"),
        ("entregado",  "Entregado"),
        ("cancelado",  "Cancelado"),
    ]
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="pedidos"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, related_name="pedidos"
    )
    cantidad          = models.PositiveIntegerField(default=1)
    total             = models.DecimalField(max_digits=10, decimal_places=2)
    estado            = models.CharField(max_length=20, choices=ESTADOS, default="procesando")
    fecha             = models.DateTimeField(auto_now_add=True)
    direccion_entrega = models.CharField(max_length=200, blank=True, default="")

    # ── EMPAQUE DE REGALO ────────────────────────────────
    es_regalo         = models.BooleanField(default=False)
    regalo_envoltura  = models.CharField(max_length=30, blank=True, default="")   # bolsa_papel | bolsa_tela | caja
    regalo_decoracion = models.CharField(max_length=30, blank=True, default="")   # corazon | globos | navidad | halloween
    regalo_mensaje    = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Pedido #{self.id} — {self.usuario.email}"

    def total_formateado(self):
        return f"${self.total:,.0f}".replace(",", ".")

    def estado_pill_class(self):
        """Clase CSS según el estado para los badges de la template."""
        clases = {
            "procesando": "sp-amber",
            "preparando": "sp-amber",
            "en_camino":  "sp-blue",
            "entregado":  "sp-green",
            "cancelado":  "sp-red",
        }
        return clases.get(self.estado, "sp-blue")

    def estado_label(self):
        return dict(self.ESTADOS).get(self.estado, self.estado)