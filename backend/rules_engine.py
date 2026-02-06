def calcular_riesgo_helada(temp, humedad, viento, presion, hora):
    score = 0

    if temp <= 2:
        score += 2
    if humedad >= 80:
        score += 1
    if viento < 3:
        score += 1
    if presion > 1015:
        score += 1
    if hora < 6:
        score += 1

    if score >= 5:
        return "ALTO"
    elif score >= 3:
        return "MEDIO"
    else:
        return "BAJO"
