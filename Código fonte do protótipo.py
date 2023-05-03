import machine
import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters

MQTT_CLIENT_ID = "clientId-workwi9256"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "workwiweather9256"
MQTT_TOPIC2    = "workwiweather9257"

# Identificando entradas ESP32 

sensor = dht.DHT22(Pin(15))
ledgreen = machine.Pin(13, machine.Pin.OUT)
ledred = machine.Pin(12, machine.Pin.OUT)
ledblue = machine.Pin(27, machine.Pin.OUT)

# Variáveis 

prev_weather = ""

# Conectando a placa à internet

print("Conectando ao WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Conectado!")

# Conectando ao servidor MQTT

print("Conectando ao MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Conectado!")

# Definindo função de callback

def mqtt_callback(MQTT_TOPIC2, msg):
  print('Nova atualização:{}'.format(msg)) 
  if sensor.humidity() > float(msg):
    ledred.value(0)
    ledgreen.value(1)
  else:
    ledgreen.value(0)
    ledred.value(1)


# Iniciando LED amarelo

ledgreen.value(1)
ledred.value(1)

# Loop principal

while True:
  print("Realizando leitura... ", end="")
  sensor.measure() 
  message = ujson.dumps({
    "Temperatura: ": sensor.temperature(),
    "Umidade do ar: ": sensor.humidity(),
  }) 

  client.set_callback(mqtt_callback)
  client.subscribe(MQTT_TOPIC2)
  client.check_msg

  if message != prev_weather:
    print("Atualizado!")
    print("Reportando ao servidor MQTT {}: {}".format(MQTT_TOPIC, message))
    client.publish(MQTT_TOPIC, message)
    prev_weather = message
  else:
    print("\nMesma condição")
  time.sleep(1)