import network
import espnow
from machine import Pin, ADC
import time
import dht 
from adc_sub import ADC_substitute

def get_battery_percentage():
    i = battery.read_voltage()
    bp = alpha * i + beta
    bp = int(bp)
    if bp < 0:
        bp = 0
    elif bp > 100:
        bp = 100
    return bp

dashboard_mac_address = b'\xC8\xF0\x9E\x4E\xD9\x64'

sensor_id_1 = "DHT11"
pin_dht11 = 32

sensor_id_2 = "MQ135"
pin_sensor_analog = 35
pin_sensor_digital = 33

pin_battery = 34

sta = network.WLAN(network.STA_IF)
sta.active(True)

en = espnow.ESPNow()
en.active(True)

sensor_1 = dht.DHT11(Pin(pin_dht11))

sensor_analog = ADC_substitute(pin_sensor_analog)
sensor_digital = Pin(pin_sensor_digital, Pin.IN)

battery = ADC_substitute(pin_battery)

prev_sensor1_value_temp = -999
prev_sensor1_value_hum = -999
prev_sensor2_value_analog = -999
prev_sensor2_value_digital = -999
prev_bat_pct = -1

en.add_peer(dashboard_mac_address)
en.send(dashboard_mac_address, sensor_id_1 + " klar", False)
en.send(dashboard_mac_address, sensor_id_2 + " klar", False)

print(sensor_id_1 + " klar")
print(sensor_id_2 + " klar")

i1 = 1.675343
i2 = 2.360493
bp1 = 0
bp2 = 100
alpha = (bp2 - bp1) / (i2 - i1)
beta = bp1 - alpha * i1

while True:
    bat_pct = get_battery_percentage()

    sensor_1.measure()
    sensor1_value_temp = sensor_1.temperature()
    sensor1_value_hum = sensor_1.humidity()

    print("Sensor 1 - Temperatur:", sensor1_value_temp)
    print("Sensor 1 - Luftfugtighed:", sensor1_value_hum)

    data_string_sensor1 = f"{time.ticks_ms()}|{bat_pct}|Sensor 1 - Temperatur: {sensor1_value_temp}|Sensor 1 - Luftfugtighed: {sensor1_value_hum}"
    try:
        print("Sender data fra Sensor 1...")
        en.send(dashboard_mac_address, data_string_sensor1, False)
        print("Data fra Sensor 1 sendt.")
    except ValueError as e:
        print("Fejl ved afsendelse af besked for Sensor 1: " + str(e))

    sensor2_value_analog = sensor_analog.read_adc()
    sensor2_value_digital = sensor_digital.value()

    print("Sensor 2 - Analog værdi:", sensor2_value_analog)
    print("Sensor 2 - Digital værdi:", sensor2_value_digital)

    data_string_sensor2 = f"{time.ticks_ms()}|{bat_pct}|Sensor 2 - Analog værdi: {sensor2_value_analog}|Sensor 2 - Digital værdi: {sensor2_value_digital}"
    try:
        print("Sender data fra Sensor 2...")
        en.send(dashboard_mac_address, data_string_sensor2, False)
        print("Data fra Sensor 2 sendt.")
    except ValueError as e:
        print("Fejl ved afsendelse af besked for Sensor 2: " + str(e))

    time.sleep(1)
