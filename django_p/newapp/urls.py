from django.urls import path
from . import views

urlpatterns = [
    # Aquí puedes añadir tus rutas, por ejemplo:
    # path('ruta/', views.tu_vista, name='nombre_vista'),
    path("", views.index, name="index"),

]
