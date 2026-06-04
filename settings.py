import pygame

pygame.init()
color_fondo = (225,225,225)
fondo = pygame.image.load("imagenes/tablero.png")

#Cargar ficha amarilla
ficha_amarilla = pygame.image.load("imagenes/amarillo.png")

#Cargar ficha verde
ficha_verde = pygame.image.load("imagenes/verde.png")

#Cargar ficha roja
ficha_rojo = pygame.image.load("imagenes/rojo.png")

#Cargar fichas azul
ficha_azul = pygame.image.load("imagenes/azul.png")

fichas_imagenes = {
    'amarillo':ficha_amarilla, 
    'verde':ficha_verde, 
    'azul':ficha_azul, 
    'rojo':ficha_rojo
}

#Cargar dado
Cara_dado_1 = pygame.image.load("imagenes/Dado1.png")
Cara_dado_2 = pygame.image.load("imagenes/Dado2.png")
Cara_dado_3 = pygame.image.load("imagenes/Dado3.png")
Cara_dado_4 = pygame.image.load("imagenes/Dado4.png")
Cara_dado_5 = pygame.image.load("imagenes/Dado5.png")
Cara_dado_6 = pygame.image.load("imagenes/Dado6.png")

Lista_dado = [Cara_dado_1, Cara_dado_2, Cara_dado_3, Cara_dado_4, Cara_dado_5, Cara_dado_6]

# -----------------------------------------------------------------------------------------------

ANCHO, ALTO = 750,512

WHITE = (255,255,255)

AZUL = (43,143,228)
AMARILLO = (227,227,43)
ROJO = (227,43,43)
VERDE = (43,184,43)
VERDE_LISTO = (28,171,29)
NEGRO = (0,0,0)


POS_USERNAME= (50, 200)
POS_COLORES = (50, 250)
TAMAÑO_CUADRO = 40
GRID = 50
POS_LISTA = (400, 200)

colores_parques = {
    'azul':AZUL,
    'amarillo':AMARILLO,
    'rojo':ROJO,
    'verde':VERDE
}

CANTIDAD_JUGADORES = 4
OPORTUNIDADES_SALIR = 3

BORDE_COLOR = 4

# Posiciones de cada ficha en la carcel
carcel_fichas = {
    'amarillo':[[410, 405],[450, 405],[410, 465],[450, 465]],
    'azul':[[60, 405],[100, 405],[60, 465],[100, 465]],
    'verde':[[410, 55],[450, 55],[410, 115],[450, 115]],
    'rojo':[[60,55],[100,55],[60,115],[100,115]]
}

final_fichas = {
    'verde': [[290, 250], [280, 250], [290, 260], [280, 260]], 
    'rojo': [[250, 213], [250, 223], [265, 213], [265, 223]], 
    'azul': [[225, 260], [225, 250], [240, 260], [240, 250]], 
    'amarillo': [[250, 285], [250, 275], [265, 285], [265, 275]]
}

pos_nombres = {
    'amarillo':(400, 420),
    'azul':(50 , 420),
    'verde':(400, 70),
    'rojo':(50 , 70)
}

casillas = {
    1:[300, 497],
    2:[300, 471],
    3:[300, 446],
    4:[300, 423],
    5:[300, 395],
    6:[300, 372],
    7:[300, 348],
    8:[300, 320],
    9:[318, 300],
    10:[349, 300],
    11:[373, 300],
    12:[400, 300],
    13:[423, 300],
    14:[451, 300],
    15:[476, 300],
    16:[499, 300],
    17:[499, 256],
    18:[499, 213],
    19:[476, 213],
    20:[451, 213],
    21:[423, 213],
    22:[400, 213],
    23:[373, 213],
    24:[349, 213],
    25:[318, 213],
    26:[300, 190],
    27:[300, 162],
    28:[300, 138],
    29:[300, 110],
    30:[300, 86],
    31:[300, 62],
    32:[300, 35],
    33:[300, 11],
    34:[254, 11],
    35:[210, 11],
    36:[210, 35],
    37:[210, 62],
    38:[210, 86],
    39:[210, 110],
    40:[210, 138],
    41:[210, 162],
    42:[210, 190],
    43:[193, 213],
    44:[167, 213],
    45:[140, 213],
    46:[115, 213],
    47:[90, 213],
    48:[64, 213],
    49:[38, 213],
    50:[11, 213],
    51:[11, 256],
    52:[11, 300],
    53:[38, 300],
    54:[64, 300],
    55:[90, 300],
    56:[115, 300],
    57:[140, 300],
    58:[167, 300],
    59:[193, 300],
    60:[210, 320],
    61:[210, 348],
    62:[210, 372],
    63:[210, 395],
    64:[210, 423],
    65:[210, 446],
    66:[210, 471],
    67:[210, 497],
    68:[254, 497]
}

casas = {
    'azul':[[11, 256], [38, 256], [64, 256], [90, 256], [115, 256], [140, 256], [167, 256], [193, 256], [210, 256]],
    'rojo':[[254, 11], [254, 35], [254, 62], [254, 86], [254, 110], [254, 138], [254, 162], [254, 190], [254, 213]],
    'verde':[[499, 256], [476, 256], [451, 256], [423, 256], [400, 256], [373, 256], [349, 256], [318, 256], [300, 256]],
    'amarillo':[[254, 497], [254, 471], [254, 446], [254, 423], [254, 395], [254, 372], [254, 348], [254, 320], [254, 300]]
}

seguros = [12, 17, 29, 34, 46, 51, 63, 68]

salidas = {
    'azul':56,
    'rojo':39,
    'verde':22,
    'amarillo':5
}

tam_ficha = (10, 15)

MOVIMIENTO_INVALIDO = [-15, -15]

def calcular_destino_movimiento(ficha, pasos, color):
    """Calcula la casilla destino para una ficha o None si el movimiento no es valido."""
    if pasos <= 0:
        return None

    if ficha in carcel_fichas[color] or ficha in final_fichas[color]:
        return None

    casa = casas[color]
    if ficha in casa:
        indice_casa = casa.index(ficha) + pasos
        if indice_casa >= len(casa):
            return None
        return casa[indice_casa]

    ls_casillas = list(casillas.values())
    if ficha not in ls_casillas:
        return None

    indice_actual = ls_casillas.index(ficha) + 1
    indice_entrada = ls_casillas.index(casa[0]) + 1

    pasos_a_entrada = indice_entrada - indice_actual
    if pasos_a_entrada < 0:
        pasos_a_entrada += len(casillas)

    if pasos >= pasos_a_entrada:
        indice_casa = pasos - pasos_a_entrada
        if indice_casa >= len(casa):
            return None
        return casa[indice_casa]

    indice_destino = indice_actual + pasos
    if indice_destino > len(casillas):
        indice_destino -= len(casillas)
    return casillas[indice_destino]


def calcular_posibles_movimientos(fichas, movimientos, color):
    """Devuelve una matriz de destinos por ficha respetando el orden de movimientos."""
    posibles = []
    for ficha in fichas:
        destinos = []
        for movimiento in movimientos:
            destino = calcular_destino_movimiento(ficha, movimiento, color)
            destinos.append(destino if destino is not None else MOVIMIENTO_INVALIDO)
        posibles.append(destinos)
    return posibles


def valores_dados(dados):
    """Convierte los dados internos 0-5 a valores 1-6."""
    return [dado + 1 for dado in dados if dado is not None and dado >= 0]


def ficha_activa(ficha, color):
    return ficha not in carcel_fichas[color] and ficha not in final_fichas[color]


def indices_fichas_activas(fichas, color):
    return [i for i, ficha in enumerate(fichas) if ficha_activa(ficha, color)]


def distancia_a_meta(ficha, color):
    """Cantidad exacta de pasos para llegar a la ultima casilla de llegada."""
    if not ficha_activa(ficha, color):
        return None

    casa = casas[color]
    if ficha in casa:
        return len(casa) - 1 - casa.index(ficha)

    ls_casillas = list(casillas.values())
    if ficha not in ls_casillas:
        return None

    indice_actual = ls_casillas.index(ficha) + 1
    indice_entrada = ls_casillas.index(casa[0]) + 1
    pasos_a_entrada = indice_entrada - indice_actual
    if pasos_a_entrada < 0:
        pasos_a_entrada += len(casillas)
    return pasos_a_entrada + len(casa) - 1


def debe_lanzar_un_dado(fichas, color):
    """Solo una ficha activa cerca de la meta lanza un dado."""
    activas = indices_fichas_activas(fichas, color)
    if len(activas) != 1:
        return False
    distancia = distancia_a_meta(fichas[activas[0]], color)
    return distancia is not None and distancia <= 6


def movimientos_desde_dados(dados, fichas, color):
    valores = valores_dados(dados)
    if not valores:
        return []
    if len(valores) == 1:
        return [valores[0]]

    activas = indices_fichas_activas(fichas, color)
    if len(activas) == 1:
        return [sum(valores)]

    return [valores[0], valores[1], sum(valores)]


def calcular_posibles_movimientos_turno(fichas, dados, color):
    """Calcula opciones iniciales evitando jugadas parciales que bloqueen el turno."""
    movimientos = movimientos_desde_dados(dados, fichas, color)
    valores = valores_dados(dados)
    posibles = calcular_posibles_movimientos(fichas, movimientos, color)

    if len(valores) != 2 or len(movimientos) != 3:
        return movimientos, posibles

    dado_1, dado_2 = valores
    for indice_ficha, ficha in enumerate(fichas):
        if not ficha_activa(ficha, color):
            continue

        if posibles[indice_ficha][0] != MOVIMIENTO_INVALIDO:
            llega_a_meta = posibles[indice_ficha][0] == casas[color][-1]
            puede_otro_usar_dado_2 = any(
                otro_indice != indice_ficha
                and ficha_activa(otra_ficha, color)
                and calcular_destino_movimiento(otra_ficha, dado_2, color) is not None
                for otro_indice, otra_ficha in enumerate(fichas)
            )
            if not llega_a_meta and not puede_otro_usar_dado_2:
                posibles[indice_ficha][0] = MOVIMIENTO_INVALIDO

        if posibles[indice_ficha][1] != MOVIMIENTO_INVALIDO:
            llega_a_meta = posibles[indice_ficha][1] == casas[color][-1]
            puede_otro_usar_dado_1 = any(
                otro_indice != indice_ficha
                and ficha_activa(otra_ficha, color)
                and calcular_destino_movimiento(otra_ficha, dado_1, color) is not None
                for otro_indice, otra_ficha in enumerate(fichas)
            )
            if not llega_a_meta and not puede_otro_usar_dado_1:
                posibles[indice_ficha][1] = MOVIMIENTO_INVALIDO

    return movimientos, posibles
