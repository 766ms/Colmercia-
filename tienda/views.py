import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from .models import Pedido, Tienda, Usuario


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