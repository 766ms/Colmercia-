import pytest
from django.test import Client
from django.urls import reverse

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
class TestURLs:

    def test_landing_ok(self, client):
        response = client.get(reverse('landing'))
        assert response.status_code == 200

    def test_admin_redirige_si_no_logueado(self, client):
        response = client.get(reverse('admin_pag'))
        assert response.status_code == 302

    def test_vendedor_redirige_si_no_logueado(self, client):
        response = client.get(reverse('vendedor'))
        assert response.status_code == 302

    def test_comprador_redirige_si_no_logueado(self, client):
        response = client.get(reverse('comprador'))
        assert response.status_code == 302

    def test_api_productos_ok(self, client):
        response = client.get(reverse('api_productos'))
        assert response.status_code == 200

    def test_api_banners_ok(self, client):
        response = client.get(reverse('api_banners'))
        assert response.status_code == 200

@pytest.mark.django_db
class TestLogin:

    def test_login_credenciales_incorrectas(self, client):
        response = client.post(
            reverse('login'),
            data='{"email":"noexiste@x.com","password":"mal"}',
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] == False

    def test_login_comprador(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username='compradortest',
            email='comprador@test.com',
            password='test1234',
        )
        user.rol = 'comprador'
        user.aprobado = True
        user.save()

        response = client.post(
            reverse('login'),
            data='{"email":"comprador@test.com","password":"test1234"}',
            content_type='application/json'
        )
        data = response.json()
        assert data['ok'] == True
        assert data['redirect'] == '/comprador/'

    def test_login_admin(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username='admintest',
            email='admin@test.com',
            password='test1234',
        )
        user.rol = 'admin'
        user.aprobado = True
        user.save()

        response = client.post(
            reverse('login'),
            data='{"email":"admin@test.com","password":"test1234"}',
            content_type='application/json'
        )
        data = response.json()
        assert data['ok'] == True
        assert data['redirect'] == '/admin-pag/'