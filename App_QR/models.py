from django.db import models
from django.utils import timezone
import uuid


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    documento = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    foto = models.ImageField(upload_to='clientes/fotos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} ({self.documento})" if self.documento else self.nombre

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
    # optional link to Cliente; keep denormalized fields for compatibility
    cliente = models.ForeignKey(Cliente, blank=True, null=True, on_delete=models.SET_NULL)
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
        from django.db import IntegrityError, transaction

        if not self.codigo:
            # Generar código de turno consecutivo por servicio y día.
            # Intentamos evitar colisiones reintentando si hay conflicto único.
            prefix = self.SERVICIO_PREFIXES.get(self.servicio, 'T')

            # Hacemos varios intentos incrementando el número si se detecta un IntegrityError
            for attempt in range(5):
                # base count de turnos existentes hoy para este servicio
                base = Turno.objects.filter(
                    fecha_creacion__date=timezone.now().date(),
                    servicio=self.servicio
                ).count()
                numero = base + 1 + attempt
                self.codigo = f"{prefix}-{numero:03d}"
                try:
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    # intentar siguiente número
                    continue
            # Si los reintentos fallaron, hacer un último save y dejar que la excepción suba
        super().save(*args, **kwargs)
    
    def marcar_en_atencion(self):
        self.estado = 'en_atencion'
        self.fecha_atencion = timezone.now()
        self.save()
    
    def marcar_atendido(self):
        self.estado = 'atendido'
        self.save()
