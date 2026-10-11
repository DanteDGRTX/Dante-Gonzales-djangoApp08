from rest_framework import serializers
from .models import Espacio, RecursoTecnico
import re


class EspacioSerializer(serializers.ModelSerializer):
    recursos_count = serializers.SerializerMethodField()

    class Meta:
        model = Espacio
        fields = ['id', 'nombre', 'ubicacion', 'aforo_maximo', 'estado', 'creado_en', 'actualizado_en', 'recursos_count']
        read_only_fields = ['id', 'creado_en', 'actualizado_en', 'recursos_count']

    def get_recursos_count(self, obj):
        return obj.recursos.count()

    def validate_aforo_maximo(self, value):
        if value <= 0:
            raise serializers.ValidationError('El aforo máximo debe ser mayor que cero.')
        return value


class RecursoTecnicoSerializer(serializers.ModelSerializer):
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    espacio_ubicacion = serializers.CharField(source='espacio.ubicacion', read_only=True)
    espacio_id = serializers.PrimaryKeyRelatedField(
        queryset=Espacio.objects.all(),
        source='espacio',
        write_only=True,
        required=True
    )
    espacio = serializers.IntegerField(source='espacio.id', read_only=True)

    class Meta:
        model = RecursoTecnico
        fields = [
            'id', 'nombre', 'codigo_inventario', 'costo', 'cantidad_stock',
            'espacio_id', 'espacio', 'espacio_nombre', 'espacio_ubicacion',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en', 'espacio_nombre', 'espacio_ubicacion', 'espacio']

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError('El costo no puede ser negativo.')
        return value

    def validate_cantidad_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('La cantidad en stock no puede ser negativa.')
        return value

    def validate_codigo_inventario(self, value):
        # Validate format: alphanumeric with hyphens/underscores
        if not re.match(r'^[A-Z0-9_-]+$', value.upper()):
            raise serializers.ValidationError('El código de inventario solo puede contener letras, números, guiones y guiones bajos.')
        
        # Check for uniqueness (case insensitive)
        queryset = RecursoTecnico.objects.filter(codigo_inventario__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ya existe un recurso con este código de inventario.')
        return value.upper()

    def validate_espacio(self, value):
        if not value:
            raise serializers.ValidationError('El espacio es obligatorio.')
        if not Espacio.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError('El espacio seleccionado no existe.')
        return value