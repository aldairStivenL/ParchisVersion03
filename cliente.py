import pygame
import random
import json
from berkeley_sync import BerkeleyCliente
from recomendacion import obtener_recomendacion
#from settings import casillas, casas, carcel_fichas, final_fichas, BORDE_COLOR, colores_parques
from settings import *

class Cliente:
    def __init__(self, socket, nombre):
        self.socket = socket
        self.nombre = nombre
        self.fichas = [] #Lista de las fichas del jugador
        self.color = ''
        self.color_select = False
        self.turno = ''
        self.info = ''
        self.repetido = ''
        self.carcel = True
        self.saca_ficha = False
        self.inicia = False
        self.listo = False
        self.nuevo_jugador = False
        self.mueve_ficha = False
        self.cantidad_movimientos = 0
        self.posibilidades = pygame.sprite.Group()
        self.list_aux = []
        self.registrado = False # Atributo que indica si el cliente ya se registro
        self.dados = [0, 0]
        self.jugadores = []
        self.index_jugador = 0
        self.ficha = None
        self.ganador = ''
        self.listos = ''
        # Controla el primer lanzamiento del jugador
        self.primero = False
        self.colores_disponibles = None
        self.movimientos=[]
        self.fichas_movidas_turno = []
        # Sincronización Berkeley
        self.berkeley = BerkeleyCliente()
        # Última recomendación de IA
        self.recomendacion = None
    


    #Formato para los mensajes:
    #msj = [name_player,self.fichas]
    def enviar(self, mensaje):
        mensaje = json.dumps(mensaje) + '\n'
        self.socket.sendall(mensaje.encode())
    
    def limpiar_posiciones(self, diff, indice_ficha=None):
        self.posibilidades.empty()
        if indice_ficha is not None and indice_ficha not in self.fichas_movidas_turno:
            self.fichas_movidas_turno.append(indice_ficha)
        if diff in self.movimientos:
            self.movimientos.remove(diff)

        if self.cantidad_movimientos <= 0:
            self.list_aux = []
            self.movimientos = []
            return 0

        movimiento_suma = sum(valores_dados(self.dados))
        if len(valores_dados(self.dados)) > 1 and movimiento_suma in self.movimientos:
            self.movimientos.remove(movimiento_suma)

        jugador = self.jugadores[self.index_jugador]
        posiciones = calcular_posibles_movimientos(
            jugador['fichas'],
            self.movimientos,
            jugador['color']
        )
        self.list_aux = []
        for indice_ficha, (ficha, posis) in enumerate(zip(jugador['fichas'], posiciones)):
            temp = []
            if indice_ficha in self.fichas_movidas_turno:
                self.list_aux.append(temp)
                continue
            for indice, pos in enumerate(posis):
                if pos == MOVIMIENTO_INVALIDO:
                    continue
                u = Ubicacion(pos, (0, 0, 0), (15, 15), ficha, self)
                u.diff = self.movimientos[indice]
                temp.append(u)
            self.list_aux.append(temp)
        if not any(self.list_aux):
            restante = self.cantidad_movimientos
            self.cantidad_movimientos = 0
            self.movimientos = []
            self.list_aux = []
            return restante
        return 0

    def recibir(self):
        flujo = self.socket.makefile('r', encoding='utf-8')
        while True:
            try:
                recibe = flujo.readline()
                if not recibe:
                    break
            except Exception as e:
                print(f'Error: {e}')
                break
            else:
                mensaje = json.loads(recibe)
                tipo = mensaje['tipo']
                contenido = mensaje['contenido']

                # -------------- Respuestas del servidor para la pantalla de inicio -------------------#
                # --- Manejo de mensajes Berkeley ---
                if tipo == 'sync_solicitud':
                    self.berkeley.responder_solicitud(self.enviar)
                    continue
                elif tipo == 'sync_delta':
                    self.berkeley.aplicar_delta(contenido)
                    continue
                # -----------------------------------
                if not self.inicia:
                    if tipo == 'registro':
                        self.jugadores.append(contenido)

                        for jugador in self.jugadores:
                            if jugador['nombre'] == self.nombre:
                                self.index_jugador = self.jugadores.index(jugador)
                                break
                    
                        self.nuevo_jugador = True
                        # Se elimina el color del nuevo jugador de los disponibles
                        if self.registrado is False:
                            self.colores_disponibles.pop(contenido['color'])
                    
                    elif tipo == 'conexion':
                        self.nuevo_jugador = True
                        self.jugadores = contenido
                        for jugador in contenido:
                            self.colores_disponibles.pop(jugador['color'])
                    
                    elif tipo == 'iniciar juego':
                        self.inicia = True

                        if contenido == self.nombre:
                            self.turno = 'Tú'
                        else:
                            self.turno = contenido
                    elif tipo == 'actualizar':
                        self.nuevo_jugador = True
                        if isinstance(contenido[0], list):
                            self.jugadores = contenido[0]
                            self.colores_disponibles.setdefault(contenido[1], colores_parques[contenido[1]])
                        else:
                            self.jugadores = contenido
                    elif tipo == 'info':
                        if isinstance(contenido,list):
                            self.nuevo_jugador = True
                            self.jugadores = contenido[-1]
                            for jugador in self.jugadores:
                                self.colores_disponibles.pop(jugador['color'])
                            self.info = contenido[0]
                        else:
                            self.nuevo_jugador = True
                            self.info = contenido
                    elif tipo == 'ganador':
                        self.color = ''
                        self.color_select = False
                        self.nuevo_jugador = True
                        self.turno = ''
                        self.ganador = ''
                        self.listo = False
                        self.info = ''
                        self.listos = ''
                        self.colores_disponibles = colores_parques.copy()
                        self.jugadores.clear()
                    elif tipo == 'repetido':
                        self.repetido = contenido[0]
                        self.registrado = contenido[1]
                        if self.registrado:
                            # Se eliminan todos los colores excepto el que eligio el jugador
                            self.colores_disponibles = {
                                self.color:self.colores_disponibles[self.color]
                            }
                    listo = 0
                    for jugador in self.jugadores:
                        if jugador['inicia']:
                            listo += 1
                    if listo != 0 or len(self.jugadores) > 1:
                        self.listos = f'Listos({listo}\\{len(self.jugadores)})'
                    else:
                        self.listos = ''
                
                # ------------- Respuestas del servidor una vez iniciado el juego --------------#
                
                else:
                    if tipo == 'turno' or tipo == 'juegue':
                        self.list_aux = []
                        self.posibilidades.empty()
                        self.movimientos = []
                        self.fichas_movidas_turno = []
                        self.cantidad_movimientos = 0
                        if tipo == 'juegue':
                            self.primero = True
                        if contenido == self.nombre:
                            self.turno = 'Tú'
                        else:
                            self.turno = contenido
                    elif tipo == 'posibilidades':
                        
                        fichas = []
                        for jugador in self.jugadores:
                            if jugador['nombre'] == self.nombre:
                                fichas = jugador['fichas']
                                break
                        
                        self.cantidad_movimientos = contenido[0]
                        self.movimientos = contenido[1]
                        posiciones = contenido[2]
                        self.list_aux = []
                        self.posibilidades.empty()
                        self.fichas_movidas_turno = []
                        for ficha, posis in zip(fichas, posiciones):
                            temp = []
                            for indice, pos in enumerate(posis):
                                if pos != MOVIMIENTO_INVALIDO and not ficha in carcel_fichas[self.color]:
                                    u = Ubicacion(pos, (0, 0, 0),(15, 15), ficha, self)
                                    u.diff = self.movimientos[indice]
                                    temp.append(u)
                            self.list_aux.append(temp.copy())

                    elif tipo == 'mueve fichas':
                        # Aca simplemente se actualizan las posiciones 
                        self.jugadores = contenido.copy()
                    elif tipo == 'sacar ficha':
                        self.saca_ficha = contenido
                    elif tipo == 'ganador':
                        self.ganador = contenido

    def registrar(self):
        dic = {
            'tipo':'registro',
            'contenido':{
                'nombre':self.nombre,
                'color':self.color
            }
        }
        self.enviar(dic)
    

    def conexion(self):
        dic = {
            'tipo':'conexion',
            'contenido':''
        }
        self.enviar(dic)
    
    def preparado(self):
        self.listo = True
        self.jugadores[self.index_jugador]['inicia'] = True
        dic ={
            'tipo':'listo',
            'contenido':self.jugadores
        }
        self.enviar(dic)

    def solicita_fichas(self):
        dic = {
            'tipo':'fichas',
            'contenido':self.color
        }
        self.enviar(dic)
    

    def Actualizar_dados(self):
        dado_1 = random.randint(0,5)
        dado_2 = random.randint(0,5)
        #dado_1 = 3
        #dado_2 = 3
        self.dados = [dado_1, dado_2]
        if self.primero and self.turno in ('Tú', 'TÃº', 'TÃƒÂº'):
            jugador = self.jugadores[self.index_jugador]
            if debe_lanzar_un_dado(jugador['fichas'], jugador['color']):
                self.dados = [dado_1]

        dict = {
            'tipo':'',
            'contenido':self.dados
        }
        if self.primero:
            dict['tipo'] = 'tiro'
        else:
            dict['tipo'] = 'primer'
        
        self.enviar(dict)
    
    def mover(self, cantidad):
        dict = {
            'tipo':'mover',
            'contenido':[cantidad, self.jugadores]
        }
        self.enviar(dict)

class Cuadro(pygame.sprite.Sprite):
    def __init__(self, pos, color, dimensiones, color_name, cliente):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(dimensiones)
        self.image.fill(color)
        self.color_pintar = color
        self.rect = self.image.get_rect()
        self.color = color_name
        self.rect.x = pos[0]  # Defino su posicion
        self.rect.y = pos[1]
        self.cliente = cliente
        w, h = self.image.get_size()
        self.borders = [
            (0, 0),
            (w  - BORDE_COLOR // 2 , 0),
            (w  - BORDE_COLOR // 2, h - BORDE_COLOR // 2),
            (0, h - BORDE_COLOR//2)
        ]
    

    def update(self, pos_raton):
        if pos_raton[0] >= self.rect.left and pos_raton[1] >= self.rect.top and pos_raton[1] <= self.rect.bottom and pos_raton[0] <= self.rect.right:
            self.cliente.color = self.color
            self.cliente.color_select = True

class Ubicacion(pygame.sprite.Sprite):
    def __init__(self, pos, color, dimensiones, ficha, cliente: Cliente):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(dimensiones)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]  # Defino su posicion
        self.rect.y = pos[1]
        self.ficha = ficha
        self.cliente = cliente
        self.diff = 0


    def update(self, pos_raton):
        if pos_raton[0] >= self.rect.left and pos_raton[1] >= self.rect.top and pos_raton[1] <= self.rect.bottom and pos_raton[0] <= self.rect.right:
            if not self.cliente.mueve_ficha:
                index = self.cliente.jugadores[self.cliente.index_jugador]['fichas'].index(self.ficha)
                self.cliente.cantidad_movimientos -= self.diff
                pos = [self.rect.x, self.rect.y]
                self.cliente.jugadores[self.cliente.index_jugador]['fichas'][index] = pos
                fichas_casa = 0
                jugador = self.cliente.jugadores[self.cliente.index_jugador]
                final = final_fichas[jugador['color']]
                for ficha in jugador['fichas']:
                    if ficha in final:
                        fichas_casa += 1
                
                if fichas_casa == 3:
                    self.cliente.cantidad_movimientos = 0
                elif fichas_casa == 2:
                    pass
                
                extra_consumido = self.cliente.limpiar_posiciones(self.diff, index)
                
                self.cliente.mover(self.diff + extra_consumido)
                self.cliente.mueve_ficha = True
                
