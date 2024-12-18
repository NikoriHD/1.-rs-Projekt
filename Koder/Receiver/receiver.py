import network
import espnow
import socket
import time
import machine

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    
    print('Wi-Fi connected!')
    print('IP address:', wlan.ifconfig()[0])

wifi_ssid = "INDSÆT WIFI NAVN"
wifi_password = "INDSÆT KODE"
connect_to_wifi(wifi_ssid, wifi_password)

esp_now = espnow.ESPNow()
esp_now.active(True)

peer_mac = b'\xB0\xA7\x32\xDE\x67\x3C'
esp_now.add_peer(peer_mac)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 1235))
server_socket.listen(1)

print('Waiting for client connection...')
client_socket, client_address = server_socket.accept()
print('Client connected:', client_address)

BUZZER_PIN = 32
buzzer_PWM_object = machine.PWM(machine.Pin(BUZZER_PIN), freq=440, duty=0)

def play_buzzer(duration, frequency=440, duty=512):
    buzzer_PWM_object.freq(frequency)
    buzzer_PWM_object.duty(duty)
    time.sleep_ms(duration)
    buzzer_PWM_object.duty(0)
    time.sleep(0.1)

hello_msg = b'KLAR TIL AT SENDE'
client_socket.sendall(hello_msg)

while True:
    host, msg = esp_now.recv()
    if msg:
        print('Received from ESP-NOW:', msg)
        print("Modtaget ESP-NOW meddelelse:", msg)
        
        print('Sending to client:', msg)
        client_socket.sendall(msg)
        
        if msg == b'end':
            break

        if b'Sensor 2 - Analog v\xc3\xa6rdi:' in msg:
            try:
                parts = msg.decode('utf-8').split(':')
                if len(parts) >= 2:
                    analog_value = int(parts[1].strip())
                    print("Analog værdi:", analog_value)
                
                    if analog_value > 100:
                        print("Analog værdi over 100, triggering buzzer...")
                        play_buzzer(1000, frequency=440, duty=512)
                        print("Buzzer triggered!") 
                else:
                    print("Invalid message format:", msg)
            except ValueError:
                print("Failed to parse analog value from message")

client_socket.close()
server_socket.close()
print('Connection closed')
