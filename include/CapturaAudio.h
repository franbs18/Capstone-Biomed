#ifndef AUDIO_CAPTURE_H
#define AUDIO_CAPTURE_H

#include <Arduino.h>
#include <stddef.h>

void inicializarI2S();
void leerMuestrasI2S(int32_t *buffer, size_t num_muestras);

#endif
