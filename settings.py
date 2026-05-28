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