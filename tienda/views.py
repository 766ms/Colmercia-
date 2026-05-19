import json
from decimal import Decimal, InvalidOperation

# Importaciones de autenticación y mezcla de Django
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

# Importaciones de vistas y respuestas de Django
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

# Importaciones de decoradores para peticiones asíncronas
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Importaciones de tus modelos locales de la app
from .models import Pedido, Tienda, Usuario  # Asegúrate de que 'Usuario' exista en tu models.py
from django.http import JsonResponse
from .models import Producto

def productos_regalo(request):
    ocasion = request.GET.get('ocasion', 'todos')
    precio  = request.GET.get('precio', 'todos')

    qs = Producto.objects.exclude(ocasion_regalo='ninguno').exclude(ocasion_regalo='')

    if ocasion != 'todos':
        qs = qs.filter(ocasion_regalo=ocasion)

    if precio == '50':
        qs = qs.filter(precio__lt=50000)
    elif precio == '50-100':
        qs = qs.filter(precio__gte=50000, precio__lte=100000)
    elif precio == '100':
        qs = qs.filter(precio__gt=100000)

    data = [{
        'id':       p.id,
        'nombre':   p.nombre,
        'precio':   p.precio_formateado(),
        'precio_num': float(p.precio),
        'ocasion':  p.ocasion_regalo,
        'imagen':   p.imagen.url if p.imagen else '',
        'stock':    p.stock,
    } for p in qs]

    return JsonResponse(data, safe=False)

# ─────────────────────────────────────────────
#  LANDING
# ─────────────────────────────────────────────
class LandingView(TemplateView):
    template_name = "tienda/landing.html"

    def get(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.create()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


# ─────────────────────────────────────────────
#  PERFIL COMPRADOR
# ─────────────────────────────────────────────
class CompradorView(LoginRequiredMixin, TemplateView):
    template_name = "tienda/comprador.html"
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol != "comprador":
            return redirect("landing")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["pedidos"] = Pedido.objects.filter(
            usuario=self.request.user
        ).select_related("producto", "producto__tienda").order_by("-fecha")
        return context


# ─────────────────────────────────────────────
#  PANEL VENDEDOR
# ─────────────────────────────────────────────
class VendedorView(LoginRequiredMixin, TemplateView):
    template_name = "tienda/vendedor.html"
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.rol != "vendedor":
                return redirect("landing")
            if not request.user.aprobado:
                return redirect("pendiente")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user

        try:
            tienda = user.tienda
        except Tienda.DoesNotExist:
            tienda = None

        context["tienda"] = tienda

        if tienda:
            from .models import Producto
            context["productos"] = tienda.producto_set.all()
            context["pedidos"] = Pedido.objects.filter(
                producto__tienda=tienda
            ).select_related("usuario", "producto").order_by("-fecha")
        else:
            context["productos"] = []
            context["pedidos"] = []

        return context


# ─────────────────────────────────────────────
#  PENDIENTE DE APROBACIÓN
# ─────────────────────────────────────────────
class PendienteView(TemplateView):
    template_name = "tienda/pendiente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


# ─────────────────────────────────────────────
#  ADMIN
# ─────────────────────────────────────────────
class AdminView(LoginRequiredMixin, TemplateView):
    template_name = "tienda/admin_pag.html"
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol != "admin":
            return redirect("landing")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user

        # Vendedores pendientes de aprobación (con su tienda)
        context["vendedores_pendientes"] = (
            Usuario.objects.filter(rol="vendedor", aprobado=False)
            .select_related("tienda")
            .order_by("-date_joined")
        )

        # Todos los usuarios (para la tabla de control)
        context["todos_usuarios"] = (
            Usuario.objects.all()
            .prefetch_related("tienda")
            .order_by("-date_joined")
        )

        # Vendedores aprobados con su tienda y stats
        context["vendedores_aprobados"] = (
            Usuario.objects.filter(rol="vendedor", aprobado=True)
            .select_related("tienda")
            .order_by("first_name")
        )

        return context


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "Datos inválidos."})

        email = data.get("email", "").strip()
        password = data.get("password", "")

        try:
            u = Usuario.objects.get(email=email)
            user = authenticate(request, username=u.username, password=password)
        except Usuario.DoesNotExist:
            user = None

        if user:
            login(request, user)
            redirects = {
                "comprador": "/comprador/",
                "vendedor": "/vendedor/",
                "admin": "/admin-pag/",
            }
            return JsonResponse(
                {"ok": True, "redirect": redirects.get(user.rol, "/")}
            )

        return JsonResponse({"ok": False, "error": "Correo o contraseña incorrectos."})


# ─────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────
# Al inicio de views.py, añade este import:
from .forms import CompradorRegistroForm, VendedorRegistroForm

# Luego en RegistroView, reemplaza el método post completo:
class RegistroView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Datos inválidos.'})

        rol = data.get('rol', '').strip()

        if rol not in ('comprador', 'vendedor'):
            return JsonResponse({'ok': False, 'error': 'Rol inválido.'})

        # ── COMPRADOR ──
        if rol == 'comprador':
            # Mapear password → password1/password2 para el form
            data['password1'] = data.get('password', '')
            data['password2'] = data.get('password2', data.get('password', ''))
            form = CompradorRegistroForm(data)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return JsonResponse({'ok': True, 'redirect': '/comprador/'})
            else:
                primer_error = list(form.errors.values())[0][0]
                return JsonResponse({'ok': False, 'error': primer_error})

        # ── VENDEDOR ──
        if rol == 'vendedor':
            # Mapear password → password1/password2 para el form
            data['password1'] = data.get('password', '')
            data['password2'] = data.get('password2', data.get('password', ''))
            form = VendedorRegistroForm(data)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'ok': True,
                    'pendiente': True,
                    'mensaje': 'Solicitud enviada. Espera la aprobación del administrador.'
                })
            else:
                primer_error = list(form.errors.values())[0][0]
                return JsonResponse({'ok': False, 'error': primer_error})

# ─────────────────────────────────────────────
#  APROBACIÓN DE VENDEDOR (solo admin)
# ─────────────────────────────────────────────
class AprobarVendedorView(View):
    def post(self, request, user_id):
        if not request.user.is_authenticated or request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            vendedor = Usuario.objects.get(id=user_id, rol="vendedor")
            vendedor.aprobado = True
            vendedor.save()
            if hasattr(vendedor, "tienda"):
                vendedor.tienda.aprobada = True
                vendedor.tienda.save()
            return JsonResponse({"ok": True})
        except Usuario.DoesNotExist:
            return JsonResponse(
                {"ok": False, "error": "Vendedor no encontrado."}, status=404
            )


# ─────────────────────────────────────────────
#  RECHAZO DE VENDEDOR (solo admin)
# ─────────────────────────────────────────────
class RechazarVendedorView(View):
    def post(self, request, user_id):
        if not request.user.is_authenticated or request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            vendedor = Usuario.objects.get(id=user_id, rol="vendedor")
            # Eliminar tienda asociada si existe
            if hasattr(vendedor, "tienda"):
                vendedor.tienda.delete()
            vendedor.delete()
            return JsonResponse({"ok": True})
        except Usuario.DoesNotExist:
            return JsonResponse(
                {"ok": False, "error": "Vendedor no encontrado."}, status=404
            )


#  CREAR PEDIDO  —  POST /pedidos/crear/
#
#  Recibe desde el frontend el carrito completo (lista de productos)
#  y crea un Pedido por cada ítem.  Devuelve JSON con los pedidos
#  creados o un error.
# ────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class CrearPedidoView(LoginRequiredMixin, View):
    """
    Body esperado (JSON):
    {
        "items": [
            {
                "id": "Perfume Dulce Miel 50ml",   // nombre usado como id en el carrito
                "name": "Perfume Dulce Miel 50ml",
                "brand": "Essence CO",
                "price": "$95.000",
                "cantidad": 2,
                ...
            },
            ...
        ],
        "metodo_pago": "card"   // opcional, para registro futuro
    }
    """
 
    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)
 
        items = body.get("items", [])
        if not items:
            return JsonResponse({"ok": False, "error": "El carrito está vacío"}, status=400)
 
        # ── Datos de empaque de regalo (opcionales) ──────────────────────
        es_regalo         = bool(body.get("es_regalo", False))
        regalo_envoltura  = str(body.get("regalo_envoltura", "")).strip()[:30]
        regalo_decoracion = str(body.get("regalo_decoracion", "")).strip()[:30]
        regalo_mensaje    = str(body.get("regalo_mensaje", "")).strip()

        pedidos_creados = []
        errores = []
 
        for item in items:
            nombre_producto = (item.get("name") or item.get("id") or "").strip()
            cantidad = int(item.get("cantidad", 1))
 
            # Precio: viene como "$95.000" → convertir a Decimal
            precio_raw = item.get("price", "0")
            try:
                precio_num = Decimal(
                    precio_raw.replace("$", "").replace(".", "").replace(",", ".")
                )
            except (InvalidOperation, AttributeError):
                precio_num = Decimal("0")
 
            total = precio_num * cantidad
 
            # Buscar el producto en la BD por nombre (ajusta si tienes otro identificador)
            from .models import Producto, Pedido  # import local para evitar circulares
 
            producto_obj = (
                Producto.objects.filter(nombre__iexact=nombre_producto).first()
            )
 
            # Si no existe en BD lo creamos igualmente como pedido (modo catálogo estático)
            # pero sin FK a Producto (producto=None).  Puedes cambiar esto si prefieres
            # rechazar productos desconocidos.
            pedido = Pedido.objects.create(
                usuario=request.user,
                producto=producto_obj,          # puede ser None
                cantidad=cantidad,
                total=total,
                estado="procesando",
                es_regalo=es_regalo,
                regalo_envoltura=regalo_envoltura  if es_regalo else "",
                regalo_decoracion=regalo_decoracion if es_regalo else "",
                regalo_mensaje=regalo_mensaje    if es_regalo else "",
            )
            pedidos_creados.append(
                {
                    "id": pedido.id,
                    "producto": nombre_producto,
                    "cantidad": cantidad,
                    "total": str(total),
                    "estado": pedido.estado,
                    "es_regalo": pedido.es_regalo,
                }
            )
 
        return JsonResponse(
            {
                "ok": True,
                "pedidos": pedidos_creados,
                "mensaje": f"{len(pedidos_creados)} pedido(s) creado(s) correctamente.",
            }
        )
 
 
# ────────────────────────────────────────────────────────────────────
#  ACTUALIZAR ESTADO DE PEDIDO  —  PATCH /pedidos/<id>/estado/
#
#  Solo el vendedor dueño del producto (o un admin) puede cambiar
#  el estado.  El comprador solo puede leer en su perfil.
# ────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class ActualizarEstadoPedidoView(LoginRequiredMixin, View):
    """
    Body esperado (JSON):
    { "estado": "preparando" }   // procesando | preparando | en_camino | entregado | cancelado
    """
 
    ESTADOS_VALIDOS = ["procesando", "preparando", "en_camino", "entregado", "cancelado"]
 
    def patch(self, request, pedido_id):
        from .models import Pedido  # import local
 
        try:
            pedido = Pedido.objects.select_related(
                "producto__tienda__vendedor", "usuario"
            ).get(pk=pedido_id)
        except Pedido.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Pedido no encontrado"}, status=404)
 
        # Verificar permisos: vendedor del producto o admin
        es_admin = request.user.rol == "admin"
        es_vendedor_dueño = (
            request.user.rol == "vendedor"
            and pedido.producto is not None
            and pedido.producto.tienda.vendedor == request.user
        )
 
        if not (es_admin or es_vendedor_dueño):
            return JsonResponse(
                {"ok": False, "error": "No tienes permiso para cambiar este pedido"},
                status=403,
            )
 
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)
 
        nuevo_estado = body.get("estado", "").strip()
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"Estado inválido. Opciones: {', '.join(self.ESTADOS_VALIDOS)}",
                },
                status=400,
            )
 
        pedido.estado = nuevo_estado
        pedido.save(update_fields=["estado"])
 
        return JsonResponse(
            {
                "ok": True,
                "pedido_id": pedido.id,
                "estado": pedido.estado,
                "estado_label": pedido.estado_label(),
            }
        )
 

# ─────────────────────────────────────────────────────────────────────
#  API PÚBLICA DE PRODUCTOS  —  GET /api/productos/
#
#  Devuelve todos los productos con imagen, precio, stock, etc.
#  Se usa en la landing page para alimentar el buscador principal.
# ─────────────────────────────────────────────────────────────────────
def api_productos(request):
    """Endpoint público: todos los productos de vendedores activos."""
    productos = (
        Producto.objects
        .select_related("tienda__vendedor")
        .filter(tienda__vendedor__aprobado=True)
        .order_by("-creado_en")
    )
    data = [
        {
            "id":          p.id,
            "nombre":      p.nombre,
            "descripcion": p.descripcion,
            "precio":      p.precio_formateado(),
            "precio_num":  float(p.precio),
            "categoria":   p.categoria,
            "stock":       p.stock,
            "cantidad":    p.cantidad,
            "imagen":      p.imagen.url if p.imagen else "",
            "tienda":      p.tienda.nombre,
            "tienda_id":   p.tienda.id,
        }
        for p in productos
    ]
    return JsonResponse(data, safe=False)


# ─────────────────────────────────────────────────────────────────────
#  CREAR PRODUCTO  —  POST /productos/nuevo/
#
#  Recibe multipart/form-data con imagen.
#  Solo vendedores aprobados con tienda activa pueden crear productos.
# ─────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class CrearProductoView(LoginRequiredMixin, View):
    login_url = "/"

    def post(self, request):
        user = request.user
        if user.rol != "vendedor" or not user.aprobado:
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)

        try:
            tienda = user.tienda
        except Exception:
            return JsonResponse({"ok": False, "error": "No tienes tienda asociada."}, status=400)

        nombre     = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        precio_raw  = request.POST.get("precio", "0").replace("$", "").replace(".", "").replace(",", ".").strip()
        cantidad    = request.POST.get("cantidad", "0").strip()
        categoria   = request.POST.get("categoria", "").strip()
        imagen      = request.FILES.get("imagen")

        if not nombre or not descripcion or not precio_raw or not cantidad:
            return JsonResponse({"ok": False, "error": "Completa todos los campos obligatorios."}, status=400)

        try:
            precio   = Decimal(precio_raw)
            cantidad = int(cantidad)
        except Exception:
            return JsonResponse({"ok": False, "error": "Precio o cantidad inválidos."}, status=400)

        # Determinar stock automáticamente según cantidad
        if cantidad == 0:
            stock = "out"
        elif cantidad <= 5:
            stock = "low"
        else:
            stock = "high"

        prod = Producto(
            tienda=tienda,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            cantidad=cantidad,
            stock=stock,
            categoria=categoria,
            aprobado=True,
            ocasion_regalo="",  # ← esto evita que aparezca en regalos
        )
        if imagen:
            prod.imagen = imagen
        prod.save()

        return JsonResponse({
            "ok":       True,
            "id":       prod.id,
            "nombre":   prod.nombre,
            "precio":   prod.precio_formateado(),
            "cantidad": prod.cantidad,
            "stock":    prod.stock,
            "categoria": prod.categoria,
            "imagen":   prod.imagen.url if prod.imagen else "",
        })


# ─────────────────────────────────────────────────────────────────────
#  EDITAR PRODUCTO  —  POST /productos/<id>/editar/
# ─────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class EditarProductoView(LoginRequiredMixin, View):
    login_url = "/"

    def post(self, request, producto_id):
        user = request.user
        if user.rol != "vendedor" or not user.aprobado:
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)

        try:
            prod = Producto.objects.get(pk=producto_id, tienda__vendedor=user)
        except Producto.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Producto no encontrado."}, status=404)

        nombre      = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        precio_raw  = request.POST.get("precio", "").replace("$", "").replace(".", "").replace(",", ".").strip()
        cantidad    = request.POST.get("cantidad", "").strip()
        categoria   = request.POST.get("categoria", "").strip()
        imagen      = request.FILES.get("imagen")

        if nombre:
            prod.nombre = nombre
        if descripcion:
            prod.descripcion = descripcion
        if precio_raw:
            try:
                prod.precio = Decimal(precio_raw)
            except Exception:
                return JsonResponse({"ok": False, "error": "Precio inválido."}, status=400)
        if cantidad:
            try:
                prod.cantidad = int(cantidad)
                if prod.cantidad == 0:
                    prod.stock = "out"
                elif prod.cantidad <= 5:
                    prod.stock = "low"
                else:
                    prod.stock = "high"
            except Exception:
                return JsonResponse({"ok": False, "error": "Cantidad inválida."}, status=400)
        if categoria:
            prod.categoria = categoria
        if imagen:
            prod.imagen = imagen

        prod.save()

        return JsonResponse({
            "ok":       True,
            "id":       prod.id,
            "nombre":   prod.nombre,
            "precio":   prod.precio_formateado(),
            "cantidad": prod.cantidad,
            "stock":    prod.stock,
            "categoria": prod.categoria,
            "imagen":   prod.imagen.url if prod.imagen else "",
        })


# ─────────────────────────────────────────────────────────────────────
#  ELIMINAR PRODUCTO  —  DELETE /productos/<id>/eliminar/
# ─────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class EliminarProductoView(LoginRequiredMixin, View):
    login_url = "/"

    def delete(self, request, producto_id):
        user = request.user
        if user.rol != "vendedor" or not user.aprobado:
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)

        try:
            prod = Producto.objects.get(pk=producto_id, tienda__vendedor=user)
        except Producto.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Producto no encontrado."}, status=404)

        prod.delete()
        return JsonResponse({"ok": True, "id": producto_id})


# ─────────────────────────────────────────────────────────────────────
#  ACTUALIZAR OCASIÓN DE REGALO  —  POST /productos/<id>/ocasion/
# ─────────────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class ActualizarOcasionRegaloView(LoginRequiredMixin, View):
    def post(self, request, producto_id):
        if request.user.rol != 'admin':
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            prod = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Producto no encontrado."}, status=404)
        try:
            body = json.loads(request.body)
        except:
            return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)
        prod.ocasion_regalo = body.get('ocasion_regalo', '')
        prod.save(update_fields=['ocasion_regalo'])
        return JsonResponse({"ok": True, "nombre": prod.nombre, "ocasion_regalo": prod.ocasion_regalo})
