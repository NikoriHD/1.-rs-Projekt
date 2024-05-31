import socket
import sqlite3
import sys
import os

def connect_to_server(server_ip, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print('Connected to ESP32 server')
        return client_socket
    except Exception as e:
        print('Error connecting to server:', e)
        sys.exit(1)

def receive_data_and_store(client_socket, db_filename):
    try:
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()

        c.execute('DROP TABLE IF EXISTS bk_sensor_data')
        
        c.execute('''CREATE TABLE IF NOT EXISTS bk_sensor_data (
                        id            INTEGER  PRIMARY KEY AUTOINCREMENT,
                        timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
                        sensor_id     INTEGER,
                        temperature   REAL,
                        humidity      REAL,
                        analog_value  INTEGER,
                        digital_value INTEGER
                     )''')
        
        conn.commit()

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                decoded_data = data.decode('utf-8')
            except UnicodeDecodeError:
                decoded_data = str(data)

            print('Received from ESP32:', decoded_data)

            parts = decoded_data.split('|')
            sensor_id = None
            temperature = None
            humidity = None
            analog_value = None
            digital_value = None
            
            for part in parts:
                if part.startswith('Sensor'):
                    if 'Temperatur' in part:
                        temperature = float(part.split(':')[-1])
                    elif 'Luftfugtighed' in part:
                        humidity = float(part.split(':')[-1])
                    elif 'Analog værdi' in part:
                        analog_value = int(part.split(':')[-1])
                    elif 'Digital værdi' in part:
                        digital_value = int(''.join(filter(str.isdigit, part)))
                elif part.isdigit():
                    sensor_id = int(part)

            if sensor_id is not None:
                if digital_value is not None and digital_value > 100:
                    print("Digital value exceeds 100, not adding to the database.")
                else:
                    try:
                        c.execute("INSERT INTO bk_sensor_data (sensor_id, temperature, humidity, analog_value, digital_value) VALUES (?, ?, ?, ?, ?)",
                                  (sensor_id, temperature, humidity, analog_value, digital_value))
                        conn.commit()
                    except sqlite3.Error as e:
                        print(f"SQLite error: {e}")

        print('Connection closed')
        conn.close()
        client_socket.close()
    except Exception as e:
        print('Error:', e)
        sys.exit(1)

if __name__ == "__main__":
    server_ip = '192.168.0.142'  # Replace with the IP address of the ESP32
    server_port = 1235

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    db_filename = os.path.join(desktop_path, 'bk_sensor_data.db')

    client_socket = connect_to_server(server_ip, server_port)
    receive_data_and_store(client_socket, db_filename)
