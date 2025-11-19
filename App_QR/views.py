from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Turno
from .models import Cliente
from .forms import ClienteForm
import qrcode
from io import BytesIO
import base64

def generar_qr_base64(data):
    """Genera un código QR y lo convierte a base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

def home(request):
    """Vista principal con lista de turnos"""
    turnos_pendientes = Turno.objects.filter(estado='pendiente')
    turnos_en_atencion = Turno.objects.filter(estado='en_atencion')
    turnos_atendidos = Turno.objects.filter(estado='atendido').order_by('-fecha_atencion')[:10]
    
    context = {
        'turnos_pendientes': turnos_pendientes,
        'turnos_en_atencion': turnos_en_atencion,
        'turnos_atendidos': turnos_atendidos,
    }
    return render(request, 'App_QR/home.html', context)

def crear_turno(request):
    """Vista para crear un nuevo turno"""
    cliente_prefill = None
    if request.method == 'POST':
        # If user clicked Buscar por documento
        if 'buscar' in request.POST:
            buscar_documento = (request.POST.get('cliente_documento') or '').strip()
            if not buscar_documento:
                messages.error(request, 'Ingrese un número de documento para buscar.')
            else:
                # Normalizar y buscar coincidencia exacta (case-insensitive)
                cliente_obj = Cliente.objects.filter(documento__iexact=buscar_documento).first()
                # fallback a búsqueda parcial si no hubo exact match
                if not cliente_obj:
                    cliente_obj = Cliente.objects.filter(documento__icontains=buscar_documento).first()

                if cliente_obj:
                    cliente_prefill = {
                        'id': cliente_obj.pk,
                        'nombre': cliente_obj.nombre,
                        'documento': cliente_obj.documento,
                        'email': cliente_obj.email,
                        'telefono': cliente_obj.telefono,
                    }
                    messages.info(request, f'Cliente encontrado: {cliente_obj.nombre}')
                else:
                    messages.error(request, 'Cliente no existe. Por favor verifique el número de documento.')

        # If user clicked Crear Turno
        elif 'crear' in request.POST:
            cliente_id = request.POST.get('cliente_id')
            cliente_nombre = request.POST.get('cliente_nombre')
            cliente_documento = request.POST.get('cliente_documento')
            cliente_email = request.POST.get('cliente_email')
            cliente_telefono = request.POST.get('cliente_telefono')
            servicio = request.POST.get('servicio')
            observaciones = request.POST.get('observaciones')

            turno = Turno.objects.create(
                cliente_documento=cliente_documento,
                cliente_nombre=cliente_nombre,
                cliente_email=cliente_email,
                cliente_telefono=cliente_telefono,
                servicio=servicio,
                observaciones=observaciones
            )
            # asociar FK cliente si se seleccionó uno
            if cliente_id:
                try:
                    cliente_obj = Cliente.objects.get(pk=int(cliente_id))
                    turno.cliente = cliente_obj
                    # opcional: sincronizar campos
                    turno.cliente_nombre = cliente_obj.nombre
                    turno.cliente_documento = cliente_obj.documento
                    turno.cliente_email = cliente_obj.email
                    turno.cliente_telefono = cliente_obj.telefono
                    turno.save()
                except Cliente.DoesNotExist:
                    pass

            messages.success(request, f'Turno {turno.codigo} creado exitosamente')
            return redirect('ver_turno', uuid=turno.uuid)
    
    clientes = Cliente.objects.all().order_by('nombre')
    context = {
        'servicio_choices': Turno.SERVICIO_CHOICES,
        'clientes': clientes,
        'cliente_prefill': cliente_prefill,
    }
    return render(request, 'App_QR/crear_turno.html', context)

def ver_turno(request, uuid):
    """Vista para ver un turno específico con su código QR"""
    turno = get_object_or_404(Turno, uuid=uuid)
    
    # Generar URL completa para el QR
    url_turno = request.build_absolute_uri(f'/turno/{turno.uuid}/')
    qr_code = generar_qr_base64(url_turno)
    
    context = {
        'turno': turno,
        'qr_code': qr_code,
    }
    return render(request, 'App_QR/ver_turno.html', context)

def cambiar_estado_turno(request, uuid, estado):
    """Vista para cambiar el estado de un turno"""
    turno = get_object_or_404(Turno, uuid=uuid)
    
    if estado in ['pendiente', 'en_atencion', 'atendido', 'cancelado']:
        if estado == 'en_atencion':
            turno.marcar_en_atencion()
        elif estado == 'atendido':
            turno.marcar_atendido()
        else:
            turno.estado = estado
            turno.save()
        
        messages.success(request, f'Estado del turno {turno.codigo} actualizado')
    
    return redirect('home')

def descargar_qr(request, uuid):
    """Vista para descargar el código QR como imagen"""
    turno = get_object_or_404(Turno, uuid=uuid)
    
    url_turno = request.build_absolute_uri(f'/turno/{turno.uuid}/')
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_turno)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    response = HttpResponse(content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="turno_{turno.codigo}.png"'
    img.save(response, "PNG")
    
    return response

def pantalla_publica(request):
    """Vista para la pantalla pública que muestra los turnos llamados"""
    turnos_en_atencion = Turno.objects.filter(estado='en_atencion').order_by('fecha_atencion')
    ultimos_atendidos = Turno.objects.filter(estado='atendido').order_by('-fecha_atencion')[:5]
    context = {
        'turnos_en_atencion': turnos_en_atencion,
        'ultimos_atendidos': ultimos_atendidos,
    }
    return render(request, 'App_QR/pantalla_publica.html', context)

def leer_qr(request):
    """Vista que muestra un lector de QR en el navegador y redirige a la URL escaneada."""
    return render(request, 'App_QR/leer_qr.html')


### CRUD Clientes
def cliente_list(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'App_QR/cliente_list.html', {'clientes': clientes})


def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'App_QR/cliente_detail.html', {'cliente': cliente})


def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente creado correctamente')
            return redirect('cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'App_QR/cliente_form.html', {'form': form})


def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado')
            return redirect('cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'App_QR/cliente_form.html', {'form': form, 'cliente': cliente})


def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado')
        return redirect('cliente_list')
    return render(request, 'App_QR/cliente_confirm_delete.html', {'cliente': cliente})
