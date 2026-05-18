from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # ── Páginas principales ──────────────────────────────
    path("", views.LandingView.as_view(), name="landing"),
    path("comprador/", views.CompradorView.as_view(), name="comprador"),
    path("vendedor/", views.VendedorView.as_view(), name="vendedor"),
    path("admin-pag/", views.AdminView.as_view(), name="admin_pag"),
    path("pendiente/", views.PendienteView.as_view(), name="pendiente"),

    # ── Auth ─────────────────────────────────────────────
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("auth/register/", views.RegistroView.as_view(), name="register"),

    # ── Admin: gestión de vendedores ─────────────────────
    path(
        "admin/aprobar-vendedor/<int:user_id>/",
        views.AprobarVendedorView.as_view(),
        name="aprobar_vendedor",
    ),
    path(
        "admin/rechazar-vendedor/<int:user_id>/",
        views.RechazarVendedorView.as_view(),
        name="rechazar_vendedor",
    ),
]