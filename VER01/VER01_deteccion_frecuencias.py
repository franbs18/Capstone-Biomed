"""PRUEBA 1: reproduces tonos por fuera (60, 500 y 1000 Hz) frente al microfono.
El script captura 10 s, detecta los picos de frecuencia y dice cuales de las
frecuencias esperadas aparecen. Funciona con un tono a la vez o con varios juntos.

Cada test guarda:
  Figuras VER01/VER01_test_<DDMMAA>_<frecuencia>.png   (graficos)
  Audios VER01/VER01_test_<DDMMAA>_<frecuencia>.wav    (audio, para volver a graficar)
La <frecuencia> es la(s) frecuencia(s) esperada(s) que se detectaron (ej. 500, o 60-500-1000).
Para fijarla a mano: --nombre-frecuencia 500

Uso (desde la carpeta General):
  python VER01/VER01_deteccion_frecuencias.py
  python VER01/VER01_deteccion_frecuencias.py --puerto COM4 --nombre-frecuencia 500
Volver a ver los graficos:  python VER01/VER01_ver_graficos.py
"""
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import find_peaks
from VER01_comun import (guardar_wav, capturar, espectro_bloque, N_FFT, nombre_test, ruta_figura,
                         graficar_senal_completa, graficar_fft_zoom)

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="COM3")
ap.add_argument("--esperadas", type=float, nargs="+", default=[60, 500, 1000])
ap.add_argument("--tol", type=float, default=5.0, help="tolerancia en Hz")
ap.add_argument("--nombre-frecuencia", help="frecuencia para el nombre del archivo (si no, se usa la detectada)")
args = ap.parse_args()

print("Reproduce el tono ahora... capturando 10 s")
audio, fs, pico_esp, _ = capturar(args.puerto, "S")
print(f"Recibidas {len(audio)} muestras a {fs} Hz")

# Diagnostico: el microfono esta entregando senal?
rango = np.percentile(audio, 99) - np.percentile(audio, 1)
print(f"Muestras: min={audio.min():.0f} max={audio.max():.0f} | primeras 8: {audio[:8].astype(int).tolist()}")
if rango < 4:
    print("\n*** PROBLEMA: la senal esta PLANA (el microfono no entrega audio). Revisa:")
    print("    1) Prueba SLOT_MIC 1 en Configuracion.h (o L/R del INMP441 a GND)")
    print("    2) VDD a 3.3V y GND comun   3) Pines SCK/WS/SD como en Configuracion.h")
    print("    4) Prueba con un aplauso pegado al microfono\n")

# Espectro de toda la grabacion (resolucion ~0.1 Hz)
x = audio - audio.mean()
F = np.fft.rfftfreq(len(x), 1 / fs)
M = np.abs(np.fft.rfft(x * np.hanning(len(x))))
validos = F > 20
piso = np.median(M[validos])

# Picos que sobresalen del ruido (>20x la mediana), separados al menos 30 Hz
idx, _ = find_peaks(np.where(validos, M, 0), height=piso * 20, distance=int(30 / (F[1] - F[0])))
idx = idx[np.argsort(M[idx])[::-1]][:6]
picos = sorted((F[i], M[i] / piso) for i in idx)

print(f"\nPicos detectados: {', '.join(f'{f:.1f} Hz ({q:.0f}x ruido)' for f, q in picos) or 'ninguno'}")
print(f"(ESP32, ultimo bloque de 1024: {pico_esp:.1f} Hz)\n")
detectadas = []
for e in args.esperadas:
    cerca = [(f, q) for f, q in picos if abs(f - e) <= args.tol]
    if cerca:
        detectadas.append(e)
        f, q = cerca[0]
        print(f"  {e:6.0f} Hz -> DETECTADA en {f:.1f} Hz (error {abs(f - e):.2f} Hz)")
    else:
        print(f"  {e:6.0f} Hz -> no aparece")
extras = [f for f, _ in picos if all(abs(f - e) > args.tol for e in args.esperadas)]
if extras:
    print("\nOtros picos (armonicos del parlante o ruido): " + ", ".join(f"{f:.1f} Hz" for f in extras))

# Nombre del test: VER01_test_<DDMMAA>_<frecuencia>
if args.nombre_frecuencia:
    etiqueta = args.nombre_frecuencia
elif detectadas:
    etiqueta = "-".join(f"{e:g}" for e in detectadas)
elif picos:
    etiqueta = f"{max(picos, key=lambda p: p[1])[0]:.0f}"   # el pico mas fuerte
else:
    etiqueta = "sinpico"
nombre = nombre_test(etiqueta)
ruta_wav = guardar_wav(audio, fs, nombre)
ruta_png = ruta_figura(nombre)
print(f"\nTest guardado como '{nombre}':\n  audio  -> {ruta_wav}\n  figura -> {ruta_png}")

XMAX = 1500  # Hz mostrados en el espectrograma (cubre 60, 500 y 1000 Hz)
fig, ax = plt.subplots(4, 1, figsize=(11, 14))

# 0) Senal cruda: los 10 s completos, amplitud normalizada (-1 a 1 = escala completa del microfono)
graficar_senal_completa(ax[0], audio, fs)

# 1) Espectro en magnitud lineal, rango completo: cada pico = una frecuencia presente
ax[1].plot(F, M, lw=0.8, color="tab:blue")
for f, q in picos:
    if f <= 1100:
        ax[1].annotate(f"{f:.1f} Hz", (f, piso * q), textcoords="offset points",
                       xytext=(0, 8), ha="center", color="green", fontweight="bold")
ax[1].set(title="Espectro (FFT) - rango completo", xlabel="Frecuencia (Hz)", ylabel="Magnitud", xlim=(0, 1100))

# 1b) Espectro con zoom en los picos mas fuertes
graficar_fft_zoom(ax[2], F, M)

# 2) Espectrograma: frecuencia vs tiempo (el color es la intensidad)
ax[3].specgram(audio, NFFT=N_FFT, Fs=fs, noverlap=N_FFT // 2, window=np.hamming(N_FFT), cmap="magma")
ax[3].set(title="Espectrograma (frecuencia a lo largo del tiempo)",
          xlabel="Tiempo (s)", ylabel="Frecuencia (Hz)", ylim=(0, XMAX))
fig.suptitle(nombre, fontweight="bold")
plt.tight_layout()
plt.savefig(ruta_png, dpi=110)
plt.show()