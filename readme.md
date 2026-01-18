# Grabador Fuente MPD - KEY:KID

Aplicación para grabar streams DASH/MPD en vivo, con o sin DRM (usando KEY:KID). Incluye versiones GUI para Windows y consola para Android/Termux.

## Características
- Grabación de streams DASH/MPD.
- Soporte para encriptación DRM (con KEY:KID) o sin ella.
- Gestión de presets múltiples (guardar, cargar, eliminar).
- Borrado automático de archivos incompletos al parar.
- Interfaz GUI en Windows (CustomTkinter).
- Interfaz de consola en Android (Termux).

## Requisitos
- Python 3.7+
- N_m3u8DL-RE (binario, descarga desde [GitHub](https://github.com/nilaoda/N_m3u8DL-RE/releases))

### Dependencias Python
Instala con `pip install -r requisitos.txt`

## Instalación

### Para Windows (GUI)
1. Clona o descarga el repositorio.
2. Instala dependencias: `pip install -r requisitos.txt`
3. Descarga N_m3u8DL-RE.exe (versión Windows) y colócalo en el directorio del proyecto o en el PATH.
4. Ejecuta: `python grabador.py`

### Para Android (Consola via Termux)
1. Instala Termux desde Google Play o F-Droid.
2. En Termux: `pkg update && pkg install python dotnet-runtime`
3. Instala psutil: `pip install psutil`
4. Descarga N_m3u8DL-RE (versión Linux) desde GitHub y colócalo en Termux (ej: `~/N_m3u8DL-RE`).
5. Dale permisos: `chmod +x ~/N_m3u8DL-RE`
6. Copia `android_grabador.py` y `presets.json` (opcional) a Termux.
7. Ejecuta: `python android_grabador.py`

## Uso

### GUI (Windows)
- Ingresa URL, Nombre, KID/KEY (opcional), y selecciona carpeta.
- Presiona "INICIAR GRABACIÓN".
- Usa presets para guardar/cargar configuraciones.
- Presiona "PARAR" para detener (borra archivos incompletos).

### Consola (Android)
- Ejecuta el script y sigue el menú.
- Opción 1: Iniciar grabación (ingresa datos).
- Opción 2: Parar grabación.
- Opciones 3-5: Gestionar presets.
- Opción 6: Salir.

## Notas
- Para streams sin DRM, deja KID/KEY vacíos.
- Los presets se guardan en `presets.json`.
- Asegúrate de que N_m3u8DL-RE tenga permisos de ejecución en Android.
- Si hay errores, verifica que .NET esté instalado en Termux.

## Licencia
Este proyecto es de código abierto. Usa bajo tu responsabilidad.