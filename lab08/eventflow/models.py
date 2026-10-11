from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Espacio(models.Model):
    ESTADO_OPERATIVO = 'operativo'
    ESTADO_MANTENIMIENTO = 'mantenimiento'
    ESTADO_FUERA_SERVICIO = 'fuera_servicio'

    ESTADO_CHOICES = [
        (ESTADO_OPERATIVO, 'Operativo'),
        (ESTADO_MANTENIMIENTO, 'Mantenimiento'),
        (ESTADO_FUERA_SERVICIO, 'Fuera de servicio'),
    ]

    nombre = models.CharField(max_length=100, verbose_name='Nombre del área')
    ubicacion = models.CharField(max_length=100, verbose_name='Ubicación o bloque')
    aforo_maximo = models.PositiveIntegerField(
        verbose_name='Aforo máximo',
        validators=[MinValueValidator(1)]
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_OPERATIVO,
        verbose_name='Estado operativo'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.ubicacion})'

    def clean(self):
        if self.aforo_maximo is not None and self.aforo_maximo <= 0:
            raise ValidationError({'aforo_maximo': 'El aforo máximo debe ser mayor que cero.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RecursoTecnico(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del equipo')
    codigo_inventario = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código de inventario'
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Costo de alquiler/mantenimiento',
        validators=[MinValueValidator(0)]
    )
    cantidad_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad en stock',
        validators=[MinValueValidator(0)]
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.PROTECT,
        related_name='recursos',
        verbose_name='Espacio asignado'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recurso técnico'
        verbose_name_plural = 'Recursos técnicos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.codigo_inventario})'

    def clean(self):
        if self.costo is not None and self.costo < 0:
            raise ValidationError({'costo': 'El costo no puede ser negativo.'})
        if self.cantidad_stock is not None and self.cantidad_stock < 0:
            raise ValidationError({'cantidad_stock': 'La cantidad en stock no puede ser negativa.'})
        if self.codigo_inventario:
            # Validate format: alphanumeric with hyphens/underscores
            import re
            if not re.match(r'^[A-Z0-9_-]+$', self.codigo_inventario.upper()):
                raise ValidationError({'codigo_inventario': 'El código de inventario solo puede contener letras, números, guiones y guiones bajos.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)