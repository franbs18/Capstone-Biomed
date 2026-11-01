#include "CapturaAudio.h"
#include "Configuracion.h"

void inicializarI2S() {
    // Configuración estructural del periférico I2S_NUM_0
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX), // Modo Maestro y Receptor
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,        // El INMP441 requiere contenedores de 32 bits
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,        // Estéreo: se lee ambos slots y se usa el del micrófono
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,   // Protocolo estándar I2S (Philips)
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,            // Prioridad de la interrupción del sistema
        .dma_buf_count = 8,                                  // Cantidad de buffers DMA
        .dma_buf_len = 512,                                  // Tamaño de cada buffer DMA
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // Configuración física de los pines que elegiste
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE, // No usamos salida de audio
        .data_in_num = I2S_SD_PIN
    };

    // Instalar el driver y asignar los pines físicos
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
}

void leerMuestrasI2S(int32_t *buffer, size_t num_muestras) {
    // Se lee en estereo (izq, der, izq, der...) y se usa el slot SLOT_MIC (ver Configuracion.h)
    static int32_t estereo[2 * NUM_MUESTRAS];
    if (num_muestras > NUM_MUESTRAS) num_muestras = NUM_MUESTRAS;
    size_t bytes_leidos = 0;

    i2s_read(I2S_NUM_0, estereo, 2 * num_muestras * sizeof(int32_t), &bytes_leidos, portMAX_DELAY);

    // El INMP441 entrega 24 bits justificados a la izquierda en el contenedor de 32 bits
    for (size_t i = 0; i < num_muestras; i++) {
        buffer[i] = estereo[2 * i + SLOT_MIC] >> 8;
    }
}