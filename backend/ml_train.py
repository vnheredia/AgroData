# ml_train.py
import joblib
import numpy as np
import psycopg2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from db import get_connection

MODEL_PATH = "modelo_heladas.pkl"

def etiquetar(temp, humedad, viento, hora):
    # Etiquetas base (puedes afinarlas si quieres)
    if temp <= 1:
        return "ALTO"
    elif temp <= 4:
        return "MEDIO"
    else:
        return "BAJO"

def entrenar_modelo():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT temperatura, humedad, viento, presion, EXTRACT(HOUR FROM fecha_hora) as hora
        FROM datos_climaticos
        WHERE temperatura IS NOT NULL
        ORDER BY fecha_hora ASC
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if len(rows) < 100:
        print("⚠️ No hay suficientes datos para entrenar ML")
        return

    X = []
    y = []

    for temp, humedad, viento, presion, hora in rows:
        X.append([float(temp), float(humedad), float(viento), float(presion), int(hora)])
        y.append(etiquetar(float(temp), float(humedad), float(viento), int(hora)))

    X = np.array(X)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("📊 Evaluación del modelo:")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Modelo entrenado y guardado en {MODEL_PATH}")

if __name__ == "__main__":
    entrenar_modelo()
