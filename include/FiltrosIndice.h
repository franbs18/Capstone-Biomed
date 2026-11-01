// GENERADO AUTOMATICAMENTE por indice_vascular.py (python indice_vascular.py --exportar-coef)
// No editar a mano: si cambias FS, cortes u ordenes en Python, vuelve a generarlo.
// Cada fila es una seccion de 2do orden: {b0, b1, b2, a1, a2}  (a0 = 1)
#ifndef FILTROS_INDICE_H
#define FILTROS_INDICE_H

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
