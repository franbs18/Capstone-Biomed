# Proyecto FAV: estetoscopio digital (ESP32 + INMP441)

Abre **esta carpeta (`General`)** en VS Code con *File → Open Folder*. Todos los comandos de Python se corren desde aquí, en *Terminal → New Terminal*.

## Qué hay en cada carpeta

| Carpeta / archivo | Qué es |
|---|---|
| `platformio.ini`, `src/`, `include/` | **Firmware de la ESP32**. Se sube con PlatformIO (botón → de la barra azul). El puerto está configurado en `platformio.ini` (`upload_port = COM3`) |
| `lib/`, `test/`, `.vscode/` | Archivos automáticos de PlatformIO. No tocar |
| `VER01/` | **Prueba VER.01**: detección de frecuencias (60, 500 y 1000 Hz) |
| `VER01/Figuras VER01/` | Gráficos de cada test, por ejemplo `VER01_test_111026_500.png` (test del 11/10/26 con 500 Hz) |
| `VER01/Audios VER01/` | El audio de cada test, con el mismo nombre que su gráfico |
| `VER02/` | **Prueba VER.02**: índice vascular, ESP32 vs Python. Ver `VER02/PRUEBA_02_LEEME.md` |
| `_antiguos/` | Scripts viejos que ya no se usan. Se pueden borrar |

## VER.01: cómo correrla
```
python VER01/VER01_deteccion_frecuencias.py
```
1. Cuando diga "capturando 10 s", reproduce el tono frente al micrófono.
2. Al terminar, el test queda guardado como `VER01_test_<DDMMAA>_<frecuencia>`, con su gráfico en `Figuras VER01` y su audio en `Audios VER01`.
   - La frecuencia del nombre es la que se detectó. Si quieres fijarla a mano: `--nombre-frecuencia 500`.
   - Si repites el mismo test el mismo día, se guarda como `..._500_2`, `..._500_3`, etc.
3. Si el puerto no es COM3, agrega `--puerto COM4` (o el que corresponda).

Para volver a ver los gráficos de un test:
```
python VER01/VER01_ver_graficos.py                         (el último)
python VER01/VER01_ver_graficos.py VER01_test_111026_500   (uno en particular)
```

Recuerda tener **cerrados Teleplot y el Serial Monitor**: el puerto USB lo puede usar un solo programa a la vez.
