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

    # ── Pedidos ──────────────────────────────────────────
    path("pedidos/crear/", views.CrearPedidoView.as_view(), name="crear_pedido"),
    path("pedidos/<int:pedido_id>/estado/",
         views.ActualizarEstadoPedidoView.as_view(), name="actualizar_estado_pedido"),

    # ── Admin: gestión de vendedores ─────────────────────
    path("admin-pag/aprobar-vendedor/<int:user_id>/",
         views.AprobarVendedorView.as_view(), name="aprobar_vendedor"),
    path("admin-pag/rechazar-vendedor/<int:user_id>/",
         views.RechazarVendedorView.as_view(), name="rechazar_vendedor"),

    # ── API pública ───────────────────────────────────────
    path("api/regalos/", views.productos_regalo, name="productos_regalo"),
    path("api/productos/", views.api_productos, name="api_productos"),
    path("api/banners/", views.api_banners, name="api_banners"),

    # ── Gestión de Productos (vendedor) ──────────────────
    path("productos/nuevo/",
         views.CrearProductoView.as_view(), name="crear_producto"),
    path("productos/<int:producto_id>/editar/",
         views.EditarProductoView.as_view(), name="editar_producto"),
    path("productos/<int:producto_id>/eliminar/",
         views.EliminarProductoView.as_view(), name="eliminar_producto"),
    path("productos/<int:producto_id>/ocasion/",
         views.ActualizarOcasionRegaloView.as_view(), name="actualizar_ocasion_regalo"),

    # ── Admin: gestión de productos ───────────────────────
    path("admin-pag/productos/crear/",
         views.AdminCrearProductoView.as_view(), name="admin_crear_producto"),
    path("admin-pag/productos/<int:producto_id>/editar/",
         views.AdminEditarProductoView.as_view(), name="admin_editar_producto"),
    path("admin-pag/productos/<int:producto_id>/eliminar/",
         views.AdminEliminarProductoView.as_view(), name="admin_eliminar_producto"),

    # ── Admin: CRUD banners ───────────────────────────────
    path("admin-pag/banners/",
         views.AdminBannersView.as_view(), name="admin_banners"),
    path("admin-pag/banners/crear/",
         views.AdminCrearBannerView.as_view(), name="admin_crear_banner"),
    path("admin-pag/banners/<int:banner_id>/editar/",
         views.AdminEditarBannerView.as_view(), name="admin_editar_banner"),
    path("admin-pag/banners/<int:banner_id>/eliminar/",
         views.AdminEliminarBannerView.as_view(), name="admin_eliminar_banner"),
    path("admin-pag/banners/reordenar/",
         views.AdminReordenarBannersView.as_view(), name="admin_reordenar_banners"),
    path("perfil/editar/", views.EditarPerfilView.as_view(), name="editar_perfil"),
    path("perfil/foto/", views.SubirFotoPerfilView.as_view(), name="subir_foto_perfil"),
]