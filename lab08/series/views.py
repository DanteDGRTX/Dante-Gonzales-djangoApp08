from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Serie
from .serializers import SerieSerializer


class IndexView(APIView):
    def get(self, request):
        return Response({"mensaje": "servidor activo"})


class SeriesView(APIView):
    def get(self, request):
        series = Serie.objects.all()
        serializer = SerieSerializer(series, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SerieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SerieDetailView(APIView):
    def get_object(self, serie_id):
        try:
            return Serie.objects.get(pk=serie_id)
        except Serie.DoesNotExist:
            return None

    def get(self, request, serie_id):
        serie = self.get_object(serie_id)
        if serie is None:
            return Response({"error": "Serie no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SerieSerializer(serie)
        return Response(serializer.data)

    def put(self, request, serie_id):
        serie = self.get_object(serie_id)
        if serie is None:
            return Response({"error": "Serie no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SerieSerializer(serie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, serie_id):
        serie = self.get_object(serie_id)
        if serie is None:
            return Response({"error": "Serie no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)