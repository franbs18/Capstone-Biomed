"""VER01 - Funciones compartidas de la prueba 1: captura por serial (comandos S/T) y analisis espectral."""
import struct, time, os
from datetime import datetime
import numpy as np
import serial

MAGIC = b"\xA5\x5A\xA5\x5A"
BAUD = 921600
N_FFT = 1024


def _leer_hasta(ser, n):
    """Lee hasta n bytes; si hay timeout devuelve lo que llego."""
    buf = bytearray()
    while len(buf) < n:
        chunk = ser.read(min(n - len(buf), 65536))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)


def capturar(puerto, comando):
    """Envia 'S' (microfono) o 'T' (sintetico). Devuelve (audio, fs, pico_esp, indice_esp)."""
    with serial.Serial(puerto, BAUD, timeout=5) as ser:
        time.sleep(2)               # abrir el puerto reinicia el ESP32
        ser.reset_input_buffer()    # descartar log de arranque
        ser.write(comando.encode())
        ventana = b""
        while ventana != MAGIC:     # resincronizar con la cabecera
            b = ser.read(1)
            if not b:
                raise TimeoutError("No llego la cabecera. Revisa puerto/baudrate/firmware.")
            ventana = (ventana + b)[-4:]
        fs, n = struct.unpack("<II", _leer_hasta(ser, 8))
        esperado = n * 2 + 8        # audio int16 + pico + indice
        datos = _leer_hasta(ser, esperado)

    if len(datos) < esperado:
        print(f"AVISO: llegaron {len(datos)} de {esperado} bytes (faltan {esperado - len(datos)}). "
              "Se usa lo recibido; el valor del ESP32 no esta disponible.")
        datos = datos[: len(datos) // 2 * 2]
        audio = np.frombuffer(datos, dtype="<i2").astype(np.float64)
        return audio, fs, float("nan"), float("nan")

    audio = np.frombuffer(datos[: n * 2], dtype="<i2").astype(np.float64)
    pico, indice = struct.unpack("<ff", datos[n * 2:])
    return audio, fs, pico, indice


def espectro_bloque(x, fs):
    """Igual que el firmware: quita DC, Hamming, FFT, magnitud (bins 0..N/2-1)."""
    x = x - x.mean()
    mag = np.abs(np.fft.rfft(x * np.hamming(len(x))))[: len(x) // 2]
    freqs = np.arange(len(mag)) * fs / len(x)
    return freqs, mag


def indice_vascular(x, fs):
    """Ratio energia(300-1000 Hz) / energia(60-300 Hz), bins desde el 2 (como el firmware)."""
    freqs, mag = espectro_bloque(x, fs)
    idx = np.arange(len(mag))
    bajas = mag[(idx >= 2) & (freqs >= 60) & (freqs < 300)].sum()
    altas = mag[(idx >= 2) & (freqs >= 300) & (freqs <= 1000)].sum()
    return 0.0 if bajas == 0 else altas / bajas


def indices_por_bloque(audio, fs):
    n = len(audio) // N_FFT
    return np.array([indice_vascular(audio[i*N_FFT:(i+1)*N_FFT], fs) for i in range(n)])


def pico_global(audio, fs):
    """Frecuencia dominante usando toda la grabacion (resolucion fina)."""
    x = audio - audio.mean()
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    m = (freqs > 20)
    i = np.argmax(mag * m)
    return freqs[i], mag[i] / np.median(mag[m])   # (frecuencia, relacion pico/mediana)


# ------------------------------- Graficos de la prueba -------------------------------
ESCALA_COMPLETA = 32768.0   # maximo de un int16: amplitud 1.0 = escala completa del microfono
ZOOM_HZ = 20                # margen (Hz) a cada lado de los picos en la FFT con zoom
ZOOM_ANCHO_MAX = 200        # solo se incluyen picos a menos de esta distancia (Hz) del pico mayor
ZOOM_UMBRAL = 0.25          # un pico se considera "fuerte" si mide >= 25 % del pico mayor


def graficar_senal_completa(ax, audio, fs):
    """Captura completa (10 s) con la amplitud normalizada entre -1 y 1."""
    t = np.arange(len(audio)) / fs
    ax.plot(t, audio / ESCALA_COMPLETA, lw=0.4, color="tab:blue")
    ax.set(title=f"Senal cruda del microfono (captura completa, {len(audio) / fs:.1f} s)",
           xlabel="Tiempo (s)", ylabel="Amplitud normalizada\n(1 = escala completa)",
           xlim=(0, len(audio) / fs), ylim=(-1, 1))
    ax.grid(alpha=0.3)


def rango_zoom(F, M, fmin=20):
    """Rango de frecuencias alrededor de los picos mas fuertes del espectro."""
    from scipy.signal import find_peaks
    validos = F > fmin
    Mv = np.where(validos, M, 0)
    i_max = int(np.argmax(Mv))
    idx, _ = find_peaks(Mv, height=ZOOM_UMBRAL * Mv[i_max], distance=max(1, int(5 / (F[1] - F[0]))))
    f_fuertes = np.append(F[idx], F[i_max])
    f_fuertes = f_fuertes[np.abs(f_fuertes - F[i_max]) <= ZOOM_ANCHO_MAX]   # vecinos del pico mayor
    lo, hi = f_fuertes.min(), f_fuertes.max()
    return max(0.0, lo - ZOOM_HZ), hi + ZOOM_HZ, F[i_max]


def graficar_fft_zoom(ax, F, M):
    """FFT ampliada alrededor de los picos mas fuertes, con la frecuencia exacta del mayor."""
    lo, hi, f_max = rango_zoom(F, M)
    sel = (F >= lo) & (F <= hi)
    ax.plot(F[sel], M[sel], lw=1.0, color="tab:blue")
    i = np.argmax(np.where(sel, M, 0))
    ax.annotate(f"{F[i]:.2f} Hz", (F[i], M[i]), textcoords="offset points", xytext=(8, -4),
                color="green", fontweight="bold")
    ax.set(title=f"Espectro (FFT) - zoom en los picos principales ({lo:.0f}-{hi:.0f} Hz)",
           xlabel="Frecuencia (Hz)", ylabel="Magnitud", xlim=(lo, hi))
    ax.grid(alpha=0.3)


# Carpetas de resultados de la prueba VER01 (dentro de General/VER01/)
CARPETA_VER01 = os.path.dirname(os.path.abspath(__file__))
CARPETA_AUDIOS = os.path.join(CARPETA_VER01, "Audios VER01")
CARPETA_FIGURAS = os.path.join(CARPETA_VER01, "Figuras VER01")


def nombre_test(etiqueta_frecuencia):
    """Nombre del test: VER01_test_<DDMMAA>_<frecuencia>, ej. VER01_test_111026_500.
    Si ese nombre ya existe (mismo dia y frecuencia), agrega _2, _3, ..."""
    base = f"VER01_test_{datetime.now():%d%m%y}_{etiqueta_frecuencia}"
    nombre, k = base, 2
    while (os.path.exists(os.path.join(CARPETA_AUDIOS, nombre + ".wav")) or
           os.path.exists(os.path.join(CARPETA_FIGURAS, nombre + ".png"))):
        nombre, k = f"{base}_{k}", k + 1
    return nombre


def guardar_wav(audio, fs, nombre):
    """Guarda el audio como WAV mono de 16 bits en 'Audios VER01/<nombre>.wav'."""
    from scipy.io import wavfile
    os.makedirs(CARPETA_AUDIOS, exist_ok=True)
    ruta = os.path.join(CARPETA_AUDIOS, nombre + ".wav")
    wavfile.write(ruta, int(fs), np.clip(audio, -32768, 32767).astype(np.int16))
    return ruta


def ruta_figura(nombre):
    """Ruta 'Figuras VER01/<nombre>.png' (crea la carpeta si no existe)."""
    os.makedirs(CARPETA_FIGURAS, exist_ok=True)
    return os.path.join(CARPETA_FIGURAS, nombre + ".png")