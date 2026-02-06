# ml_model.py
import joblib
import numpy as np
import os

MODEL_PATH = "modelo_heladas.pkl"
_model = None

def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise Exception("❌ No existe el modelo ML. Ejecuta ml_train.py primero.")
        _model = joblib.load(MODEL_PATH)
    return _model

def predecir(temp, humedad, viento, presion, hora):
    model = _load_model()

    X = np.array([[float(temp), float(humedad), float(viento), float(presion), int(hora)]])

    proba = model.predict_proba(X)[0]
    clases = model.classes_

    idx = proba.argmax()
    riesgo = clases[idx]
    confianza = float(proba[idx])

    return riesgo, confianza
