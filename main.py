import pygame, sys
import server
import re
import time
from socket import socket, error
from threading import Thread
from cliente import Cliente,Cuadro
from settings import *
from estadisticas import ranking, probabilidad_ganar, historial_jugador
from recomendacion import obtener_recomendacion


nickname_regex = r'[a-zA-Z0-9]'


# Estableciendo la comunicación con el servidor
s = socket()
servidor_lanzado = False 

while True:
    try:
        # Conectamos a tu propia PC
        s.connect(("127.0.0.1", 8000))
        print("¡Conectado exitosamente!")
        break 
    except error:
        # if not servidor_lanzado:
        #     print('Error, servidor no encontrado\nCreando servidor....')
        #     servidor = Thread(target=server.iniciar_servidor)
        #     servidor.daemon = True 
        #     servidor.start()
        #     servidor_lanzado = True
        
        # Esperamos un segundo para no saturar el sistema
        print('Esperando al servidor... asegúrate de haber corrido server.py')
        time.sleep(2)
        s = socket()

cliente = Cliente(s, '')


escucha = Thread(target=cliente.recibir)
escucha.start()

cliente.colores_disponibles = colores_parques.copy()



def imprimirFicha(imagen, ficha, pantalla):
    x, y = imagen.get_size()
    pos_x = ficha[0]-x//2
    pos_y = ficha[1]-y//2
    pantalla.blit(imagen,(pos_x, pos_y))

def ficha_seleccionada(pos_raton, cliente: Cliente):
    index = 0
    seleccionada = False
    ficha_selec = None
    for ficha in cliente.jugadores[cliente.index_jugador]['fichas']:
        left = ficha[0] - tam_ficha[0]
        right = left + 2*tam_ficha[0]
        up = ficha[1] - tam_ficha[1]
        bottom = up + 2*tam_ficha[1]
        if pos_raton[0] >= left and pos_raton[0] <= right and pos_raton[1] >= up and pos_raton[1] <= bottom:
            seleccionada = True
            ficha_selec = ficha
            break
        index +=1
    if seleccionada:
        if cliente.saca_ficha:
            fin = final_fichas[cliente.color]
            casa = casas[cliente.color]
            if not ficha_selec in fin:
                cliente.jugadores[cliente.index_jugador]['fichas'][index] = casa [-1]
                cliente.saca_ficha = False
                cliente.mover(0)
        elif ficha_selec in carcel_fichas[cliente.color] and cliente.dados[0] == cliente.dados[1]:
            cliente.jugadores[cliente.index_jugador]['fichas'][index] = casillas[salidas[cliente.color]]
            cliente.cantidad_movimientos -= cliente.dados[0] + 1
            cliente.limpiar_posiciones(cliente.dados[0] + 1)
            cliente.mover(cliente.dados[0] + 1)

        else:
            print('Ficha seleccionada')
            cliente.posibilidades.empty()
            if cliente.list_aux[index]:
                cliente.posibilidades.add(cliente.list_aux[index].copy())

def centrar(pantalla, txt_render, pos):
    w, h = txt_render.get_size()
    x, y = pos[0] - w//2, pos[1]-h//2
    pantalla.blit(txt_render,(x,y))


def juego():
    #------------------- Pantalla de inicio (sala de espera)----------#
    global cliente
    cliente.conexion() 
    ventana_cerrada = False
    inicial_cuadros = (POS_COLORES[0]+80, POS_COLORES[1])
    base_font = pygame.font.SysFont('arial',20,True)
    base_render = pygame.font.SysFont('arial', 25, True,True)
    info_render = base_font.render(cliente.info,True, NEGRO)
    parchis_render = base_font.render('', True, NEGRO)
    nombre_render = base_font.render('Nombre:', True, NEGRO)
    color_render = base_font.render('Color:', True, NEGRO)
    intro_render = base_font.render('', True, NEGRO)
    jugadores_render = base_font.render('Jugadores', True, NEGRO)
    pantalla = pygame.display.set_mode([ANCHO, ALTO])
    pygame.display.set_caption("Parchis")

    #--------------
    fin = False

    #==================================Portada==================================
    finPortada = False
    while (not fin) and (not finPortada):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fin = True
            # CAMBIO AQUÍ: Solo avanza si se presiona la tecla ESPACIO (o la que prefieras)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    finPortada = True
        
        fondo_inicio = pygame.image.load("imagenes/fondo.png")
        pantalla.blit(fondo_inicio,(0,0))
        pygame.display.flip()
    #===========================================================================

    #==============================Instrucciones 1==============================
    finInst1 = False
    while (not fin) and (not finInst1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fin = True
            if event.type == pygame.KEYDOWN:
                finInst1 = True
            fondo_instrucciones = pygame.image.load("imagenes/instrucciones.png")
            pantalla.blit(fondo_instrucciones, (0,0))
            pygame.display.flip()
    #-------------------------------
    
    
    while not cliente.inicia:
        user_tex=""
        lista_jugadores = {}
        colores = pygame.sprite.Group()

        contador_alerta = 500
        alerta = ''
        contador_repetido = 700
        repetido_txt = cliente.repetido
        repetido_render = base_font.render(cliente.repetido, True, ROJO)
        n = 0
        for color_name, color in cliente.colores_disponibles.items():
            pos = (inicial_cuadros[0]+(n*GRID),inicial_cuadros[1])
            n += 1
            cuadro = Cuadro(pos,color,(TAMAÑO_CUADRO, TAMAÑO_CUADRO), color_name, cliente)
            colores.add(cuadro)
        w, h = jugadores_render.get_size()
        POS_LISTOS = (POS_LISTA[0] + w +10, POS_LISTA[1])
        listos_render = base_font.render(cliente.listos, True, NEGRO)
        listos = cliente.listos
        while not cliente.inicia:
            
            pantalla.fill(color_fondo)
            logo = pygame.image.load("imagenes/logo.png")
            pantalla.blit(logo,(220,10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ventana_cerrada = True
                    cliente.socket.close()
                    sys.exit()
                if cliente.info == '':
                    if event.type == pygame.KEYDOWN :
                        if event.key == pygame.K_BACKSPACE and cliente.registrado is False:
                            user_tex=user_tex[:-1]
                        # Cuando presiona TAB se registra en el juego con el nombre y color que haya indicado
                        elif event.key == pygame.K_TAB and cliente.registrado is False:
                            # Se verifica que exista un color selecionado y un nombre
                            if user_tex == '':
                                alerta = 'Por favor ingrese un nombre'
                                alerta= base_font.render(alerta,True, ROJO)
                            elif cliente.color == '':
                                alerta = 'Por favor seleccione un color'
                                alerta = base_font.render(alerta,True, ROJO)
                            else:
                                #inicio=False
                                cliente.nombre = user_tex
                                cliente.registrar()

                        elif event.key == pygame.K_RETURN and cliente.listo is False and cliente.registrado:
                            cliente.preparado()
            
                        elif re.match(nickname_regex,event.unicode) != None and len(user_tex) < 10 :
                            user_tex+= event.unicode

                    # Selcción del color
                    if event.type == pygame.MOUSEBUTTONDOWN and cliente.registrado is False:
                        pos_raton = pygame.mouse.get_pos()
                        colores.update(pos_raton)
            
            # Se renderizan y pintan los nombres de los jugadores que se van conectando
            if cliente.nuevo_jugador:
                lista_jugadores = {}
                info_render = base_font.render(cliente.info, True, ROJO)
                for jugador in cliente.jugadores:
                    mensaje = jugador['nombre']
                    if jugador['inicia']:
                        check = '+'
                        check_render = base_font.render(check, True, VERDE_LISTO)
                    else:
                        check = '-'
                        check_render = base_font.render(check, True, ROJO)
                    mensaje_render = base_font.render(mensaje,True, NEGRO)
                    lista_jugadores.setdefault(mensaje_render, check_render)
                cliente.nuevo_jugador = False
            
                if cliente.registrado is False:
                    colores = pygame.sprite.Group()
                    n = 0
                    for color_name, color in cliente.colores_disponibles.items():
                        pos = (inicial_cuadros[0]+(n*GRID),inicial_cuadros[1])
                        n += 1
                        cuadro = Cuadro(pos,color,(TAMAÑO_CUADRO, TAMAÑO_CUADRO), color_name, cliente)
                        colores.add(cuadro)
            
            n = 0
            for jugador, check in lista_jugadores.items():
                pos = (POS_LISTA[0], POS_LISTA[1]+(n*GRID))
                w, _h = jugador.get_size()
                x, y = pos[0] + w + 5, pos[1]
                pantalla.blit(jugador, pos)
                pantalla.blit(check, (x, y))
                n += 1
            #------------------------------------------------------------------#
            if len(cliente.colores_disponibles.keys()) == 1 and cliente.registrado:
                colores = pygame.sprite.Group()
                color = cliente.colores_disponibles[cliente.color]
                cuadro = Cuadro(inicial_cuadros,color, (TAMAÑO_CUADRO, TAMAÑO_CUADRO), cliente.color, cliente)
                colores.add(cuadro)
            
            if alerta != '':
                centrar(pantalla, alerta, (ANCHO // 2, 400))
                contador_alerta -= 1
                if contador_alerta == 0:
                    alerta = ''
                    contador_alerta = 500

            if repetido_txt != cliente.repetido:
                repetido_render = base_font.render(cliente.repetido, True, ROJO)
                repetido_txt = cliente.repetido

            if cliente.repetido != '':
                centrar(pantalla, repetido_render, (ANCHO // 2, 400))
                contador_repetido -=1
                if contador_repetido == 0:
                    cliente.repetido = ''
                    repetido_txt = ''
                    contador_repetido = 700

            
            if cliente.listos != listos:
                listos_render = base_font.render(cliente.listos, True, NEGRO)
                listos = cliente.listos
            

            pantalla.blit(info_render, (50, 375))

            centrar(pantalla, parchis_render, (ANCHO // 2, 50))
            
            pantalla.blit(nombre_render,POS_USERNAME)

            pantalla.blit(color_render,POS_COLORES)

            pantalla.blit(jugadores_render,(POS_LISTA[0], POS_LISTA[1]- GRID))

            pantalla.blit(listos_render, POS_LISTOS)

            if cliente.info == '':
                centrar(pantalla, intro_render, (ANCHO//2, 100))

            colores.draw(pantalla)

            if cliente.color_select:
                for color in colores:
                    if color.color == cliente.color:
                        pygame.draw.lines(color.image, NEGRO, True, color.borders,width=BORDE_COLOR)
                    else:
                        color.image.fill(color.color_pintar)
                cliente.color_select = False
            
            text_surfae=base_font.render(user_tex,True, (0,0,0))
            pantalla.blit(text_surfae,(200,200))
            pygame.display.flip()
        if ventana_cerrada:
            break
        #----------------------- Inicio de la partida -------------------------#
        pantalla = pygame.display.set_mode([ANCHO, ALTO])
        pygame.display.set_caption("Parchis")

        font_jugadores = pygame.font.SysFont('arial', 20)
        nombres_render = []


        for jugador in cliente.jugadores:
            render = font_jugadores.render(jugador['nombre'], True, (0, 0, 0))
            pos = pos_nombres[jugador['color']]
            nombres_render.append((render, pos))

        fuente_selec = pygame.font.SysFont('arial', 20, True)
        selecciona1 = 'Seleccione la ficha'
        seleccion2 = 'a mover'
        selecciona1_render = fuente_selec.render(selecciona1, True, NEGRO)
        selecciona2_render = fuente_selec.render(seleccion2,True, NEGRO)
        saca_ficha1 = 'Saca una ficha'
        saca_ficha2 = 'del juego'

        saca_ficha1_render = fuente_selec.render(saca_ficha1, True, VERDE)
        saca_ficha2_render = fuente_selec.render(saca_ficha2, True, VERDE)
        while cliente.inicia and cliente.ganador == '':
            turno = cliente.turno
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ventana_cerrada = True
                    cliente.socket.close()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and cliente.turno == 'Tú':
                        # Tecla R: pedir recomendación de IA
                        jugador_actual = cliente.jugadores[cliente.index_jugador]
                        cliente.recomendacion = obtener_recomendacion(
                            cliente.dados, jugador_actual, cliente.jugadores)
                    if event.key == pygame.K_l and len(cliente.list_aux) == 0:
                        if cliente.turno == 'Tú':
                            cliente.Actualizar_dados()
                            
                        else:
                            #Mandar un mensaje de que no es su turno
                            pass
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos_raton = pygame.mouse.get_pos()

                    if cliente.list_aux or cliente.saca_ficha:
                        ficha_seleccionada(pos_raton, cliente)

                    if cliente.posibilidades:
                        cliente.posibilidades.update(pos_raton)
                        cliente.mueve_ficha = False
                
            pantalla.fill(color_fondo)
            pantalla.blit(fondo, (0,0))

            # Se imprimen las cuatro fichas de cada jugador en partida
            for jugador in cliente.jugadores:
                for ficha in jugador['fichas']:
                    imagen = fichas_imagenes[jugador['color']]
                    imprimirFicha(imagen, ficha, pantalla)
                    
                    
            # Se imprimen los nombres de los jugadores en partida
            for nombre in nombres_render:
                txt, pos = nombre
                pantalla.blit(txt, pos)

            #Impresion de los dos dados
            pantalla.blit(Lista_dado[cliente.dados[0]], (570,250))
            pantalla.blit(Lista_dado[cliente.dados[1]], (644,250))
            Mensaje = 'Tecla L para lanzar'
            fuente = pygame.font.SysFont('arial', 20)
            Mensaje = fuente.render(Mensaje, True, (0, 0, 0))
            pantalla.blit(Mensaje, (570,320)) 


            #Imprimir usuario
            Mensaje = 'Usuario: '+ cliente.nombre 
            fuente = pygame.font.SysFont('arial', 20)
            Mensaje = fuente.render(Mensaje,True, (0, 0, 0))
            pantalla.blit(Mensaje, (550,100))
            cliente.posibilidades.draw(pantalla)

            #Imprimir turno
            Mensaje = 'Turno: '+ turno
            fuente = pygame.font.SysFont('arial', 20)
            Mensaje = fuente.render(Mensaje, True, (0, 0, 0))
            pantalla.blit(Mensaje, (550,150))

            # Mostrar recomendación de IA (tecla R)
            if cliente.recomendacion and cliente.turno == 'Tú':
                rec = cliente.recomendacion
                fuente_rec = pygame.font.SysFont('arial', 17)
                lbl = fuente_rec.render('IA Recomienda (R):', True, (0,180,0))
                pantalla.blit(lbl, (530, 370))
                rec_txt1 = f'Ficha {rec["ficha"]} → {rec["movimiento"]} casillas'
                rec_txt2 = rec.get('justificacion','')[:55]
                r1 = fuente_rec.render(rec_txt1, True, (0,150,0))
                r2 = fuente_rec.render(rec_txt2, True, (80,80,80))
                pantalla.blit(r1, (530, 390))
                pantalla.blit(r2, (530, 410))

            pygame.display.flip()
            #fps.tick(60)      

            #Imprime mensaje de selecionar la ficha a mover
            if cliente.turno == 'Tú' and not cliente.posibilidades and cliente.list_aux:
                pantalla.blit(selecciona1_render, (530, 340))
                pantalla.blit(selecciona2_render, (530, 340))
            
            #Imprime mensaje para sacar la ficha que quiera
            if cliente.saca_ficha:
                pantalla.blit(saca_ficha1_render, (513, 100))
                pantalla.blit(saca_ficha2_render, (513, 120))

        if ventana_cerrada:
            break
        if cliente.inicia:
            cliente.inicia = False
            
        pantalla = pygame.display.set_mode([ANCHO, ALTO])
        pygame.display.set_caption("Parchis")
        #captura = pygame.image.load('screenshot.jpg')
        continua = False

        ganador = cliente.ganador
        jugador = cliente.nombre

        
        txt_ganador = ''
        if ganador == jugador:
            txt_ganador = '¡Ganaste!'
        else:
            txt_ganador = f'Ganó {ganador}'
        txt_render = base_render.render(txt_ganador, True, WHITE)
        opciones = base_font.render('', True, WHITE)

        cliente.fichas = [] #Lista de las fichas del jugador
        cliente.color = ''
        cliente.color_select = False
        cliente.turno = ''
        cliente.info = ''
        cliente.carcel = True
        cliente.saca_ficha = False
        cliente.inicia = False
        cliente.listo = False
        cliente.nuevo_jugador = False
        cliente.mueve_ficha = False
        cliente.cantidad_movimientos = 0
        cliente.posibilidades = pygame.sprite.Group()
        cliente.list_aux = []
        cliente.registrado = False # Atributo que indica si el cliente ya se registro
        cliente.dados = [0, 0]
        cliente.jugadores = []
        cliente.index_jugador = 0
        cliente.ficha = None
        cliente.ganador = ''
        cliente.listos = ''
        # Controla el primer lanzamiento del jugador
        cliente.primero = False
        cliente.colores_disponibles = colores_parques.copy()
        cliente.movimientos=[]

        while not continua:
            #pantalla.blit(captura,(0, 0))
            pygame.draw.rect(pantalla, (0, 0, 0, 1),(0,0,ANCHO,ALTO))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ventana_cerrada = True
                    cliente.socket.close()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        continua = True
                        cliente.inicia = True
                        ventana_cerrada = True
                    elif event.key == pygame.K_RETURN:
                        continua = True
                        cliente.inicia = False
            
            centrar(pantalla, txt_render, (ANCHO // 2, ALTO // 2))
            centrar(pantalla, opciones, (ANCHO // 2, 400))
            pygame.display.flip()
        if ventana_cerrada:
            break
    pygame.quit()

inicio = Thread(target=juego)
inicio.start()