# Grabador Fuente MPD - KEY:KID (Android Native)

Versión nativa para Android usando Android Studio y Kotlin. Reproduce exactamente la funcionalidad del script Python.

## Estructura
- `android/`: Proyecto Android completo.
- Copia el binario `N_m3u8DL-RE` (Linux) a `android/src/main/assets/N_m3u8DL-RE`.

## Cómo Usar
1. Abre Android Studio.
2. Importa la carpeta `android/` como proyecto Gradle.
3. Compila e instala en dispositivo/emulador.
4. La app extrae automáticamente el binario al iniciar.

## Notas
- Requiere permisos de almacenamiento e internet.
- Presets se guardan localmente con SharedPreferences.
- Para grabación sin DRM, deja KID/KEY vacíos.