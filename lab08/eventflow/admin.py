from django.contrib import admin
from .models import Espacio, RecursoTecnico


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'aforo_maximo', 'estado', 'creado_en']
    list_filter = ['estado', 'creado_en']
    search_fields = ['nombre', 'ubicacion']
    ordering = ['nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'ubicacion')
        }),
        ('Capacidad y estado', {
            'fields': ('aforo_maximo', 'estado')
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecursoTecnico)
class RecursoTecnicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_inventario', 'costo', 'cantidad_stock', 'espacio', 'creado_en']
    list_filter = ['espacio', 'creado_en']
    search_fields = ['nombre', 'codigo_inventario', 'espacio__nombre']
    ordering = ['nombre']
    readonly_fields = ['creado_en', 'actualizado_en']
    raw_id_fields = ['espacio']
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'codigo_inventario')
        }),
        ('Costos y stock', {
            'fields': ('costo', 'cantidad_stock')
        }),
        ('Asignación', {
            'fields': ('espacio',)
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )