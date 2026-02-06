from db import get_connection
from rules_engine import calcular_riesgo_helada
from ml_model import predecir
from alerts import decidir_alerta

def analizar_ultimo_dato():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            temperatura, 
            humedad, 
            viento, 
            presion, 
            EXTRACT(HOUR FROM fecha_hora) AS hora
        FROM datos_climaticos
        ORDER BY fecha_hora DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"error": "No hay datos aún"}

    temp, humedad, viento, presion, hora = row

    riesgo_reglas = calcular_riesgo_helada(temp, humedad, viento, presion, hora)
    riesgo_ml, confianza_ml = predecir(temp, humedad, viento, presion, hora)

    semaforo = decidir_alerta(riesgo_ml, confianza_ml, riesgo_reglas)

    return {
        "temperatura": float(temp),
        "humedad": float(humedad),
        "viento": float(viento),
        "presion": float(presion),
        "hora": int(hora),
        "riesgo_reglas": riesgo_reglas,
        "riesgo_ml": riesgo_ml,
        "confianza_ml": round(confianza_ml, 2),
        "alerta_final": semaforo
    }

if __name__ == "__main__":
    print(analizar_ultimo_dato())
