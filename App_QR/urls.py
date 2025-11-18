from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_turno, name='crear_turno'),
    path('turno/<uuid:uuid>/', views.ver_turno, name='ver_turno'),
    path('turno/<uuid:uuid>/estado/<str:estado>/', views.cambiar_estado_turno, name='cambiar_estado'),
    path('turno/<uuid:uuid>/descargar-qr/', views.descargar_qr, name='descargar_qr'),
    path('pantalla/', views.pantalla_publica, name='pantalla_publica'),
    path('leer-qr/', views.leer_qr, name='leer_qr'),
]
