def decidir_alerta(riesgo_ml, confianza_ml, riesgo_reglas):
    # Priorizamos ML si está seguro
    if riesgo_ml == "ALTO" and confianza_ml >= 0.7:
        return "ROJO"
    if riesgo_ml == "MEDIO" and confianza_ml >= 0.6:
        return "AMARILLO"

    # Respaldo por reglas
    if riesgo_reglas == "ROJO":
        return "ROJO"
    if riesgo_reglas == "AMARILLO":
        return "AMARILLO"

    return "VERDE"
