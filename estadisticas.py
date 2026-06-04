# ============================================================
#  Módulo: Estadísticas de Partidas
#  Parchis3 - Sistemas Distribuidos UTP
#  Generado con asistencia de IA (Claude - Anthropic)
# ============================================================
"""
Persiste estadísticas de partidas en un archivo JSON local.
Funciones principales:
  - registrar_partida(ganador, jugadores)  → guarda resultado
  - ranking()                              → jugadores con más victorias
  - probabilidad_ganar(nombre)             → win-rate histórico del jugador
  - historial_jugador(nombre, n)           → últimas n partidas
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any

STATS_FILE = 'estadisticas.json'


# ------------------------------------------------------------------
# Helpers de I/O
# ------------------------------------------------------------------

def _cargar() -> Dict[str, Any]:
    if not os.path.exists(STATS_FILE):
        return {'partidas': [], 'jugadores': {}}
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {'partidas': [], 'jugadores': {}}


def _guardar(datos: Dict[str, Any]):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def _asegurar_jugador(datos: Dict, nombre: str):
    if nombre not in datos['jugadores']:
        datos['jugadores'][nombre] = {
            'victorias': 0,
            'partidas_jugadas': 0,
            'ultima_partida': None
        }


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def registrar_partida(ganador: str, jugadores: List[str]):
    """
    Registra el resultado de una partida terminada.
    :param ganador:   nombre del jugador ganador
    :param jugadores: lista con los nombres de TODOS los participantes
    """
    datos = _cargar()
    ahora = datetime.now().isoformat(timespec='seconds')

    # Guardar registro de la partida
    partida = {
        'id': len(datos['partidas']) + 1,
        'fecha': ahora,
        'ganador': ganador,
        'jugadores': jugadores
    }
    datos['partidas'].append(partida)

    # Actualizar contadores por jugador
    for nombre in jugadores:
        _asegurar_jugador(datos, nombre)
        datos['jugadores'][nombre]['partidas_jugadas'] += 1
        datos['jugadores'][nombre]['ultima_partida'] = ahora
        if nombre == ganador:
            datos['jugadores'][nombre]['victorias'] += 1

    _guardar(datos)
    print(f'[Stats] Partida #{partida["id"]} registrada. Ganador: {ganador}')


def ranking(top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Devuelve los jugadores con más victorias, ordenados de mayor a menor.
    :param top_n: cuántos jugadores mostrar (default 10)
    :return: lista de dicts con nombre, victorias, partidas_jugadas, win_rate
    """
    datos = _cargar()
    resultado = []
    for nombre, stats in datos['jugadores'].items():
        pj = stats['partidas_jugadas']
        vic = stats['victorias']
        wr = round(vic / pj * 100, 1) if pj > 0 else 0.0
        resultado.append({
            'nombre': nombre,
            'victorias': vic,
            'partidas_jugadas': pj,
            'win_rate': wr,
            'ultima_partida': stats.get('ultima_partida', '')
        })

    resultado.sort(key=lambda x: (x['victorias'], x['win_rate']), reverse=True)
    return resultado[:top_n]


def probabilidad_ganar(nombre: str) -> float:
    """
    Calcula la probabilidad histórica (win-rate) de que el jugador gane.
    :return: valor entre 0.0 y 100.0 (porcentaje)
    """
    datos = _cargar()
    if nombre not in datos['jugadores']:
        return 0.0
    stats = datos['jugadores'][nombre]
    pj = stats['partidas_jugadas']
    if pj == 0:
        return 0.0
    return round(stats['victorias'] / pj * 100, 2)


def historial_jugador(nombre: str, n: int = 5) -> List[Dict[str, Any]]:
    """
    Devuelve las últimas n partidas en las que participó el jugador.
    :return: lista de partidas más recientes primero
    """
    datos = _cargar()
    partidas_del_jugador = [
        p for p in datos['partidas'] if nombre in p['jugadores']
    ]
    # Más recientes primero
    partidas_del_jugador.sort(key=lambda p: p['fecha'], reverse=True)
    return partidas_del_jugador[:n]


def ultimas_partidas(n: int = 5) -> List[Dict[str, Any]]:
    """
    Devuelve las ultimas n partidas registradas, mas recientes primero.
    """
    datos = _cargar()
    partidas = list(datos['partidas'])
    partidas.sort(key=lambda p: p['fecha'], reverse=True)
    return partidas[:n]


def resumen_jugador(nombre: str) -> Dict[str, Any]:
    """
    Devuelve un resumen completo de las estadísticas de un jugador.
    """
    datos = _cargar()
    _asegurar_jugador(datos, nombre)
    stats = datos['jugadores'][nombre]
    pj = stats['partidas_jugadas']
    vic = stats['victorias']
    return {
        'nombre': nombre,
        'victorias': vic,
        'partidas_jugadas': pj,
        'derrotas': pj - vic,
        'win_rate': round(vic / pj * 100, 2) if pj > 0 else 0.0,
        'ultima_partida': stats.get('ultima_partida', 'Nunca'),
        'historial': historial_jugador(nombre, 5)
    }


def imprimir_ranking():
    """Imprime el ranking en consola (útil para debug)."""
    tabla = ranking()
    if not tabla:
        print('[Stats] No hay partidas registradas aún.')
        return
    print('\n=== RANKING PARCHIS3 ===')
    print(f'{"#":<4} {"Jugador":<15} {"Victorias":<10} {"Partidas":<10} {"Win Rate":<10}')
    print('-' * 55)
    for i, j in enumerate(tabla, 1):
        print(f'{i:<4} {j["nombre"]:<15} {j["victorias"]:<10} {j["partidas_jugadas"]:<10} {j["win_rate"]:>6.1f}%')
    print()
