from django.core.management.base import BaseCommand
from django.db import transaction
from eventflow.models import Espacio, RecursoTecnico
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga datos de demostración para EventFlow (idempotente)'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos de demostración para EventFlow...')
        
        with transaction.atomic():
            # Crear espacios
            espacios_data = [
                {
                    'nombre': 'Auditorio Principal',
                    'ubicacion': 'Bloque A - Planta Baja',
                    'aforo_maximo': 300,
                    'estado': 'operativo'
                },
                {
                    'nombre': 'Sala de Conferencias A',
                    'ubicacion': 'Bloque B - Piso 2',
                    'aforo_maximo': 80,
                    'estado': 'operativo'
                },
                {
                    'nombre': 'Laboratorio de Cómputo',
                    'ubicacion': 'Bloque C - Piso 1',
                    'aforo_maximo': 40,
                    'estado': 'mantenimiento'
                },
                {
                    'nombre': 'Aula Magna',
                    'ubicacion': 'Bloque A - Piso 3',
                    'aforo_maximo': 500,
                    'estado': 'operativo'
                },
                {
                    'nombre': 'Sala de Reuniones',
                    'ubicacion': 'Bloque D - Piso 1',
                    'aforo_maximo': 20,
                    'estado': 'fuera_servicio'
                },
            ]
            
            espacios_creados = {}
            for esp_data in espacios_data:
                espacio, created = Espacio.objects.get_or_create(
                    nombre=esp_data['nombre'],
                    defaults=esp_data
                )
                espacios_creados[esp_data['nombre']] = espacio
                if created:
                    self.stdout.write(f'  [OK] Espacio creado: {espacio.nombre}')
                else:
                    self.stdout.write(f'  → Espacio ya existe: {espacio.nombre}')
            
            # Crear recursos técnicos
            recursos_data = [
                {
                    'nombre': 'Proyector Epson EB-2250U',
                    'codigo_inventario': 'PROJ-EPSON-001',
                    'costo': Decimal('180.00'),
                    'cantidad_stock': 4,
                    'espacio': 'Auditorio Principal'
                },
                {
                    'nombre': 'Sistema de Audio JBL',
                    'codigo_inventario': 'AUD-JBL-001',
                    'costo': Decimal('350.00'),
                    'cantidad_stock': 2,
                    'espacio': 'Auditorio Principal'
                },
                {
                    'nombre': 'Pantalla Motorizada 120"',
                    'codigo_inventario': 'SCR-MOT-001',
                    'costo': Decimal('120.00'),
                    'cantidad_stock': 3,
                    'espacio': 'Auditorio Principal'
                },
                {
                    'nombre': 'Videoconferencia Polycom',
                    'codigo_inventario': 'VC-POLY-001',
                    'costo': Decimal('450.00'),
                    'cantidad_stock': 1,
                    'espacio': 'Sala de Conferencias A'
                },
                {
                    'nombre': 'Pantalla Interactiva 75"',
                    'codigo_inventario': 'SCR-INT-001',
                    'costo': Decimal('280.00'),
                    'cantidad_stock': 2,
                    'espacio': 'Sala de Conferencias A'
                },
                {
                    'nombre': 'Estación de Trabajo Dell',
                    'codigo_inventario': 'WKS-DELL-001',
                    'costo': Decimal('80.00'),
                    'cantidad_stock': 20,
                    'espacio': 'Laboratorio de Cómputo'
                },
                {
                    'nombre': 'Monitor 24" Dell',
                    'codigo_inventario': 'MON-DELL-001',
                    'costo': Decimal('45.00'),
                    'cantidad_stock': 25,
                    'espacio': 'Laboratorio de Cómputo'
                },
                {
                    'nombre': 'Proyector Láser 4K',
                    'codigo_inventario': 'PROJ-LASER-001',
                    'costo': Decimal('600.00'),
                    'cantidad_stock': 1,
                    'espacio': 'Aula Magna'
                },
                {
                    'nombre': 'Sistema de Sonido Line Array',
                    'codigo_inventario': 'AUD-LINE-001',
                    'costo': Decimal('800.00'),
                    'cantidad_stock': 1,
                    'espacio': 'Aula Magna'
                },
                {
                    'nombre': 'Pizarra Digital',
                    'codigo_inventario': 'PB-DIG-001',
                    'costo': Decimal('150.00'),
                    'cantidad_stock': 1,
                    'espacio': 'Sala de Reuniones'
                },
            ]
            
            for rec_data in recursos_data:
                espacio = espacios_creados.get(rec_data['espacio'])
                if not espacio:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Espacio no encontrado: {rec_data["espacio"]}'))
                    continue
                
                recurso, created = RecursoTecnico.objects.get_or_create(
                    codigo_inventario=rec_data['codigo_inventario'],
                    defaults={
                        'nombre': rec_data['nombre'],
                        'costo': rec_data['costo'],
                        'cantidad_stock': rec_data['cantidad_stock'],
                        'espacio': espacio
                    }
                )
                if created:
                    self.stdout.write(f'  [OK] Recurso creado: {recurso.nombre} ({recurso.codigo_inventario})')
                else:
                    self.stdout.write(f'  → Recurso ya existe: {recurso.nombre} ({recurso.codigo_inventario})')
        
        self.stdout.write(self.style.SUCCESS('\nDatos de demostracion cargados correctamente!'))
        self.stdout.write(f'Total espacios: {Espacio.objects.count()}')
        self.stdout.write(f'Total recursos: {RecursoTecnico.objects.count()}')