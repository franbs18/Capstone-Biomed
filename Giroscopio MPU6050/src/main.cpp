#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM303_U.h>
#include <Adafruit_L3GD20_U.h>

/* Declaración de ambos sensores unificados */
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(30301);
Adafruit_L3GD20_Unified       gyro  = Adafruit_L3GD20_Unified(20);

void setup(void) {
  Serial.begin(115200);
  
  // Forzar pines I2C estándar del ESP32 (SDA=21, SCL=22)
  Wire.begin(21, 22);

  Serial.println(F("=== Test Movimiento 10-DOF (Accel + Gyro) ==="));
  Serial.println("");
  
  /* Inicializar el acelerómetro */
  if(!accel.begin()) {
    Serial.println(F("¡Error! No se detecto el acelerometro LSM303."));
    while(1);
  }

  /* Inicializar el giroscopio */
  if(!gyro.begin()) {
    Serial.println(F("¡Error! No se detecto el giroscopio L3GD20."));
    while(1);
  }
  
  Serial.println(F("¡Sensores cargados con exito!"));

  delay(500); // Darle tiempo a los chips para estabilizarse
}


void loop(void) {
  /* Contenedores para almacenar las lecturas */
  sensors_event_t accel_event;
  sensors_event_t gyro_event;
  
  /* Obtener eventos actuales de hardware */
  accel.getEvent(&accel_event);
  delay(10); 
  gyro.getEvent(&gyro_event);
  
  /* Imprimir lecturas del Acelerómetro */
  Serial.print(F("Accel -> X: "));
  Serial.print(accel_event.acceleration.x);
  Serial.print(F(" | Y: "));
  Serial.print(accel_event.acceleration.y);
  Serial.print(F(" | Z: "));
  Serial.print(accel_event.acceleration.z);
  Serial.print(F(" m/s^2"));

  /* Imprimir lecturas del Giroscopio (Velocidad angular) */
  Serial.print(F("  ||  Gyro -> X: "));
  Serial.print(gyro_event.gyro.x);
  Serial.print(F(" | Y: "));
  Serial.print(gyro_event.gyro.y);
  Serial.print(F(" | Z: "));
  Serial.print(gyro_event.gyro.z);
  Serial.println(F(" rad/s"));

  delay(500); // Actualiza cada medio segundo
}
