#include <Arduino.h>
#include "Configuracion.h"
#include "CapturaAudio.h"
#include "IndiceVascular.h"

// El modulo del indice vascular tiene sus propios parametros: deben coincidir con los de captura
static_assert(IV_FS == SAMPLE_RATE, "IV_FS (IndiceVascular.h) debe ser igual a SAMPLE_RATE");
static_assert(IV_N_FFT == NUM_MUESTRAS, "IV_N_FFT (IndiceVascular.h) debe ser igual a NUM_MUESTRAS");
static_assert(IV_DURACION_S == DURACION_S, "IV_DURACION_S (IndiceVascular.h) debe ser igual a DURACION_S");

const int TOTAL_BLOQUES = ((uint32_t)SAMPLE_RATE * DURACION_S + NUM_MUESTRAS - 1) / NUM_MUESTRAS;
int32_t bufferCaptura[NUM_MUESTRAS];
int16_t bufferTx[NUM_MUESTRAS];   // lo que se envia por serial (16 bits)

// Protocolo compatible con tu Python original:
// [magic 4B: A5 5A A5 5A][fs uint32][n_muestras uint32][n * int16 audio][magMedia float][indiceHVSI float]
void ejecutarCaptura() {
    // Descartar audio viejo acumulado en el DMA mientras esperabamos el comando
    for (int i = 0; i < 5; i++) leerMuestrasI2S(bufferCaptura, NUM_MUESTRAS);

    ivReiniciar();

    const uint8_t magic[4] = {0xA5, 0x5A, 0xA5, 0x5A};
    uint32_t fs = SAMPLE_RATE;
    uint32_t n  = (uint32_t)TOTAL_BLOQUES * NUM_MUESTRAS;
    Serial.write(magic, 4);
    Serial.write((uint8_t*)&fs, 4);
    Serial.write((uint8_t*)&n, 4);

    for (int b = 0; b < TOTAL_BLOQUES; b++) {
        leerMuestrasI2S(bufferCaptura, NUM_MUESTRAS);

        // 24 bits -> 16 bits
        for (int i = 0; i < NUM_MUESTRAS; i++)
            bufferTx[i] = (int16_t)constrain(bufferCaptura[i] >> 8, -32768, 32767);
        
        Serial.write((uint8_t*)bufferTx, NUM_MUESTRAS * sizeof(int16_t));

        // Procesar bloque en IndiceVascular (filtros + FFT + integracion 50-300 Hz)
        ivProcesarMuestras(bufferTx, NUM_MUESTRAS);
    }

    // Enviar los 2 floats finales que espera tu script de Python
    float magMedia = ivMagnitudMedia();   // Se recibira en la variable 'pico' de tu Python
    float indice   = ivCalcularHVSI();    // Se recibira en la variable 'indice' de tu Python
    Serial.write((uint8_t*)&magMedia, 4);
    Serial.write((uint8_t*)&indice, 4);
}

// Diagnostico: lee en estereo y reporta rango de cada canal (texto por serial)
void diagnosticoCanales() {
    i2s_driver_uninstall(I2S_NUM_0);
    i2s_config_t cfg = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    i2s_pin_config_t pins = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD_PIN
    };
    i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pins);

    static int32_t st[1024];
    size_t br = 0;
    for (int k = 0; k < 6; k++) i2s_read(I2S_NUM_0, st, sizeof(st), &br, portMAX_DELAY);

    long minA = 2147483647, maxA = -2147483647, minB = 2147483647, maxB = -2147483647;
    for (int i = 0; i < 512; i++) {
        long a = st[2 * i] >> 8, b = st[2 * i + 1] >> 8;
        if (a < minA) minA = a; if (a > maxA) maxA = a;
        if (b < minB) minB = b; if (b > maxB) maxB = b;
    }
    Serial.printf("DIAG canal_izq(WS=0): min=%ld max=%ld | canal_der(WS=1): min=%ld max=%ld\n", minA, maxA, minB, maxB);

    i2s_driver_uninstall(I2S_NUM_0);
    inicializarI2S();
}

// Prueba de pin SD sin I2S: dice si el pin esta a 3V3, a GND o flotando (10 s, cada 0.5 s)
void pruebaPinSD() {
    i2s_driver_uninstall(I2S_NUM_0);
    for (int k = 0; k < 20; k++) {
        pinMode(I2S_SD_PIN, INPUT_PULLUP);   delay(5); int up = digitalRead(I2S_SD_PIN);
        pinMode(I2S_SD_PIN, INPUT_PULLDOWN); delay(5); int dn = digitalRead(I2S_SD_PIN);
        Serial.printf("PIN GPIO%d pullup=%d pulldown=%d\n", I2S_SD_PIN, up, dn);
        delay(490);
    }
    pinMode(I2S_SD_PIN, INPUT);
    inicializarI2S();
}

// Escaner de pines: muestra cuales GPIO leen ALTO (tocalos con un cable desde 3V3). 15 s.
void escanearPines() {
    i2s_driver_uninstall(I2S_NUM_0);
    const int pines[] = {2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33};
    for (int p : pines) pinMode(p, INPUT_PULLDOWN);
    for (int k = 0; k < 30; k++) {
        Serial.print("ALTO:");
        bool alguno = false;
        for (int p : pines) if (digitalRead(p)) { Serial.printf(" %d", p); alguno = true; }
        if (!alguno) Serial.print(" ninguno");
        Serial.println();
        delay(500);
    }
    inicializarI2S();
}

void setup() {
    Serial.begin(BAUDRATE);
    Serial.println("BOOT");
    inicializarI2S();
}

void loop() {
    if (Serial.available() > 0) {
        char c = Serial.read();
        if (c == 'S' || c == 'V') ejecutarCaptura(); // microfono real + IndiceVascular
        if (c == 'D') diagnosticoCanales();          // diagnostico de cableado
        if (c == 'E') escanearPines();               // escaner de pines
        if (c == 'P') pruebaPinSD();                 // prueba del pin SD (3V3/GND/flotante)
    }
}