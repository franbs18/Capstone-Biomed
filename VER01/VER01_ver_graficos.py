"""VER01 - Vuelve a mostrar los graficos de un test de la PRUEBA 1 a partir de su audio guardado.

Lee el audio de 'Audios VER01/' y guarda la figura en 'Figuras VER01/' con el mismo nombre.

Uso (desde la carpeta General):
  python VER01/VER01_ver_graficos.py                          (ultimo test)
  python VER01/VER01_ver_graficos.py VER01_test_111026_500    (un test en particular)
"""
import glob
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

from VER01_comun import CARPETA_AUDIOS, ruta_figura, graficar_senal_completa, graficar_fft_zoom

if len(sys.argv) > 1:
    ruta = sys.argv[1]
    if not os.path.exists(ruta):                      # se puede dar solo el nombre del test
        ruta = os.path.join(CARPETA_AUDIOS, os.path.splitext(os.path.basename(ruta))[0] + ".wav")
else:
    audios = glob.glob(os.path.join(CARPETA_AUDIOS, "*.wav"))
    if not audios:
        raise SystemExit(f"No hay audios en {CARPETA_AUDIOS}. Corre primero VER01_deteccion_frecuencias.py")
    ruta = max(audios, key=os.path.getmtime)

nombre = os.path.splitext(os.path.basename(ruta))[0]
fs, audio = wavfile.read(ruta)
audio = audio.astype(float)
print("Mostrando:", ruta)

x = audio - audio.mean()
F = np.fft.rfftfreq(len(x), 1 / fs)
M = np.abs(np.fft.rfft(x * np.hanning(len(x))))

fig, ax = plt.subplots(4, 1, figsize=(11, 14))
graficar_senal_completa(ax[0], audio, fs)
ax[1].plot(F, M, lw=0.8)
ax[1].set(title="Espectro (FFT) - rango completo", xlabel="Frecuencia (Hz)", ylabel="Magnitud", xlim=(0, 1100))
graficar_fft_zoom(ax[2], F, M)
ax[3].specgram(audio, NFFT=1024, Fs=fs, noverlap=512, window=np.hamming(1024), cmap="magma")
ax[3].set(title="Espectrograma", xlabel="Tiempo (s)", ylabel="Frecuencia (Hz)", ylim=(0, 1500))
fig.suptitle(nombre, fontweight="bold")
plt.tight_layout()
ruta_png = ruta_figura(nombre)
plt.savefig(ruta_png, dpi=110)
print("Figura guardada en:", ruta_png)
plt.show()
