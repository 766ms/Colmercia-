import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.db.models import Prefetch, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Pedido, Tienda, Usuario, Producto, BannerLanding, Favorito
from .forms import CompradorRegistroForm, VendedorRegistroForm

@login_required
@require_POST
def toggle_favorito(request):
    data = json.loads(request.body)
    nombre = data.get('nombre')
    
    fav, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto_nombre=nombre,
        defaults={
            'producto_precio': data.get('precio', ''),
            'producto_imagen': data.get('imagen', ''),
            'producto_ico':    data.get('ico', ''),
            'producto_tienda': data.get('tienda', ''),
        }
    )
    if not created:
        fav.delete()
        return JsonResponse({'ok': True, 'action': 'removed'})
    
    return JsonResponse({'ok': True, 'action': 'added'})


@login_required
def get_favoritos(request):
    favs = request.user.favoritos.all().values(
        'producto_nombre', 'producto_precio', 'producto_imagen', 'producto_ico', 'producto_tienda'
    )
    return JsonResponse(list(favs), safe=False)


# ─────────────────────────────────────────────
#  REGALOS
# ─────────────────────────────────────────────
def productos_regalo(request):
    CACHE_KEY = f"regalos_{request.GET.get('ocasion','todos')}_{request.GET.get('precio','todos')}"
    data = cache.get(CACHE_KEY)
    if data is None:
        ocasion = request.GET.get("ocasion", "todos")
        precio  = request.GET.get("precio",  "todos")
        qs = (
            Producto.objects
            .exclude(ocasion_regalo="")
            .only("id", "nombre", "precio", "ocasion_regalo", "imagen", "stock")
        )
        if ocasion != "todos":
            qs = qs.filter(ocasion_regalo=ocasion)
        if precio == "50":
            qs = qs.filter(precio__lt=50000)
        elif precio == "50-100":
            qs = qs.filter(precio__gte=50000, precio__lte=100000)
        elif precio == "100":
            qs = qs.filter(precio__gt=100000)
        data = [
            {
                "id":      p.id,
                "nombre":  p.nombre,
                "precio":  p.precio_formateado(),
                "ocasion": p.ocasion_regalo,
                "imagen":  p.imagen.url if p.imagen else "",
                "stock":   p.stock,
            }
            for p in qs
        ]
        cache.set(CACHE_KEY, data, 30)
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

        LABELS = {
            'procesando': 'Procesando',
            'preparando': 'Preparando',
            'en_camino':  'En camino',
            'entregado':  'Entregado',
            'cancelado':  'Cancelado',
        }
        estados_config = list(LABELS.items())

        if tienda:
            context["productos"] = tienda.producto_set.all()
            pedidos = Pedido.objects.filter(
                producto__tienda=tienda
            ).select_related("usuario", "producto").order_by("-fecha")

            for pedido in pedidos:
                pedido.opciones_estado = [
                    {
                        'valor':    valor,
                        'label':    label,
                        'selected': 'selected' if pedido.estado == valor else '',
                    }
                    for valor, label in estados_config
                ]
                pedido.estado_label_txt = LABELS.get(pedido.estado, pedido.estado)

            context["pedidos"] = pedidos

            # ── Stats reales ──
            ventas_qs = Pedido.objects.filter(
                producto__tienda=tienda
            ).exclude(estado="cancelado")
            context["total_ventas"] = ventas_qs.aggregate(
                total=Sum("total")
            )["total"] or 0
            context["total_pedidos"] = pedidos.count()
            context["total_productos"] = tienda.producto_set.count()
        else:
            context["productos"] = []
            context["pedidos"]   = []
            context["total_ventas"] = 0
            context["total_pedidos"] = 0
            context["total_productos"] = 0

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

        cached = cache.get("admin_context")
        if cached is None:
            cached = {}

            cached["vendedores_pendientes"] = list(
                Usuario.objects
                .filter(rol="vendedor", aprobado=False)
                .select_related("tienda")
                .only(
                    "id", "first_name", "last_name", "email", "telefono",
                    "date_joined", "tienda__nombre", "tienda__categoria",
                    "tienda__ubicacion", "tienda__descripcion",
                )
                .order_by("-date_joined")
            )
            cached["todos_pedidos"] = list(
Pedido.objects
    .select_related("usuario", "producto", "producto__tienda")
    .only(
        "id", "estado", "total", "cantidad", "fecha",
        "es_regalo", "direccion_entrega",
        "usuario__id", "usuario__first_name", "usuario__last_name", "usuario__email",
        "producto__id", "producto__nombre",
        "producto__tienda__id", "producto__tienda__nombre",
    )
    .order_by("-fecha")[:200]  # últimos 200 pedidos
)

            cached["todos_usuarios"] = list(
                Usuario.objects
                .select_related("tienda")
                .only(
                    "id", "first_name", "last_name", "email", "rol",
                    "aprobado", "date_joined", "telefono",
                    "tienda__nombre", "tienda__categoria",
                    "tienda__ubicacion", "tienda__descripcion",
                )
                .order_by("-date_joined")
            )

            cached["vendedores_aprobados"] = list(
                Usuario.objects
                .filter(rol="vendedor", aprobado=True)
                .select_related("tienda")
                .prefetch_related(
                    Prefetch(
                        "tienda__producto_set",
                        queryset=Producto.objects.only(
                            "id", "nombre", "precio", "cantidad", "stock",
                            "tienda_id", "categoria", "descripcion",
                            "imagen", "ocasion_regalo",
                        ),
                    )
                )
                .order_by("first_name")
            )

            from django.db.models import Count, Q
            u_stats = Usuario.objects.aggregate(
                total_usuarios=Count("id"),
                total_vendedores_activos=Count("id", filter=Q(rol="vendedor", aprobado=True)),
            )
            cached["total_usuarios"] = u_stats["total_usuarios"]
            cached["total_vendedores_activos"] = u_stats["total_vendedores_activos"]

            p_stats = Pedido.objects.aggregate(
                total_pedidos=Count("id"),
                ventas_totales=Sum("total", filter=~Q(estado="cancelado")),
            )
            cached["total_pedidos_plataforma"] = p_stats["total_pedidos"]
            cached["ventas_totales_plataforma"] = p_stats["ventas_totales"] or 0

            cached["total_productos_publicados"] = Producto.objects.filter(
                tienda__vendedor__aprobado=True
            ).count()

            hoy = timezone.now()
            ventas_por_mes = (
                Pedido.objects
                .filter(fecha__gte=hoy - timezone.timedelta(days=180))
                .exclude(estado="cancelado")
                .annotate(mes=TruncMonth("fecha"))
                .values("mes")
                .annotate(total_mes=Sum("total"))
                .order_by("mes")
            )
            cached["chart_labels"] = json.dumps([e["mes"].strftime("%b") for e in ventas_por_mes])
            cached["chart_valores"] = json.dumps([float(e["total_mes"] or 0) for e in ventas_por_mes])

            cache.set("admin_context", cached, 60)
            

        context.update(cached)
        from django.db import connection
        print(f"\n🔴 TOTAL QUERIES: {len(connection.queries)}")
        for q in connection.queries:
            print(f"  {q['time']}s → {q['sql'][:100]}")
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
            return JsonResponse({"ok": True, "redirect": redirects.get(user.rol, "/")})

        return JsonResponse({"ok": False, "error": "Correo o contraseña incorrectos."})


# ─────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────
class RegistroView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Datos inválidos.'})

        rol = data.get('rol', '').strip()

        if rol not in ('comprador', 'vendedor'):
            return JsonResponse({'ok': False, 'error': 'Rol inválido.'})

        if rol == 'comprador':
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

        if rol == 'vendedor':
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
#  APROBACIÓN DE VENDEDOR
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
            cache.delete("admin_context")  # 👈 agrega esto
            return JsonResponse({"ok": True})
        except Usuario.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Vendedor no encontrado."}, status=404)


class RechazarVendedorView(View):
    def post(self, request, user_id):
        if not request.user.is_authenticated or request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            vendedor = Usuario.objects.get(id=user_id, rol="vendedor")
            if hasattr(vendedor, "tienda"):
                vendedor.tienda.delete()
            vendedor.delete()
            cache.delete("admin_context")  # 👈 agrega esto
            return JsonResponse({"ok": True})
        except Usuario.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Vendedor no encontrado."}, status=404)


# ─────────────────────────────────────────────
#  CREAR PEDIDO
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class CrearPedidoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

        items = body.get("items", [])
        if not items:
            return JsonResponse({"ok": False, "error": "El carrito está vacío"}, status=400)

        es_regalo         = bool(body.get("es_regalo", False))
        regalo_envoltura  = str(body.get("regalo_envoltura", "")).strip()[:30]
        regalo_decoracion = str(body.get("regalo_decoracion", "")).strip()[:30]
        regalo_mensaje    = str(body.get("regalo_mensaje", "")).strip()

        pedidos_creados = []

        for item in items:
            nombre_producto = (item.get("name") or item.get("id") or "").strip()
            cantidad = int(item.get("cantidad", 1))
            precio_raw = item.get("price", "0")
            try:
                precio_num = Decimal(
                    precio_raw.replace("$", "").replace(".", "").replace(",", ".")
                )
            except (InvalidOperation, AttributeError):
                precio_num = Decimal("0")

            total = precio_num * cantidad
            producto_obj = Producto.objects.filter(nombre__iexact=nombre_producto).first()

            pedido = Pedido.objects.create(
                usuario=request.user,
                producto=producto_obj,
                cantidad=cantidad,
                total=total,
                estado="procesando",
                es_regalo=es_regalo,
                regalo_envoltura=regalo_envoltura  if es_regalo else "",
                regalo_decoracion=regalo_decoracion if es_regalo else "",
                regalo_mensaje=regalo_mensaje       if es_regalo else "",
            )
            pedidos_creados.append({
                "id": pedido.id,
                "producto": nombre_producto,
                "cantidad": cantidad,
                "total": str(total),
                "estado": pedido.estado,
                "es_regalo": pedido.es_regalo,
            })

        return JsonResponse({
            "ok": True,
            "pedidos": pedidos_creados,
            "mensaje": f"{len(pedidos_creados)} pedido(s) creado(s) correctamente.",
        })


# ─────────────────────────────────────────────
#  ACTUALIZAR ESTADO DE PEDIDO
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class ActualizarEstadoPedidoView(LoginRequiredMixin, View):
    ESTADOS_VALIDOS = ["procesando", "preparando", "en_camino", "entregado", "cancelado"]

    def patch(self, request, pedido_id):
        try:
            pedido = Pedido.objects.select_related(
                "producto__tienda__vendedor", "usuario"
            ).get(pk=pedido_id)
        except Pedido.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Pedido no encontrado"}, status=404)

        es_admin = request.user.rol == "admin"
        es_vendedor_dueño = (
            request.user.rol == "vendedor"
            and pedido.producto is not None
            and pedido.producto.tienda.vendedor == request.user
        )

        if not (es_admin or es_vendedor_dueño):
            return JsonResponse({"ok": False, "error": "No tienes permiso"}, status=403)

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

        nuevo_estado = body.get("estado", "").strip()
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return JsonResponse({"ok": False, "error": f"Estado inválido. Opciones: {', '.join(self.ESTADOS_VALIDOS)}"}, status=400)

        pedido.estado = nuevo_estado
        pedido.save(update_fields=["estado"])

        return JsonResponse({
            "ok": True,
            "pedido_id": pedido.id,
            "estado": pedido.estado,
            "estado_label": pedido.estado_label(),
        })


# ─────────────────────────────────────────────
#  API PÚBLICA DE PRODUCTOS
# ─────────────────────────────────────────────
def api_productos(request):
    CACHE_KEY = "api_productos_all"
    data = cache.get(CACHE_KEY)
    if data is None:
        productos = (
            Producto.objects
            .select_related("tienda")
            .filter(tienda__vendedor__aprobado=True)
            .only(
                "id", "nombre", "descripcion", "precio",
                "categoria", "stock", "cantidad", "imagen",
                "ocasion_regalo", "tienda_id",
                "tienda__id", "tienda__nombre",
            )
            .order_by("-creado_en")
        )
        data = [
            {
                "id":             p.id,
                "nombre":         p.nombre,
                "descripcion":    p.descripcion,
                "precio":         p.precio_formateado(),
                "precio_num":     float(p.precio),
                "categoria":      p.categoria,
                "stock":          p.stock,
                "cantidad":       p.cantidad,
                "imagen":         p.imagen.url if p.imagen else "",
                "tienda":         p.tienda.nombre,
                "tienda_id":      p.tienda.id,
                "ocasion_regalo": p.ocasion_regalo,
            }
            for p in productos
        ]
        cache.set(CACHE_KEY, data, 60)
    return JsonResponse(data, safe=False)


# ─────────────────────────────────────────────
#  CREAR PRODUCTO (vendedor)
# ─────────────────────────────────────────────
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

        nombre      = request.POST.get("nombre", "").strip()
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

        stock = "out" if cantidad == 0 else "low" if cantidad <= 5 else "high"

        prod = Producto(
            tienda=tienda, nombre=nombre, descripcion=descripcion,
            precio=precio, cantidad=cantidad, stock=stock,
            categoria=categoria, aprobado=True, ocasion_regalo="",
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


# ─────────────────────────────────────────────
#  EDITAR PRODUCTO (vendedor)
# ─────────────────────────────────────────────
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

        if nombre:      prod.nombre = nombre
        if descripcion: prod.descripcion = descripcion
        if precio_raw:
            try:
                prod.precio = Decimal(precio_raw)
            except Exception:
                return JsonResponse({"ok": False, "error": "Precio inválido."}, status=400)
        if cantidad:
            try:
                prod.cantidad = int(cantidad)
                prod.stock = "out" if prod.cantidad == 0 else "low" if prod.cantidad <= 5 else "high"
            except Exception:
                return JsonResponse({"ok": False, "error": "Cantidad inválida."}, status=400)
        if categoria: prod.categoria = categoria
        if imagen:    prod.imagen = imagen
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


# ─────────────────────────────────────────────
#  ELIMINAR PRODUCTO (vendedor)
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  ACTUALIZAR OCASIÓN DE REGALO
# ─────────────────────────────────────────────
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
        except Exception:
            return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)
        prod.ocasion_regalo = body.get('ocasion_regalo', '')
        prod.save(update_fields=['ocasion_regalo'])
        return JsonResponse({"ok": True, "nombre": prod.nombre, "ocasion_regalo": prod.ocasion_regalo})


# ─────────────────────────────────────────────
#  EDITAR PRODUCTO (admin)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class AdminEditarProductoView(LoginRequiredMixin, View):
    def post(self, request, producto_id):
        if request.user.rol != 'admin':
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            prod = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Producto no encontrado."}, status=404)

        nombre      = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        precio_raw  = request.POST.get("precio", "").replace("$","").replace(".","").replace(",",".").strip()
        cantidad    = request.POST.get("cantidad", "").strip()
        categoria   = request.POST.get("categoria", "").strip()
        ocasion     = request.POST.get("ocasion_regalo", "").strip()
        imagen      = request.FILES.get("imagen")

        if nombre:      prod.nombre = nombre
        if descripcion: prod.descripcion = descripcion
        if precio_raw:
            try:    prod.precio = Decimal(precio_raw)
            except: return JsonResponse({"ok": False, "error": "Precio inválido."}, status=400)
        if cantidad:
            try:
                prod.cantidad = int(cantidad)
                prod.stock = "out" if prod.cantidad == 0 else "low" if prod.cantidad <= 5 else "high"
            except: return JsonResponse({"ok": False, "error": "Cantidad inválida."}, status=400)
        if categoria: prod.categoria = categoria
        prod.ocasion_regalo = ocasion
        if imagen:    prod.imagen = imagen
        prod.save()

        return JsonResponse({
            "ok": True, "id": prod.id, "nombre": prod.nombre,
            "precio": prod.precio_formateado(), "cantidad": prod.cantidad,
            "stock": prod.stock, "categoria": prod.categoria,
            "ocasion_regalo": prod.ocasion_regalo,
            "imagen": prod.imagen.url if prod.imagen else "",
        })


# ─────────────────────────────────────────────
#  ELIMINAR PRODUCTO (admin)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class AdminEliminarProductoView(LoginRequiredMixin, View):
    def delete(self, request, producto_id):
        if request.user.rol != 'admin':
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            prod = Producto.objects.get(pk=producto_id)
            nombre = prod.nombre
            prod.delete()
            return JsonResponse({"ok": True, "id": producto_id, "nombre": nombre})
        except Producto.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Producto no encontrado."}, status=404)


# ─────────────────────────────────────────────
#  CREAR PRODUCTO (admin)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class AdminCrearProductoView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.rol != 'admin':
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)

        nombre      = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        precio_raw  = request.POST.get("precio", "0").replace("$","").replace(".","").replace(",",".").strip()
        cantidad    = request.POST.get("cantidad", "0").strip()
        categoria   = request.POST.get("categoria", "").strip()
        ocasion     = request.POST.get("ocasion_regalo", "").strip()
        tienda_id   = request.POST.get("tienda_id", "").strip()
        imagen      = request.FILES.get("imagen")

        if not nombre or not descripcion or not precio_raw or not cantidad or not tienda_id:
            return JsonResponse({"ok": False, "error": "Completa todos los campos."}, status=400)

        try:
            tienda   = Tienda.objects.get(pk=tienda_id)
            precio   = Decimal(precio_raw)
            cantidad = int(cantidad)
        except Exception:
            return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

        stock = "out" if cantidad == 0 else "low" if cantidad <= 5 else "high"

        prod = Producto(
            tienda=tienda, nombre=nombre, descripcion=descripcion,
            precio=precio, cantidad=cantidad, stock=stock,
            categoria=categoria, ocasion_regalo=ocasion, aprobado=True,
        )
        if imagen: prod.imagen = imagen
        prod.save()

        return JsonResponse({
            "ok": True, "id": prod.id, "nombre": prod.nombre,
            "precio": prod.precio_formateado(), "cantidad": prod.cantidad,
            "stock": prod.stock, "categoria": prod.categoria,
            "ocasion_regalo": prod.ocasion_regalo,
            "imagen": prod.imagen.url if prod.imagen else "",
            "tienda": tienda.nombre,
        })


def _invalidar_cache_productos():
    cache.delete("api_productos_all")
    for oc in ["todos", "cumpleanos", "amor", "navidad", "halloween"]:
        for pr in ["todos", "50", "50-100", "100"]:
            cache.delete(f"regalos_{oc}_{pr}")


# ─────────────────────────────────────────────
#  BANNERS
# ─────────────────────────────────────────────
def api_banners(request):
    banners = BannerLanding.objects.filter(activo=True).order_by("orden")
    data = []
    for b in banners:
        if b.imagen:
            imagen_str = str(b.imagen)
            imagen_url = imagen_str if imagen_str.startswith('/static/') else b.imagen.url
        else:
            imagen_url = ""
        data.append({"id": b.id, "orden": b.orden, "imagen": imagen_url, "activo": b.activo})
    return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class AdminBannersView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        banners = BannerLanding.objects.all().order_by("orden")
        data = [{"id": b.id, "orden": b.orden, "imagen": b.imagen.url if b.imagen else "", "activo": b.activo} for b in banners]
        return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class AdminCrearBannerView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        imagen = request.FILES.get("imagen")
        if not imagen:
            return JsonResponse({"ok": False, "error": "Debes subir una imagen."}, status=400)
        orden = BannerLanding.objects.count()
        banner = BannerLanding(orden=orden, activo=True)
        banner.imagen = imagen
        banner.save()
        return JsonResponse({"ok": True, "id": banner.id, "orden": banner.orden, "imagen": banner.imagen.url, "activo": banner.activo})


@method_decorator(csrf_exempt, name="dispatch")
class AdminEditarBannerView(LoginRequiredMixin, View):
    def post(self, request, banner_id):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            banner = BannerLanding.objects.get(pk=banner_id)
        except BannerLanding.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Banner no encontrado."}, status=404)
        imagen = request.FILES.get("imagen")
        if imagen:
            if banner.imagen:
                banner.imagen.delete(save=False)
            banner.imagen = imagen
        activo_raw = request.POST.get("activo")
        if activo_raw is not None:
            banner.activo = activo_raw in ("true", "1", "True")
        banner.save()
        return JsonResponse({"ok": True, "id": banner.id, "orden": banner.orden, "imagen": banner.imagen.url if banner.imagen else "", "activo": banner.activo})


@method_decorator(csrf_exempt, name="dispatch")
class AdminEliminarBannerView(LoginRequiredMixin, View):
    def delete(self, request, banner_id):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            banner = BannerLanding.objects.get(pk=banner_id)
            if banner.imagen:
                banner.imagen.delete(save=False)
            banner.delete()
            for i, b in enumerate(BannerLanding.objects.order_by("orden")):
                if b.orden != i:
                    b.orden = i
                    b.save(update_fields=["orden"])
            return JsonResponse({"ok": True, "id": banner_id})
        except BannerLanding.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Banner no encontrado."}, status=404)


@method_decorator(csrf_exempt, name="dispatch")
class AdminReordenarBannersView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            body = json.loads(request.body)
            ids = body.get("orden", [])
            for i, bid in enumerate(ids):
                BannerLanding.objects.filter(pk=bid).update(orden=i)
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)


# ─────────────────────────────────────────────
#  EDITAR PERFIL
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class EditarPerfilView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

        user = request.user
        nombre   = body.get("nombre", "").strip()
        email    = body.get("email", "").strip()
        telefono = body.get("telefono", "").strip()

        if not nombre or not email:
            return JsonResponse({"ok": False, "error": "Nombre y correo son obligatorios"}, status=400)

        if Usuario.objects.exclude(pk=user.pk).filter(email=email).exists():
            return JsonResponse({"ok": False, "error": "Ese correo ya está en uso"}, status=400)

        partes = nombre.split()
        user.first_name = partes[0]
        user.last_name  = " ".join(partes[1:]) if len(partes) > 1 else ""
        user.email      = email
        user.telefono   = telefono
        user.save(update_fields=["first_name", "last_name", "email", "telefono"])

        return JsonResponse({"ok": True, "nombre": nombre, "email": email, "telefono": telefono})


# ─────────────────────────────────────────────
#  SUBIR FOTO PERFIL
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class SubirFotoPerfilView(LoginRequiredMixin, View):
    def post(self, request):
        imagen = request.FILES.get("imagen")
        if not imagen:
            return JsonResponse({"ok": False, "error": "No se recibió imagen."}, status=400)
        if imagen.size > 5 * 1024 * 1024:
            return JsonResponse({"ok": False, "error": "La imagen supera 5MB."}, status=400)
        user = request.user
        user.foto_perfil = imagen
        user.save(update_fields=["foto_perfil"])
        return JsonResponse({"ok": True, "url": user.foto_perfil.url})


# ─────────────────────────────────────────────
#  DEVOLUCIÓN DE PEDIDO (admin)
# ─────────────────────────────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class AdminDevolucionPedidoView(LoginRequiredMixin, View):
    def post(self, request, pedido_id):
        if request.user.rol != "admin":
            return JsonResponse({"ok": False, "error": "Sin permisos."}, status=403)
        try:
            pedido = Pedido.objects.select_related(
                "usuario", "producto", "producto__tienda"
            ).get(pk=pedido_id)
        except Pedido.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Pedido no encontrado."}, status=404)

        if pedido.estado == "cancelado":
            return JsonResponse({"ok": False, "error": "El pedido ya está cancelado/devuelto."}, status=400)

        estado_anterior = pedido.estado
        pedido.estado = "cancelado"
        pedido.save(update_fields=["estado"])

        # Restituir stock si el producto aún existe
        if pedido.producto:
            prod = pedido.producto
            prod.cantidad += pedido.cantidad
            prod.stock = "out" if prod.cantidad == 0 else "low" if prod.cantidad <= 5 else "high"
            prod.save(update_fields=["cantidad", "stock"])

        return JsonResponse({
            "ok": True,
            "pedido_id": pedido.id,
            "estado_anterior": estado_anterior,
            "estado": pedido.estado,
            "stock_restituido": pedido.cantidad if pedido.producto else 0,
            "producto": pedido.producto.nombre if pedido.producto else "—",
            "usuario": f"{pedido.usuario.first_name} {pedido.usuario.last_name}",
            "total": str(pedido.total),
        })
