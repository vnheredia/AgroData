from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from db import get_connection
import os
from google import genai

load_dotenv()  
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "../frontend")  

app = Flask(__name__, static_folder=WEB_DIR)

# =========================
# SERVIR EL HTML
# =========================
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# =========================
# ESTADO ACTUAL DEL CLIMA
# =========================
@app.route("/api/estado")
def estado_actual():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT fecha_hora, temperatura, humedad, viento, presion
        FROM datos_climaticos
        ORDER BY fecha_hora DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "No hay datos"}), 404

    # ⚠️ Simulación básica de ML (luego lo conectamos a tu modelo real)
    temperatura = float(row[1])
    humedad = float(row[2])

    # Regla simple de riesgo de helada (provisional pero real)
    if temperatura <= 2:
        riesgo_ml = "ALTO"
        confianza_ml = "0.85"
        riesgo_reglas = "ALTO"
        alerta_final = "ALTO"
    elif temperatura <= 6:
        riesgo_ml = "MEDIO"
        confianza_ml = "0.65"
        riesgo_reglas = "MEDIO"
        alerta_final = "MEDIO"
    else:
        riesgo_ml = "BAJO"
        confianza_ml = "0.92"
        riesgo_reglas = "BAJO"
        alerta_final = "BAJO"

    data = {
        "fecha_hora": row[0].strftime("%Y-%m-%d %H:%M:%S"),
        "temperatura": temperatura,
        "humedad": humedad,
        "viento": float(row[3]),
        "presion": float(row[4]),
        "riesgo_ml": riesgo_ml,
        "confianza_ml": confianza_ml,
        "riesgo_reglas": riesgo_reglas,
        "alerta_final": alerta_final
    }

    return jsonify(data)


# =========================
# HISTÓRICO CON FILTROS
# =========================
@app.route("/api/historico")
def historico():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    offset = (page - 1) * limit

    conn = get_connection()
    cur = conn.cursor()

    if desde and hasta:
        cur.execute("""
            SELECT fecha_hora, temperatura, humedad, viento, presion
            FROM datos_climaticos
            WHERE fecha_hora >= %s::date
            AND fecha_hora < (%s::date + INTERVAL '1 day')
            ORDER BY fecha_hora DESC
            LIMIT %s OFFSET %s
        """, (desde, hasta, limit, offset))

    else:
        cur.execute("""
            SELECT fecha_hora, temperatura, humedad, viento, presion
            FROM datos_climaticos
            ORDER BY fecha_hora DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

    rows = cur.fetchall()

    # total de registros (para saber cuántas páginas hay)
    cur.execute("SELECT COUNT(*) FROM datos_climaticos")
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    data = [
        {
            "fecha_hora": r[0].strftime("%Y-%m-%d %H:%M:%S"),
            "temperatura": float(r[1]),
            "humedad": float(r[2]),
            "viento": float(r[3]),
            "presion": float(r[4]),
        } for r in rows
    ]

    return jsonify({
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    })

# =========================
# CHAT IA 
# =========================
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("mensaje", "")

    if not mensaje:
        return jsonify({"reply": "No recibí tu mensaje."})

    try:
        prompt = f"""
Eres un asistente agrícola para agricultores de Malchinguí, Ecuador.
Da recomendaciones claras, prácticas y cortas.

Pregunta del agricultor:
{mensaje}
"""

        # Llamada correcta a Gemini
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        # Extraer texto de forma segura
        if hasattr(response, "text") and response.text:
            texto = response.text
        else:
            texto = response.candidates[0].content.parts[0].text

        return jsonify({
            "reply": texto
        })

    except Exception as e:
        print("❌ Error Gemini:", e)
        return jsonify({"reply": "Error al contactar con la IA"}), 500




if __name__ == "__main__":
    app.run(debug=True)
