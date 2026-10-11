from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Espacio, RecursoTecnico


class EventFlowAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass123')
        
        # Create test spaces
        self.espacio1 = Espacio.objects.create(
            nombre='Auditorio Principal',
            ubicacion='Bloque A',
            aforo_maximo=200,
            estado=Espacio.ESTADO_OPERATIVO
        )
        self.espacio2 = Espacio.objects.create(
            nombre='Sala de Conferencias',
            ubicacion='Bloque B',
            aforo_maximo=50,
            estado=Espacio.ESTADO_MANTENIMIENTO
        )
        
        # Create test resources
        self.recurso1 = RecursoTecnico.objects.create(
            nombre='Proyector Epson',
            codigo_inventario='PROJ-001',
            costo=Decimal('150.00'),
            cantidad_stock=5,
            espacio=self.espacio1
        )
        self.recurso2 = RecursoTecnico.objects.create(
            nombre='Sistema de Audio',
            codigo_inventario='AUD-001',
            costo=Decimal('300.00'),
            cantidad_stock=3,
            espacio=self.espacio1
        )
        self.recurso3 = RecursoTecnico.objects.create(
            nombre='Pantalla LED',
            codigo_inventario='SCR-001',
            costo=Decimal('200.00'),
            cantidad_stock=2,
            espacio=self.espacio2
        )

    def get_token(self, user):
        response = self.client.post('/api/auth/token/', {
            'username': user.username,
            'password': 'testpass123' if user.username == 'testuser' else 'adminpass123'
        }, format='json')
        return response.data.get('access')

    # --- GET público de espacios y recursos ---
    def test_get_espacios_publico(self):
        response = self.client.get('/api/espacios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_recursos_publico(self):
        response = self.client.get('/api/recursos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_espacio_detalle(self):
        response = self.client.get(f'/api/espacios/{self.espacio1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Auditorio Principal')

    def test_get_recurso_detalle(self):
        response = self.client.get(f'/api/recursos/{self.recurso1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Proyector Epson')
        self.assertEqual(response.data['espacio_nombre'], 'Auditorio Principal')

    # --- POST autenticado correcto ---
    def test_post_espacio_autenticado(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Nuevo Espacio',
            'ubicacion': 'Bloque C',
            'aforo_maximo': 100,
            'estado': 'operativo'
        }
        response = self.client.post('/api/espacios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Nuevo Espacio')
        self.assertTrue(Espacio.objects.filter(nombre='Nuevo Espacio').exists())

    def test_post_recurso_autenticado(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Nuevo Recurso',
            'codigo_inventario': 'NEW-001',
            'costo': '100.00',
            'cantidad_stock': 10,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Nuevo Recurso')
        self.assertTrue(RecursoTecnico.objects.filter(codigo_inventario='NEW-001').exists())

    # --- POST anónimo bloqueado ---
    def test_post_espacio_anonimo_bloqueado(self):
        data = {
            'nombre': 'Espacio Anonimo',
            'ubicacion': 'Bloque X',
            'aforo_maximo': 50,
            'estado': 'operativo'
        }
        response = self.client.post('/api/espacios/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_post_recurso_anonimo_bloqueado(self):
        data = {
            'nombre': 'Recurso Anonimo',
            'codigo_inventario': 'ANON-001',
            'costo': '50.00',
            'cantidad_stock': 1,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # --- Validaciones: aforo inválido ---
    def test_post_espacio_aforo_invalido(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Espacio Invalido',
            'ubicacion': 'Bloque X',
            'aforo_maximo': 0,
            'estado': 'operativo'
        }
        response = self.client.post('/api/espacios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('aforo_maximo', response.data)

    def test_post_espacio_aforo_negativo(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Espacio Invalido',
            'ubicacion': 'Bloque X',
            'aforo_maximo': -10,
            'estado': 'operativo'
        }
        response = self.client.post('/api/espacios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('aforo_maximo', response.data)

    # --- Validaciones: costo inválido ---
    def test_post_recurso_costo_invalido(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Recurso Invalido',
            'codigo_inventario': 'INV-001',
            'costo': '-50.00',
            'cantidad_stock': 1,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('costo', response.data)

    def test_post_recurso_cantidad_stock_negativa(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Recurso Invalido',
            'codigo_inventario': 'INV-002',
            'costo': '100.00',
            'cantidad_stock': -5,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cantidad_stock', response.data)

    # --- Validaciones: código de inventario duplicado ---
    def test_post_recurso_codigo_duplicado(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Recurso Duplicado',
            'codigo_inventario': 'PROJ-001',  # Already exists
            'costo': '100.00',
            'cantidad_stock': 1,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('codigo_inventario', response.data)

    def test_post_recurso_codigo_formato_invalido(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Recurso Invalido',
            'codigo_inventario': 'invalid@code!',  # Invalid characters
            'costo': '100.00',
            'cantidad_stock': 1,
            'espacio_id': self.espacio1.id
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('codigo_inventario', response.data)

    # --- Validaciones: espacio inexistente ---
    def test_post_recurso_espacio_inexistente(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Recurso Invalido',
            'codigo_inventario': 'INV-003',
            'costo': '100.00',
            'cantidad_stock': 1,
            'espacio_id': 99999  # Non-existent
        }
        response = self.client.post('/api/recursos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('espacio_id', response.data)

    # --- Actualización y eliminación ---
    def test_put_espacio(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'nombre': 'Auditorio Actualizado',
            'ubicacion': 'Bloque A',
            'aforo_maximo': 250,
            'estado': 'operativo'
        }
        response = self.client.put(f'/api/espacios/{self.espacio1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Auditorio Actualizado')
        self.assertEqual(response.data['aforo_maximo'], 250)

    def test_patch_espacio(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {'aforo_maximo': 300}
        response = self.client.patch(f'/api/espacios/{self.espacio1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aforo_maximo'], 300)

    def test_delete_espacio(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create a new espacio without resources to delete
        espacio_temp = Espacio.objects.create(
            nombre='Espacio Temporal',
            ubicacion='Bloque Z',
            aforo_maximo=10,
            estado='operativo'
        )
        response = self.client.delete(f'/api/espacios/{espacio_temp.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Espacio.objects.filter(id=espacio_temp.id).exists())

    def test_delete_recurso(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.delete(f'/api/recursos/{self.recurso1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RecursoTecnico.objects.filter(id=self.recurso1.id).exists())

    # --- Filtros ---
    def test_filtro_recursos_por_espacio(self):
        response = self.client.get(f'/api/recursos/?espacio={self.espacio1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        for recurso in response.data['results']:
            self.assertEqual(recurso['espacio'], self.espacio1.id)

    def test_filtro_recursos_por_costo_min(self):
        response = self.client.get('/api/recursos/?costo_min=200')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for recurso in response.data['results']:
            self.assertGreaterEqual(Decimal(str(recurso['costo'])), Decimal('200.00'))

    def test_filtro_recursos_por_costo_max(self):
        response = self.client.get('/api/recursos/?costo_max=200')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for recurso in response.data['results']:
            self.assertLessEqual(Decimal(str(recurso['costo'])), Decimal('200.00'))

    def test_filtro_recursos_por_rango_costo(self):
        response = self.client.get('/api/recursos/?costo_min=100&costo_max=250')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for recurso in response.data['results']:
            costo = Decimal(str(recurso['costo']))
            self.assertGreaterEqual(costo, Decimal('100.00'))
            self.assertLessEqual(costo, Decimal('250.00'))

    # --- Protección al eliminar espacio con recursos ---
    def test_delete_espacio_con_recursos_bloqueado(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # espacio1 has 2 resources
        response = self.client.delete(f'/api/espacios/{self.espacio1.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertTrue(Espacio.objects.filter(id=self.espacio1.id).exists())

    # --- ID inexistente ---
    def test_get_espacio_inexistente(self):
        response = self.client.get('/api/espacios/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_recurso_inexistente(self):
        response = self.client.get('/api/recursos/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EventFlowModelTestCase(TestCase):
    def test_espacio_str(self):
        espacio = Espacio.objects.create(
            nombre='Test Espacio',
            ubicacion='Test Ubicacion',
            aforo_maximo=100,
            estado='operativo'
        )
        self.assertEqual(str(espacio), 'Test Espacio (Test Ubicacion)')

    def test_recurso_str(self):
        espacio = Espacio.objects.create(
            nombre='Test Espacio',
            ubicacion='Test Ubicacion',
            aforo_maximo=100,
            estado='operativo'
        )
        recurso = RecursoTecnico.objects.create(
            nombre='Test Recurso',
            codigo_inventario='TEST-001',
            costo=Decimal('100.00'),
            cantidad_stock=5,
            espacio=espacio
        )
        self.assertEqual(str(recurso), 'Test Recurso (TEST-001)')

    def test_espacio_aforo_validation(self):
        espacio = Espacio(
            nombre='Test',
            ubicacion='Test',
            aforo_maximo=0,
            estado='operativo'
        )
        with self.assertRaises(Exception):
            espacio.full_clean()

    def test_recurso_costo_negativo_validation(self):
        espacio = Espacio.objects.create(
            nombre='Test',
            ubicacion='Test',
            aforo_maximo=100,
            estado='operativo'
        )
        recurso = RecursoTecnico(
            nombre='Test',
            codigo_inventario='TEST-001',
            costo=Decimal('-10.00'),
            cantidad_stock=5,
            espacio=espacio
        )
        with self.assertRaises(Exception):
            recurso.full_clean()

    def test_recurso_codigo_inventario_unique(self):
        espacio = Espacio.objects.create(
            nombre='Test',
            ubicacion='Test',
            aforo_maximo=100,
            estado='operativo'
        )
        RecursoTecnico.objects.create(
            nombre='Test 1',
            codigo_inventario='TEST-001',
            costo=Decimal('100.00'),
            cantidad_stock=5,
            espacio=espacio
        )
        recurso2 = RecursoTecnico(
            nombre='Test 2',
            codigo_inventario='TEST-001',
            costo=Decimal('100.00'),
            cantidad_stock=5,
            espacio=espacio
        )
        with self.assertRaises(Exception):
            recurso2.full_clean()