# ============================================================
#  Módulo: Recomendación de Jugada con IA
#  Parchis3 - Sistemas Distribuidos UTP
#  Generado con asistencia de IA (Claude - Anthropic)
# ============================================================
"""
Módulo de recomendación que usa la API de Anthropic (Claude) para
sugerir la mejor jugada dado el estado actual del tablero y los dados.

Uso típico (desde main.py cuando es el turno del jugador):
    from recomendacion import obtener_recomendacion
    rec = obtener_recomendacion(dados, jugador, todos_jugadores)
    # rec es un dict con 'ficha', 'movimiento', 'justificacion'

Si no hay conexión a la API, usa el motor de recomendación local
como fallback automático.
"""

import json
import urllib.request
import urllib.error
from settings import (
    casillas, casas, carcel_fichas, final_fichas,
    seguros, salidas
)

# ---------------------------------------------------------------
# Constante: URL de la API de Anthropic
# (La API key la inyecta el entorno de claude.ai automáticamente)
# ---------------------------------------------------------------
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


# ---------------------------------------------------------------
# Motor local de recomendación (fallback sin API)
# ---------------------------------------------------------------

def _casilla_index(ficha_pos: list, color: str) -> int:
    """Devuelve el índice de casilla de una ficha (0 = cárcel)."""
    ls = list(casillas.values())
    if ficha_pos in ls:
        return ls.index(ficha_pos) + 1
    return 0


def _ficha_en_carcel(ficha_pos: list, color: str) -> bool:
    return ficha_pos in carcel_fichas[color]


def _ficha_en_casa(ficha_pos: list, color: str) -> bool:
    return ficha_pos in casas[color]


def _ficha_en_final(ficha_pos: list, color: str) -> bool:
    return ficha_pos in final_fichas[color]


def _evaluar_movimiento_local(ficha_idx: int, ficha_pos: list, dado: int,
                               color: str, todos_jugadores: list) -> dict:
    """
    Evalúa un posible movimiento y devuelve un score + descripción.
    """
    score = 0
    razones = []
    ls_casillas = list(casillas.values())

    if _ficha_en_carcel(ficha_pos, color):
        return {'score': -1, 'razones': ['ficha en cárcel, no se puede mover']}

    if _ficha_en_final(ficha_pos, color):
        return {'score': -1, 'razones': ['ficha ya en posición final']}

    idx_actual = _casilla_index(ficha_pos, color)
    if idx_actual == 0:
        # Está en casillas de casa (camino de color)
        idx_casa = casas[color].index(ficha_pos)
        nuevo_idx = idx_casa + dado
        if nuevo_idx >= len(casas[color]):
            return {'score': -1, 'razones': ['movimiento fuera del tablero']}
        nueva_pos = casas[color][nuevo_idx]
        if nueva_pos in final_fichas[color]:
            score += 100
            razones.append('¡llega al final!')
        else:
            score += 20
            razones.append('avanza en la recta final')
        return {'score': score, 'razones': razones, 'nueva_pos': nueva_pos}

    # Ficha en casillas normales
    nuevo_idx = idx_actual + dado
    if nuevo_idx > 68:
        nuevo_idx = nuevo_idx - 68

    index_entrada_casa = list(casillas.values()).index(casas[color][0]) + 1 if casas[color][0] in ls_casillas else 0

    # ¿Entra a la recta de color?
    if nuevo_idx >= index_entrada_casa and idx_actual < index_entrada_casa:
        pasos_en_casa = nuevo_idx - index_entrada_casa
        if pasos_en_casa < len(casas[color]):
            nueva_pos = casas[color][pasos_en_casa]
            score += 40
            razones.append('entra a la recta de color (protegida)')
        else:
            nueva_pos = casas[color][-1]
    else:
        if nuevo_idx > 68:
            nuevo_idx -= 68
        if nuevo_idx < 1 or nuevo_idx > 68:
            return {'score': -1, 'razones': ['movimiento inválido']}
        nueva_pos = casillas[nuevo_idx]

    # ¿Cae en seguro?
    if nuevo_idx in seguros:
        score += 15
        razones.append('cae en casilla de seguro')

    # ¿Come ficha rival?
    for jugador in todos_jugadores:
        if jugador['color'] != color:
            for f in jugador['fichas']:
                if f == nueva_pos and nuevo_idx not in seguros and nuevo_idx not in salidas.values():
                    score += 50
                    razones.append(f'come la ficha de {jugador["nombre"]} ({jugador["color"]})')

    # ¿Está en riesgo de ser comida en posición actual?
    if idx_actual not in seguros and idx_actual not in salidas.values():
        for jugador in todos_jugadores:
            if jugador['color'] != color:
                for f in jugador['fichas']:
                    fi = _casilla_index(f, jugador['color'])
                    if fi > 0:
                        for d in range(1, 13):
                            ni = fi + d
                            if ni > 68:
                                ni -= 68
                            if ni == idx_actual:
                                score -= 20
                                razones.append('ficha en riesgo de ser comida si se queda')
                                break

    if not razones:
        razones.append('movimiento de avance normal')

    return {'score': score, 'razones': razones, 'nueva_pos': nueva_pos}


def _recomendar_local(dados: list, jugador: dict, todos_jugadores: list) -> dict:
    """Motor local de recomendación sin IA."""
    color = jugador['color']
    fichas = jugador['fichas']
    movimientos_posibles = [dados[0] + 1, dados[1] + 1, sum(dados) + 2]
    mejor_score = -999
    mejor_ficha_idx = 0
    mejor_dado = movimientos_posibles[0]
    mejor_razones = ['movimiento por defecto']

    for i, ficha in enumerate(fichas):
        if _ficha_en_carcel(ficha, color) or _ficha_en_final(ficha, color):
            continue
        for dado in movimientos_posibles:
            ev = _evaluar_movimiento_local(i, ficha, dado, color, todos_jugadores)
            if ev['score'] > mejor_score:
                mejor_score = ev['score']
                mejor_ficha_idx = i
                mejor_dado = dado
                mejor_razones = ev.get('razones', [])

    justificacion = '; '.join(mejor_razones) if mejor_razones else 'mejor movimiento disponible'
    return {
        'ficha': mejor_ficha_idx,
        'movimiento': mejor_dado,
        'justificacion': justificacion,
        'fuente': 'motor_local'
    }


# ---------------------------------------------------------------
# Recomendación con Claude (API de Anthropic)
# ---------------------------------------------------------------

def _construir_prompt(dados: list, jugador: dict, todos_jugadores: list) -> str:
    color = jugador['color']
    fichas = jugador['fichas']
    fichas_desc = []
    ls_casillas = list(casillas.values())

    for i, f in enumerate(fichas):
        if _ficha_en_carcel(f, color):
            estado = 'en cárcel'
        elif _ficha_en_final(f, color):
            estado = 'en posición FINAL (meta)'
        elif _ficha_en_casa(f, color):
            estado = f'en recta de color (casilla {casas[color].index(f)+1}/9)'
        else:
            idx = _casilla_index(f, color)
            en_seguro = ' (SEGURO)' if idx in seguros else ''
            en_salida = ' (SALIDA)' if idx in salidas.values() else ''
            estado = f'casilla {idx}{en_seguro}{en_salida}'
        fichas_desc.append(f'  Ficha {i}: {estado}')

    rivales_desc = []
    for j in todos_jugadores:
        if j['nombre'] != jugador['nombre']:
            cerca = []
            for f in j['fichas']:
                if not _ficha_en_carcel(f, j['color']):
                    idx = _casilla_index(f, j['color'])
                    if idx > 0:
                        cerca.append(f'casilla {idx}')
            rivales_desc.append(f'  {j["nombre"]} ({j["color"]}): {", ".join(cerca) if cerca else "todas en cárcel"}')

    mov = [dados[0]+1, dados[1]+1, sum(dados)+2]

    prompt = f"""Eres un experto en el juego de Parqués colombiano. Analiza el siguiente estado y recomienda la mejor jugada.

JUGADOR: {jugador['nombre']} (fichas {color})
DADOS: {dados[0]+1} y {dados[1]+1}
MOVIMIENTOS POSIBLES: {mov[0]}, {mov[1]} o {mov[2]} casillas

MIS FICHAS:
{chr(10).join(fichas_desc)}

RIVALES:
{chr(10).join(rivales_desc) if rivales_desc else '  No hay rivales activos'}

REGLAS CLAVE:
- Casillas de seguro y salida protegen las fichas de ser comidas
- Si caes en la misma casilla que un rival (fuera de seguro/salida), lo mandas a la cárcel
- La recta de color es el camino final y es intocable por rivales
- Llegar a la meta con las 4 fichas gana la partida

Responde ÚNICAMENTE con un JSON con este formato exacto (sin explicación fuera del JSON):
{{"ficha": <índice 0-3>, "movimiento": <casillas a mover>, "justificacion": "<explicación breve en español>"}}"""

    return prompt


def _llamar_api_claude(prompt: str) -> dict:
    """Llama a la API de Anthropic y devuelve el JSON de recomendación."""
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        },
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        respuesta = json.loads(resp.read().decode('utf-8'))

    texto = respuesta['content'][0]['text'].strip()
    # Extraer JSON de la respuesta
    inicio = texto.find('{')
    fin = texto.rfind('}') + 1
    if inicio == -1 or fin == 0:
        raise ValueError('No se encontró JSON en la respuesta de Claude')
    resultado = json.loads(texto[inicio:fin])
    resultado['fuente'] = 'claude_api'
    return resultado


# ---------------------------------------------------------------
# Función principal exportada
# ---------------------------------------------------------------

def obtener_recomendacion(dados: list, jugador: dict, todos_jugadores: list) -> dict:
    """
    Obtiene la recomendación de jugada para el jugador actual.

    :param dados:           lista [dado1, dado2] con valores 0-5 (índice de cara)
    :param jugador:         dict del jugador actual {'nombre', 'color', 'fichas'}
    :param todos_jugadores: lista de todos los jugadores en partida
    :return: dict con claves 'ficha', 'movimiento', 'justificacion', 'fuente'
    """
    # Intenta primero con la API de Claude
    try:
        prompt = _construir_prompt(dados, jugador, todos_jugadores)
        resultado = _llamar_api_claude(prompt)
        print(f'[IA] Recomendación via Claude API: ficha {resultado["ficha"]}, '
              f'{resultado["movimiento"]} casillas')
        return resultado
    except Exception as e:
        print(f'[IA] API no disponible ({e}), usando motor local...')

    # Fallback: motor local
    resultado = _recomendar_local(dados, jugador, todos_jugadores)
    print(f'[IA-Local] Recomendación: ficha {resultado["ficha"]}, '
          f'{resultado["movimiento"]} casillas — {resultado["justificacion"]}')
    return resultado


# ---------------------------------------------------------------
# Test rápido de consola
# ---------------------------------------------------------------
if __name__ == '__main__':
    from settings import carcel_fichas as cf, casillas as cs
    fichas_test = [list(cf['azul'][0]), list(cf['azul'][1]),
                   list(cs[10]), list(cs[25])]
    jugador_test = {'nombre': 'JugadorTest', 'color': 'azul', 'fichas': fichas_test}
    rivales_test = [
        {'nombre': 'Rival1', 'color': 'rojo',
         'fichas': [list(cs[8]), list(cs[11]), list(cf['rojo'][0]), list(cf['rojo'][1])]},
    ]
    dados_test = [1, 1]  # doble 2
    rec = obtener_recomendacion(dados_test, jugador_test, rivales_test)
    print('\n=== RECOMENDACIÓN ===')
    print(f'Ficha:        {rec["ficha"]}')
    print(f'Movimiento:   {rec["movimiento"]} casillas')
    print(f'Justificación: {rec["justificacion"]}')
    print(f'Fuente:        {rec["fuente"]}')
