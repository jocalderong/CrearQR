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
    # Clientes CRUD
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/crear/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
]
