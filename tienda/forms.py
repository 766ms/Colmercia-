from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Tienda


# ─────────────────────────────────────────────
#  REGISTRO COMPRADOR
# ─────────────────────────────────────────────
class CompradorRegistroForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': 'Tu nombre completo'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'fc',
            'placeholder': 'tu@correo.com'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': '+57 300 000 0000'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'fc',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'fc',
            'placeholder': 'Repite la contraseña'
        })
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'password1', 'password2']

    def clean_email(self):
        """Verifica que el correo no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def clean_password2(self):
        """Verifica que las contraseñas coincidan."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nombre']
        user.telefono = self.cleaned_data.get('telefono', '')
        user.rol = 'comprador'
        user.aprobado = True
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────
#  REGISTRO VENDEDOR
# ─────────────────────────────────────────────
class VendedorRegistroForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': 'Tu nombre completo'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'fc',
            'placeholder': 'tu@correo.com'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': '+57 300 000 0000'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'fc',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'fc',
            'placeholder': 'Repite la contraseña'
        })
    )
    # Datos de tienda
    tienda_nombre = forms.CharField(
        max_length=100,
        label="Nombre de tu tienda",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': 'Mi Tienda ColMercia'
        })
    )
    tienda_desc = forms.CharField(
        required=False,
        label="Descripción de tu tienda",
        widget=forms.Textarea(attrs={
            'class': 'fc',
            'placeholder': 'Cuéntanos qué vendes...',
            'rows': 3
        })
    )
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        label="Ciudad",
        widget=forms.TextInput(attrs={
            'class': 'fc',
            'placeholder': 'Barranquilla'
        })
    )
    categoria = forms.ChoiceField(
        label="Categoría principal",
        required=False,
        choices=[
            ('', 'Selecciona...'),
            ('Maquillaje', 'Maquillaje'),
            ('Ropa y Accesorios', 'Ropa y Accesorios'),
            ('Carteras y Bolsos', 'Carteras y Bolsos'),
            ('Calzado', 'Calzado'),
            ('Papelería', 'Papelería'),
            ('Tecnología', 'Tecnología'),
            ('Regalos', 'Regalos'),
        ],
        widget=forms.Select(attrs={'class': 'fc'})
    )

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'email', 'telefono',
            'tienda_nombre', 'tienda_desc', 'ciudad', 'categoria',
            'password1', 'password2'
        ]

    def clean_email(self):
        """Verifica que el correo no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def clean_password2(self):
        """Verifica que las contraseñas coincidan."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        """Crea el usuario vendedor y su tienda asociada."""
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nombre']
        user.telefono = self.cleaned_data.get('telefono', '')
        user.rol = 'vendedor'
        user.aprobado = False  # Requiere aprobación del admin
        if commit:
            user.save()
            # Crear tienda automáticamente
            Tienda.objects.create(
                vendedor=user,
                nombre=self.cleaned_data.get('tienda_nombre', user.first_name),
                descripcion=self.cleaned_data.get('tienda_desc', ''),
                ubicacion=self.cleaned_data.get('ciudad', ''),
                categoria=self.cleaned_data.get('categoria', ''),
                aprobada=False,
            )
        return user


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'fc',
            'placeholder': 'tu@correo.com'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'fc',
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        """Valida que los campos no estén vacíos."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if not email or not password:
            raise forms.ValidationError("Completa todos los campos.")
        return cleaned_data