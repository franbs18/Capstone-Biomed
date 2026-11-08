#ifndef VASCULAR_INDEX_H
#define VASCULAR_INDEX_H

#include <Arduino.h>
#include <stddef.h>

void generarAudioSintetico(int32_t *buffer, size_t num_muestras);
float calcularFFT(int32_t *buffer, size_t num_muestras);
float calcularIndiceVascular(int32_t *buffer, size_t num_muestras);

#endif
