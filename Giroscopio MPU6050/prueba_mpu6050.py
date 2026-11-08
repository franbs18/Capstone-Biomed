import serial
import time

PUERTO_SERIAL = '/dev/cu.usbserial-0001' 
BAUD_RATE = 115200

try:
    print(f"Conectando al puerto {PUERTO_SERIAL} a {BAUD_RATE} baudios...")
    
    # Abrimos el puerto configurando explícitamente DTR y RTS en False para no bloquear
    ser = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1, rtscts=False, dsrdtr=False)
    
    print("Forzando reinicio de hardware del ESP32...")
    # Truco eléctrico para reiniciar el ESP32 desde Python (equivale a presionar el botón EN)
    ser.setDTR(False)
    ser.setRTS(False)
    time.sleep(0.5)
    ser.setDTR(True)
    ser.setRTS(True)
    time.sleep(1) # Esperar a que arranque
    
    print("Conectado con éxito. Escuchando datos... (Presiona Ctrl+C para salir)\n")
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            linea_raw = ser.readline()
            try:
                linea_texto = linea_raw.decode('utf-8', errors='ignore').strip()
                if linea_texto: # Solo imprimir si no está vacío
                    print(f"[TEXTO]: {linea_texto}")
            except Exception as e:
                print(f"[BYTES RAROS]: {linea_raw}")
        time.sleep(0.01) # Pequeña pausa para no saturar el procesador de la Mac

except serial.SerialException as e:
    print(f"\nError al abrir el puerto: {e}")
except KeyboardInterrupt:
    print("\nLectura finalizada por el usuario.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Puerto serial cerrado.")
