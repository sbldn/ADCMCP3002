import datetime
import serial
import json



class SensorReader:
    def __init__(self, puerto='COM8', baudrate=115200):
        self.puerto = puerto
        self.baudrate=baudrate


    def get_values(self):
        timestamp = datetime.datetime.now()
        serial_json=self.leer_puerto_serial(self.puerto, self.baudrate)
        if serial_json:
            return_json = {
                'Time': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'Temperature': serial_json['temperature'],
                'Light': serial_json['luminosity']
            }
        else:
            return_json = {}
        
        return return_json
        

    def leer_puerto_serial(self, puerto, baudrate):
        try:
            # Abrir el puerto serial
            ser = serial.Serial(puerto, baudrate, timeout=1)
            # print(f"Conectado al puerto {puerto} a {baudrate} baudios.")
            
            # Leer datos continuamente
            while True:
                if ser.in_waiting > 0:
                    linea = ser.readline().decode('utf-8').rstrip()
                    return json.loads(linea)


        except serial.SerialException as e:
            print(f"Error al abrir el puerto serial: {e}")

        except KeyboardInterrupt:
            print("Lectura interrumpida por el usuario.")
        
        finally:
            # Cerrar el puerto serial
            if 'ser' in locals() and ser.is_open:
                ser.close()
                # print("Puerto serial cerrado.")


if __name__ == "__main__":
    sensor = SensorReader(puerto='COM8', baudrate=115200)
    values = sensor.get_values()
    print(values)

