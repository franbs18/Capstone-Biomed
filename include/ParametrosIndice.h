// GENERADO AUTOMATICAMENTE por VER02/VER02_indice.py (python VER02/VER02_indice.py --exportar)
// No editar a mano: cambia los valores en Python y vuelve a generarlo.
#ifndef PARAMETROS_INDICE_H
#define PARAMETROS_INDICE_H

// Calibracion de la escala 0-999: A_media = IV_A_REF -> HVSI = 999
#define IV_A_REF 40.000000f

// Cada fila es una seccion de 2do orden: {b0, b1, b2, a1, a2}  (a0 = 1)
// Pasabanda Butterworth orden 4, 50-1500 Hz, fs = 16000 Hz
#define IV_N_SOS_BP 4
static const float IV_SOS_BP[4][5] = {
    {3.443946442e-03f, 6.887892883e-03f, 3.443946442e-03f, -1.143525404e+00f, 3.479968157e-01f},
    {1.000000000e+00f, 2.000000000e+00f, 1.000000000e+00f, -1.390779605e+00f, 6.674252631e-01f},
    {1.000000000e+00f, -2.000000000e+00f, 1.000000000e+00f, -1.962301204e+00f, 9.627254141e-01f},
    {1.000000000e+00f, -2.000000000e+00f, 1.000000000e+00f, -1.985392659e+00f, 9.857820334e-01f}
};

// Pasabajo Butterworth orden 4, fc = 300 Hz, fs = 16000 Hz
#define IV_N_SOS_LP 2
static const float IV_SOS_LP[2][5] = {
    {1.036861927e-05f, 2.073723854e-05f, 1.036861927e-05f, -1.791587697e+00f, 8.040928440e-01f},
    {1.000000000e+00f, 2.000000000e+00f, 1.000000000e+00f, -1.900646564e+00f, 9.139129337e-01f}
};

#endif
