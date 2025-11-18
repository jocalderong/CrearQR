from django.db import models
from django.utils import timezone
import uuid

class Turno(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_atencion', 'En Atención'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
    ]

    SERVICIO_CHOICES = [
        ('facturacion', 'Facturación'),
        ('servicio_medico', 'Servicio Médico'),
        ('farmacia', 'Farmacia'),
        ('general', 'General'),
        ('historia_clinica', 'Historia Clínica'),
    ]

    SERVICIO_PREFIXES = {
        'facturacion': 'F',
        'servicio_medico': 'M',
        'farmacia': 'P',
        'general': 'G',
        'historia_clinica': 'H',
    }
    
    codigo = models.CharField(max_length=10, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cliente_nombre = models.CharField(max_length=200)
    cliente_documento = models.CharField(max_length=20, blank=True, null=True)
    cliente_email = models.EmailField(blank=True, null=True)
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True)
    servicio = models.CharField(max_length=50, choices=SERVICIO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_atencion = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
    
    def __str__(self):
        return f"{self.codigo} - {self.cliente_nombre}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código de turno consecutivo por servicio y día
            prefix = self.SERVICIO_PREFIXES.get(self.servicio, 'T')
            ultimo_turno = Turno.objects.filter(
                fecha_creacion__date=timezone.now().date(),
                servicio=self.servicio
            ).order_by('-id').first()
            
            if ultimo_turno and ultimo_turno.codigo:
                try:
                    numero = int(ultimo_turno.codigo.split('-')[1]) + 1
                except:
                    numero = 1
            else:
                numero = 1
            self.codigo = f"{prefix}-{numero:03d}"
        
        super().save(*args, **kwargs)
    
    def marcar_en_atencion(self):
        self.estado = 'en_atencion'
        self.fecha_atencion = timezone.now()
        self.save()
    
    def marcar_atendido(self):
        self.estado = 'atendido'
        self.save()
