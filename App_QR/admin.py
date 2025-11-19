from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'email', 'telefono')
    search_fields = ('nombre', 'documento', 'email')

from .models import Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'cliente_nombre', 'servicio', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['codigo', 'cliente_nombre', 'cliente_email', 'cliente_telefono']
    readonly_fields = ['codigo', 'uuid', 'fecha_creacion']
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('codigo', 'uuid', 'estado', 'fecha_creacion', 'fecha_atencion')
        }),
        ('Datos del Cliente', {
            'fields': ('cliente_nombre', 'cliente_email', 'cliente_telefono')
        }),
        ('Servicio', {
            'fields': ('servicio', 'observaciones')
        }),
    )
