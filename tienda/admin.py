from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Tienda, Producto, BannerLanding, Pedido, Favorito

@admin.register(BannerLanding)
class BannerLandingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'titulo', 'orden', 'activo']
    list_editable = ['orden', 'activo']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tienda', 'precio', 'stock', 'aprobado', 'seccion_landing']
    list_editable = ['aprobado', 'seccion_landing']
    list_filter = ['aprobado', 'seccion_landing', 'categoria']

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'username', 'rol', 'aprobado']
    list_filter = ['rol', 'aprobado']

admin.site.register(Tienda)
admin.site.register(Pedido)
admin.site.register(Favorito)