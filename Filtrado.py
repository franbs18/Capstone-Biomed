import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
# Usando los audios sintéticos VER02

ruta_alto_orig = 'VER02/Audios sinteticos VER02/VER02_sintetico_alto.wav'
ruta_alto_exp = 'resultados_captura/audio_alto_20261019_005357.wav'

ruta_medio_orig = 'VER02/Audios sinteticos VER02/VER02_sintetico_alto.wav'
ruta_medio_exp = 'resultados_captura/audio_alto_20261019_005357.wav'

ruta_bajo_orig = 'VER02/Audios sinteticos VER02/VER02_sintetico_alto.wav'
ruta_bajo_exp = 'resultados_captura/audio_alto_20261019_005357.wav'

# i = 1   #  ir cambiando según número de prueba

# alto: VER02_sintetico_alto
# medio: VER02_sintetico_medio
# bajo: VER02_sintetico_bajo

fs_alto_o, data_alto_o = wavfile.read(ruta_alto_orig)
fs_alto_e, data_alto_e = wavfile.read(ruta_alto_exp)

fs_medio_o, data_medio_o = wavfile.read(ruta_medio_orig)
fs_medio_e, data_medio_e = wavfile.read(ruta_medio_exp)

fs_bajo_o, data_bajo_o = wavfile.read(ruta_bajo_orig)
fs_bajo_e, data_bajo_e = wavfile.read(ruta_bajo_exp)

# Si son estéreo, nos quedamos con un canal
if len(data_alto_o.shape) > 1:
  data_o = data_alto_o[:, 0]
if len(data_alto_e.shape) > 1:
  data_alto_e = data_alto_e[:, 0]

# Normalizar al rango [-1.0, 1.0]
data_alto_o = data_alto_o.astype(np.float32) / 32768.0
data_alto_e = data_alto_e.astype(np.float32) / 32768.0

# Alinear la longitud de ambas señales para que coincidan perfectamente en el tiempo
min_len = min(len(data_alto_o), len(data_alto_e))
data_alto_o = data_alto_o[:min_len]
data_alto_e = data_alto_e[:min_len]
tiempo = np.arange(min_len) / fs_alto_o


# ==========================================
# 2. DEFINIR Y APLICAR LOS FILTROS
# ==========================================
def aplicar_pasabanda(data, fs, lowcut=50.0, highcut=1500.0, order=4):
  # Filtro pasabanda para la señal O
  sos = butter(order, [lowcut, highcut], btype="band", fs=fs, output="sos")
  return sosfilt(sos, data)


def aplicar_pasabajo(data, fs, cutoff=300.0, order=4):
  # Filtro pasabajo para la señal E
  sos = butter(order, cutoff, btype="low", fs=fs, output="sos")
  return sosfilt(sos, data)


# Aplicamos los filtros correspondientes
data_o_filtrada = aplicar_pasabajo(aplicar_pasabanda(data_alto_o, fs_alto_o), fs_alto_o)
data_e_filtrada = aplicar_pasabajo(aplicar_pasabanda(data_alto_e, fs_alto_e), fs_alto_e)


# ==========================================
# 3. GUARDAR LOS NUEVOS ARCHIVOS .WAV
# ==========================================
# Convertir de nuevo a enteros de 16 bits (-32768 a 32767) para el archivo WAV
audio_o_16bit = np.int16(np.clip(data_o_filtrada, -1.0, 1.0) * 32767)
audio_e_16bit = np.int16(np.clip(data_e_filtrada, -1.0, 1.0) * 32767)

wavfile.write('audio_alto_o_filtrado.wav', fs_alto_o, audio_o_16bit)
wavfile.write('audio_alto_e_filtrado.wav', fs_alto_e, audio_e_16bit)
print(
    '¡Archivos guardados con éxito como "audio_o_filtrado.wav" y'
    ' "audio_e_filtrado.wav"!'
)



# ==========================================
# 3. CALCULAR LA FFT (ANTES Y DESPUÉS)
# ==========================================
def calcular_fft(data, fs):
  n = len(data)
  yf = fft(data)
  xf = fftfreq(n, 1 / fs)[: n // 2]
  amplitud = 2.0 / n * np.abs(yf[: n // 2])
  return xf, amplitud


# FFT Originales
xf_o_orig, amp_o_orig = calcular_fft(data_alto_o, fs_alto_o)
xf_e_orig, amp_e_orig = calcular_fft(data_alto_e, fs_alto_e)

# FFT Filtradas
xf_o_filt, amp_o_filt = calcular_fft(data_o_filtrada, fs_alto_o)
xf_e_filt, amp_e_filt = calcular_fft(data_e_filtrada, fs_alto_e)


# ==========================================
# 4. GRAFICAR TODO EN UNA SOLA FIGURA (4 Subplots)
# ==========================================
fig, axs = plt.subplots(4, 1, figsize=(12, 14))

# --- Gráfica 1: Señales Originales en el Tiempo ---
axs[0].plot(tiempo, data_alto_o, color="gray", alpha=0.7, label="Señal O (Original)")
axs[0].plot(
    tiempo, data_alto_e, color="darkorange", alpha=0.7, label="Señal E (Original)"
)
axs[0].set_title("1. Señales Originales en el Tiempo")
axs[0].set_xlabel("Tiempo (s)")
axs[0].set_ylabel("Amplitud")
axs[0].legend(loc="upper right")
axs[0].grid(True)

# --- Gráfica 2: Espectro Original (FFT) ---
axs[1].plot(
    xf_o_orig,
    amp_o_orig,
    color="gray",
    alpha=0.7,
    label="FFT O (Original)",
)
axs[1].plot(
    xf_e_orig,
    amp_e_orig,
    color="darkorange",
    alpha=0.7,
    label="FFT E (Original)",
)
axs[1].set_title("2. Espectro de Frecuencias - Señales Originales (FFT)")
axs[1].set_xlabel("Frecuencia (Hz)")
axs[1].set_ylabel("Magnitud")
axs[1].set_xlim(0, 2000)
axs[1].legend(loc="upper right")
axs[1].grid(True)

# --- Gráfica 3: Señales Filtradas en el Tiempo ---
axs[2].plot(
    tiempo,
    data_o_filtrada,
    color="royalblue",
    alpha=0.8,
    label="Señal O (Pasabanda 50-1500 Hz)",
)
axs[2].plot(
    tiempo,
    data_e_filtrada,
    color="crimson",
    alpha=0.8,
    label="Señal E (Pasabajo 300 Hz)",
)
axs[2].set_title("3. Señales Filtradas en el Tiempo")
axs[2].set_xlabel("Tiempo (s)")
axs[2].set_ylabel("Amplitud")
axs[2].legend(loc="upper right")
axs[2].grid(True)

# --- Gráfica 4: Espectro Filtrado (FFT) ---
axs[3].plot(
    xf_o_filt,
    amp_o_filt,
    color="royalblue",
    alpha=0.8,
    label="FFT O (Filtrada Pasabanda)",
)
axs[3].plot(
    xf_e_filt,
    amp_e_filt,
    color="crimson",
    alpha=0.8,
    label="FFT E (Filtrada Pasabajo)",
)
axs[3].set_title("4. Espectro de Frecuencias - Señales Filtradas (FFT)")
axs[3].set_xlabel("Frecuencia (Hz)")
axs[3].set_ylabel("Magnitud")
axs[3].set_xlim(0, 2000)
axs[3].legend(loc="upper right")
axs[3].grid(True)

plt.tight_layout()
plt.show()