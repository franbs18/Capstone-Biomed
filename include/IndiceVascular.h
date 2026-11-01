#ifndef INDICE_VASCULAR_H
#define INDICE_VASCULAR_H

// Indice vascular tipo HVSI (Hitomi et al. 2026) - mismo algoritmo que VER02/VER02_indice.py
//
//  1. Pasabanda Butterworth 50-1500 Hz (orden 4)   -> ruido ambiental / interferencias
//  2. Pasabajo  Butterworth fc = 300 Hz (orden 4)  -> flujo sanguineo (sin valvulas venosas)
//  3. Espectrograma: bloques de 1024 muestras (64 ms, Hamming), uno cada 256 (75 % de solape)
//  4. Valor absoluto |X(f)| integrado entre 50 y 300 Hz en cada bloque -> A[b]
//  5. Promedio de A[b] (sin los bloques de los primeros 64 ms: transitorio de los filtros)
//  6. Normalizacion 0-999 con referencia FIJA: HVSI = 999 * promedio(A) / IV_A_REF (tope 999)
//
// Los filtros y la calibracion IV_A_REF vienen de ParametrosIndice.h, que se GENERA desde Python
// (python VER02/VER02_indice.py --exportar). Este modulo no usa Arduino.h: se puede compilar
// y probar en el computador.

#include <stdint.h>

#define IV_FS                16000     // Hz (debe ser = SAMPLE_RATE)
#define IV_N_FFT             1024      // muestras por bloque (debe ser = NUM_MUESTRAS)
#define IV_SALTO             256       // un bloque nuevo cada 256 muestras (75 % de solape)
#define IV_DURACION_S        10        // s por captura (debe ser = DURACION_S)
#define IV_MAX_LECTURAS      ((IV_FS * IV_DURACION_S + IV_N_FFT - 1) / IV_N_FFT)       // 157
#define IV_MAX_MUESTRAS      ((uint32_t)IV_MAX_LECTURAS * IV_N_FFT)                    // 160768
#define IV_MAX_BLOQUES       ((IV_MAX_MUESTRAS - IV_N_FFT) / IV_SALTO + 1)            // 625

#define IV_F_INT_MIN         50.0f     // Hz: banda que se integra del espectrograma
#define IV_F_INT_MAX         300.0f
#define IV_BLOQUES_DESCARTE  (IV_N_FFT / IV_SALTO)   // 4 bloques = primeros 64 ms
#define IV_ESCALA            999.0f

// Deja los filtros en cero y borra las magnitudes (llamar antes de cada captura)
void ivReiniciar();

// Entrega n muestras int16 nuevas (en orden, sin saltos; tipicamente una lectura I2S de 1024).
// Las filtra y, cada IV_SALTO muestras, calcula un bloque del espectrograma (Hamming + FFT)
// e integra |X(f)| entre 50 y 300 Hz -> A[b]. Devuelve cuantos bloques lleva calculados.
uint16_t ivProcesarMuestras(const int16_t *muestras, uint16_t n);

uint16_t ivNumBloques();            // bloques del espectrograma desde ivReiniciar()
const float *ivMagnitudes();        // A[0..ivNumBloques()-1]
float ivMagnitudMedia();            // promedio de A[b] (sin el transitorio)
float ivCalcularHVSI();             // 999 * promedio / IV_A_REF, entre 0 y 999

#endif
