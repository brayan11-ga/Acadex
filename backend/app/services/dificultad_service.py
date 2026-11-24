RATIO_BAJO = 0.72
RATIO_ALTO = 1.25
RATIO_MUY_ALTO = 2.0

def calcular_dificultad_real(
        dificultad_estimada: int, tiempo_estimado_min:int, tiempo_real_seg: float
)-> int:
    # la dificultad real compara el tiempo real (seg) con el estimado (min)
    if not tiempo_real_seg or tiempo_real_seg <=0 or not tiempo_estimado_min or tiempo_estimado_min <=0:
        return dificultad_estimada #sin tiempo registrado no hay nda
    ratio=tiempo_real_seg /(tiempo_estimado_min * 60)
    if ratio <= RATIO_BAJO:
        ajuste =-1
    elif ratio <= RATIO_ALTO:
        ajuste = 0
    elif ratio <= RATIO_MUY_ALTO:
        ajuste = 1
    else:
        ajuste = 2
    return max(1,min(5, dificultad_estimada + ajuste))