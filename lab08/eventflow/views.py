from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Espacio, RecursoTecnico
from .serializers import EspacioSerializer, RecursoTecnicoSerializer


class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado']
    search_fields = ['nombre', 'ubicacion']
    ordering_fields = ['nombre', 'ubicacion', 'aforo_maximo', 'creado_en']
    ordering = ['nombre']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if espacio has associated recursos
        if instance.recursos.exists():
            return Response(
                {
                    'error': 'No se puede eliminar el espacio porque tiene recursos técnicos asociados.',
                    'recursos_asociados': list(instance.recursos.values_list('nombre', flat=True))
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class RecursoTecnicoViewSet(viewsets.ModelViewSet):
    queryset = RecursoTecnico.objects.select_related('espacio').all()
    serializer_class = RecursoTecnicoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['espacio', 'espacio__nombre']
    search_fields = ['nombre', 'codigo_inventario']
    ordering_fields = ['nombre', 'costo', 'cantidad_stock', 'creado_en']
    ordering = ['nombre']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by costo range
        costo_min = self.request.query_params.get('costo_min')
        costo_max = self.request.query_params.get('costo_max')
        
        if costo_min is not None:
            try:
                queryset = queryset.filter(costo__gte=costo_min)
            except (ValueError, TypeError):
                pass
        if costo_max is not None:
            try:
                queryset = queryset.filter(costo__lte=costo_max)
            except (ValueError, TypeError):
                pass
        
        # Filter by espacio (by ID or nombre)
        espacio = self.request.query_params.get('espacio')
        if espacio is not None:
            try:
                queryset = queryset.filter(espacio_id=espacio)
            except (ValueError, TypeError):
                # Try filtering by nombre
                queryset = queryset.filter(espacio__nombre__icontains=espacio)
        
        return queryset