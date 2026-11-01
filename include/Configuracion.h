#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <driver/i2s.h>

// Pines INMP441 -> ESP32 (L/R del INMP441 conectado a GND = canal izquierdo)
#define I2S_BCK_PIN   5   // SCK  (PROBABLE: confirmar con escaneo_pines.py)
#define I2S_WS_PIN    18  // WS   (confirmado por escaner)
#define I2S_SD_PIN    19  // SD   (confirmado por escaner)

// Parametros de audio
// Slot del par estereo donde llega el microfono: 0 = izquierdo (L/R a GND), 1 = derecho.
// Si la senal sale plana, prueba cambiarlo.
#define SLOT_MIC      0

#define SAMPLE_RATE   16000  // Nyquist = 8 kHz
#define NUM_MUESTRAS  1024   // Resolucion de la FFT (15.625 Hz por bin a 16 kHz)
#define DURACION_S    10     // Segundos por captura
#define BAUDRATE      921600 // Debe coincidir con los scripts de Python

#endif