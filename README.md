# CrearQR

Proyecto Django para gestión de turnos y generación/lectura de códigos QR.

## Contenido
- `App_QR/`: aplicación principal (modelos, vistas, plantillas).
- `Sol/`: configuración del proyecto Django.
- `requirements.txt`: dependencias detectadas (`Django==5.2.8`, `qrcode`, `Pillow`).
- `.gitignore`: reglas para excluir `.venv`, bases de datos, IDE, etc.
- `App_QR/static/App_QR/css/`: archivos CSS extraídos de las plantillas.

## Requisitos
- Python 3.14+
- Virtual environment (recomendado)

## Instalación (Windows - PowerShell)
```powershell
# Crear y activar virtualenv
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install -U pip
pip install -r requirements.txt
```

## Configuración rápida
```powershell
# Migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

Acceder en: `http://127.0.0.1:8000/`

## Notas
- Las plantillas tienen los estilos extraídos a `App_QR/static/App_QR/css/`. Asegúrate de tener `django.contrib.staticfiles` en `INSTALLED_APPS` (estándar en el `settings.py` generado).
- Para producción, configure variables de entorno y use un servidor WSGI/ASGI adecuado.
- El proyecto usa `qrcode` y `Pillow` para generar imágenes QR.

## Contribuir
- Añade issues/PRs en el repositorio.
- Sigue el `.gitignore` y no subas la carpeta `.venv` ni archivos de configuración sensibles.

