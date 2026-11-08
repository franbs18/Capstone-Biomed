#include "IndiceVascular.h"
#include "ParametrosIndice.h"
#include <math.h>
#include <string.h>
#include <arduinoFFT.h>

#if (IV_N_FFT & (IV_N_FFT - 1)) != 0
#error "IV_N_FFT debe ser potencia de 2"
#endif

// Buffers de la FFT en float (la FPU del ESP32 es de precision simple: mucho mas rapido que double)
static float ivReal[IV_N_FFT];
static float ivImag[IV_N_FFT];
static float ivVentana[IV_N_FFT];
static ArduinoFFT<float> ivFFT(ivReal, ivImag, IV_N_FFT, (float)IV_FS);

// Estados de los filtros (forma directa II transpuesta, igual que scipy.signal.sosfilt)
static float zBP[IV_N_SOS_BP][2];
static float zLP[IV_N_SOS_LP][2];

// Ultimas IV_N_FFT muestras filtradas (buffer circular) para armar bloques con solape
static float ivHist[IV_N_FFT];
static uint16_t ivPos = 0;            // donde se escribe la proxima muestra (= la mas antigua)
static uint32_t ivMuestras = 0;       // muestras filtradas desde ivReiniciar()

static float ivMag[IV_MAX_BLOQUES];   // A[b]: |X(f)| integrado 50-300 Hz en cada bloque
static uint16_t ivBloques = 0;
static uint16_t kMin = 0, kMax = 0;
static bool ivPreparado = false;

static void ivPreparar() {
    // Hamming identica a numpy.hamming: 0.54 - 0.46 cos(2 pi n / (N - 1))
    for (int n = 0; n < IV_N_FFT; n++)
        ivVentana[n] = (float)(0.54 - 0.46 * cos(2.0 * M_PI * n / (IV_N_FFT - 1)));

    // Bins cuya frecuencia esta dentro de [IV_F_INT_MIN, IV_F_INT_MAX] (4..19 a 16 kHz / 1024)
    const float hzPorBin = (float)IV_FS / IV_N_FFT;
    kMin = 0xFFFF; kMax = 0;
    for (uint16_t k = 0; k <= IV_N_FFT / 2; k++) {
        float f = k * hzPorBin;
        if (f >= IV_F_INT_MIN && f <= IV_F_INT_MAX) {
            if (k < kMin) kMin = k;
            kMax = k;
        }
    }
    ivPreparado = true;
}

static inline float biquad(float x, const float c[5], float z[2]) {
    float y = c[0] * x + z[0];
    z[0] = c[1] * x - c[3] * y + z[1];
    z[1] = c[2] * x - c[4] * y;
    return y;
}

// Un bloque (columna) del espectrograma con las ultimas IV_N_FFT muestras filtradas
static void ivCalcularBloque() {
    if (ivBloques >= IV_MAX_BLOQUES) return; // <-- Freno de seguridad contra crash de memoria

    for (uint16_t i = 0; i < IV_N_FFT; i++) {
        ivReal[i] = ivHist[(ivPos + i) & (IV_N_FFT - 1)] * ivVentana[i];
        ivImag[i] = 0.0f;
    }
    ivFFT.compute(FFTDirection::Forward);

    double a = 0.0;
    for (uint16_t k = kMin; k <= kMax; k++)
        a += sqrtf(ivReal[k] * ivReal[k] + ivImag[k] * ivImag[k]);
    ivMag[ivBloques++] = (float)a;
}

void ivReiniciar() {
    if (!ivPreparado) ivPreparar();
    memset(zBP, 0, sizeof(zBP));
    memset(zLP, 0, sizeof(zLP));
    memset(ivHist, 0, sizeof(ivHist));
    memset(ivMag, 0, sizeof(ivMag));
    ivPos = 0;
    ivMuestras = 0;
    ivBloques = 0;
}

uint16_t ivProcesarMuestras(const int16_t *muestras, uint16_t n) {
    if (!ivPreparado) ivPreparar();
    for (uint16_t i = 0; i < n; i++) {
        // Pasabanda 50-1500 Hz y pasabajo 300 Hz, muestra a muestra (el estado sigue entre lecturas)
        float x = muestras[i] * (1.0f / 32768.0f);
        for (int s = 0; s < IV_N_SOS_BP; s++) x = biquad(x, IV_SOS_BP[s], zBP[s]);
        for (int s = 0; s < IV_N_SOS_LP; s++) x = biquad(x, IV_SOS_LP[s], zLP[s]);

        ivHist[ivPos] = x;
        ivPos = (ivPos + 1) & (IV_N_FFT - 1);
        ivMuestras++;

        // Bloque nuevo cuando ya hay IV_N_FFT muestras y pasaron IV_SALTO desde el anterior
        if (ivMuestras >= IV_N_FFT && ((ivMuestras - IV_N_FFT) % IV_SALTO) == 0 &&
            ivBloques < IV_MAX_BLOQUES)
            ivCalcularBloque();
    }
    return ivBloques;
}

uint16_t ivNumBloques() { return ivBloques; }
const float *ivMagnitudes() { return ivMag; }

float ivMagnitudMedia() {
    int n = (int)ivBloques - IV_BLOQUES_DESCARTE;
    if (n < 1) return 0.0f;
    double suma = 0.0;
    for (int i = IV_BLOQUES_DESCARTE; i < ivBloques; i++) suma += ivMag[i];
    return (float)(suma / n);
}


float ivCalcularHVSI() {
    double hvsi = IV_ESCALA * (double)ivMagnitudMedia() / IV_A_REF;
    if (hvsi < 0.0) hvsi = 0.0;
    if (hvsi > IV_ESCALA) hvsi = IV_ESCALA;   // satura en 999, igual que el HVSI de Hitomi
    return (float)hvsi;
}
