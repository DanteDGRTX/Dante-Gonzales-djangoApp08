from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EspacioViewSet, RecursoTecnicoViewSet

router = DefaultRouter()
router.register(r'espacios', EspacioViewSet, basename='espacio')
router.register(r'recursos', RecursoTecnicoViewSet, basename='recursotecnico')

urlpatterns = [
    path('', include(router.urls)),
]