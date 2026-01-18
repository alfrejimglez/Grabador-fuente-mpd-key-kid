# Grabador Fuente MPD - KEY:KID (Android Native)

Versión nativa para Android usando Android Studio y Kotlin. Reproduce exactamente la funcionalidad del script Python.

## Estructura
- `android/`: Proyecto Android completo (estándar de Android Studio).
  - `build.gradle` (root)
  - `settings.gradle`
  - `app/build.gradle` (app)
  - `app/src/main/...`
- Copia el binario `N_m3u8DL-RE` (Linux) a `android/app/src/main/assets/N_m3u8DL-RE`.

## Cómo Usar
1. Abre Android Studio.
2. Importa la carpeta `android/` como proyecto Gradle existente.
3. Asegúrate de tener el SDK de Android y Kotlin instalados.
4. Compila e instala en dispositivo/emulador (API 24+).
5. La app extrae automáticamente el binario al iniciar.

## Notas
- Requiere permisos de almacenamiento e internet.
- Presets se guardan localmente con SharedPreferences.
- Para grabación sin DRM, deja KID/KEY vacíos.
- Si hay errores de Gradle, verifica las versiones en build.gradle.