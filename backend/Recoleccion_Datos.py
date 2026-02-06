import json
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime
import time

# ======== CONFIG BD ========
DB_HOST = "localhost"
DB_NAME = "agrodata"
DB_USER = "postgres"
DB_PASS = "Margarita1980"

# ======== CONFIG MQTT ========
MQTT_BROKER = "4861bba361b14626a3407343f1d5b658.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "sensores/estacion1"
MQTT_USER = "Grupo6"
MQTT_PASS = "Infraestructura2"

# ======== COORDENADAS DE MALCHINGUÍ ========
LAT = 0.05223829352641043
LON = -78.3433616677921

# ======== CONTROL DE TIEMPO ========
INTERVALO_GUARDADO = 60  # 5 minutos
ultimo_guardado = 0

def on_message(client, userdata, msg):
    global ultimo_guardado
    ahora = time.time()

    # Si no han pasado 5 minutos, no guardamos
    if ahora - ultimo_guardado < INTERVALO_GUARDADO:
        return

    ultimo_guardado = ahora

    payload = msg.payload.decode()
    data = json.loads(payload)

    # Limpieza de unidades
    temp = float(data["temperatura"].replace(" °C", ""))
    hum = float(data["humedad"].replace(" %", ""))
    luz = float(data["luz"].replace(" Lux", ""))
    lluvia = float(data["lluvia"].replace(" % probabilidad de Lluvia", ""))
    presion = float(data["presion"].replace(" hPa", ""))
    viento = float(data["viento"].replace(" km/h", ""))
    aire = float(data["aire"].replace(" AQI", ""))
    fecha = datetime.strptime(data["fecha_hora"], "%Y-%m-%d %H:%M:%S")

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO datos_climaticos 
        (fecha_hora, temperatura, humedad, luz, lluvia, presion, viento, aire, ubicacion)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s, ST_GeogFromText('POINT(%s %s)'))
    """, (fecha, temp, hum, luz, lluvia, presion, viento, aire, LON, LAT))

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Dato guardado en BD:", fecha, temp, hum)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()

client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)

print("📡 Escuchando datos de la estación (guardando cada 5 minutos)...")
client.loop_forever()
