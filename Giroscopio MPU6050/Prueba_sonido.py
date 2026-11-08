import os
import struct
import time
import matplotlib.pyplot as plt
import numpy as np
import serial

# --- CONFIGURACIÓN ---
PUERTO = "/dev/cu.usbserial-0001"
BAUDRATE = 921600
NOMBRE_CARPETA = "resultados_captura"

# Crear la carpeta de salida si no existe
os.makedirs(NOMBRE_CARPETA, exist_ok=True)

queaudio = '_alto'

# Generar marcas de tiempo para que los archivos tengan nombres únicos
timestamp = time.strftime("%Y%m%d_%H%M%S")
path_wav = os.path.join(NOMBRE_CARPETA, f"audio{queaudio}_{timestamp}.wav")
path_png = os.path.join(NOMBRE_CARPETA, f"grafico{queaudio}_{timestamp}.png")

print(f"Conectando al puerto {PUERTO}...")
ser = serial.Serial(PUERTO, BAUDRATE, timeout=15)

time.sleep(2)
ser.reset_input_buffer()

print("Enviando comando 'S' a la ESP32...")
ser.write(b"S")

# 1. Sincronización por Magic Bytes
magic_target = b"\xa5\x5a\xa5\x5a"
buffer_recibido = bytearray()

print("Buscando cabecera...")
while True:
  byte_actual = ser.read(1)
  if not byte_actual:
    print("Error: Timeout buscando la cabecera.")
    ser.close()
    exit()
  buffer_recibido.extend(byte_actual)
  if len(buffer_recibido) > 4:
    buffer_recibido.pop(0)
  if bytes(buffer_recibido) == magic_target:
    print("¡Cabecera sincronizada con éxito!")
    break

# 2. Leer configuración
fs = struct.unpack("<I", ser.read(4))[0]
n_muestras = struct.unpack("<I", ser.read(4))[0]

# 3. Leer audio completo
bytes_totales_esperados = n_muestras * 2
bytes_audio = bytearray()

print("Leyendo bloques de audio desde la ESP32...")
while len(bytes_audio) < bytes_totales_esperados:
  chunk = ser.read(bytes_totales_esperados - len(bytes_audio))
  if not chunk:
    break
  bytes_audio.extend(chunk)
# 201910 50% con parlante
# 4. Leer resultados de la ESP32
pico = struct.unpack("<f", ser.read(4))[0]
indice = struct.unpack("<f", ser.read(4))[0]

print(f"\n--- Resultados devueltos por la ESP32 ---")
print(f"Pico FFT calculado en placa: {pico:.2f} Hz")
print(f"Índice Vascular calculado en placa: {indice:.2f}")

ser.close()

# Procesamiento de datos
audio_16bit = np.frombuffer(bytes_audio, dtype=np.int16)

# --- GUARDAR ARCHIVO DE AUDIO (.WAV) ---
import wave

with wave.open(path_wav, "w") as wf:
  wf.setnchannels(1)  # Mono
  wf.setsampwidth(2)  # 2 bytes (16 bits)
  wf.setframerate(fs)
  wf.writeframes(audio_16bit.tobytes())
print(f"Archivo de audio guardado en: {path_wav}")

# Omitir el primer 0.5 segundo para eliminar el transitorio inicial
corte_muestras = int(fs * 0.5)
audio_limpio = audio_16bit[corte_muestras:]
tiempo_limpio = np.arange(len(audio_limpio)) / fs + 0.5

# Normalizar la amplitud entre -1 y 1 para visualización
audio_normalizado = audio_limpio / 32768.0

# FFT de la señal limpia
fft_vals = np.fft.rfft(audio_limpio)
fft_freqs = np.fft.rfftfreq(len(audio_limpio), 1 / fs)
fft_mag = np.abs(fft_vals) / len(audio_limpio)

# --- GRAFICACIÓN (3 Subplots: Tiempo, FFT y Espectrograma) ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# 1. Gráfica en el tiempo (normalizada)
ax1.plot(tiempo_limpio, audio_normalizado, color="royalblue", linewidth=0.5)
ax1.set_title(
    "Señal de Audio Estable (Normalizada) - Sin transitorio inicial"
)
ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Amplitud (-1 a 1)")
ax1.grid(True)
ax1.set_ylim(-1.1, 1.1)

# 2. Espectro de Frecuencias (FFT) con zoom a 2000 Hz
ax2.plot(fft_freqs, fft_mag, color="crimson", linewidth=0.8)
ax2.set_title("Espectro de Frecuencias (FFT)")
ax2.set_xlabel("Frecuencia (Hz)")
ax2.set_ylabel("Magnitud")
ax2.grid(True)
ax2.set_xlim(0, 2000)

# 3. Espectrograma con zoom a 2000 Hz
Pxx, freqs, bins, im = ax3.specgram(
    audio_limpio, NFFT=1024, Fs=fs, noverlap=512, cmap="inferno"
)
ax3.set_title("Espectrograma (Frecuencia vs Tiempo)")
ax3.set_xlabel("Tiempo (s)")
ax3.set_ylabel("Frecuencia (Hz)")
ax3.set_ylim(0, 2000)
fig.colorbar(im, ax=ax3, label="Intensidad (dB)")

plt.tight_layout()

# --- GUARDAR IMAGEN DEL GRÁFICO (.PNG) ---
plt.savefig(path_png, dpi=300)
print(f"Imagen del gráfico guardada en: {path_png}")

plt.show()