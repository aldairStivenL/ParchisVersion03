# ParchisVersion03

Proyecto de parchis multijugador para Sistemas Distribuidos.

## Requisitos

- Python 3.10 o superior.
- Pygame instalado.
- Ejecutar los comandos desde la carpeta del proyecto.

## Instalacion

1. Abre una terminal en la carpeta donde se ubica el proyecto

2. Instala Pygame si aun no lo tienes:

   ```powershell
   python -m pip install pygame
   ```

## Como iniciar una partida

1. Inicia el servidor en una terminal:

   ```powershell
   python server.py
   ```

   Debe aparecer el mensaje `Servidor escuchando...`.

2. Abre otra terminal por cada jugador que vaya a participar y ejecuta:

   ```powershell
   python main.py
   ```

3. En cada ventana del juego:
   - Presiona `ESPACIO` para pasar la portada.
   - Presiona cualquier tecla para pasar la pantalla de instrucciones.
   - Escribe un nombre.
   - Selecciona un color.
   - Presiona `TAB` para registrarte.
   - Presiona `ENTER` cuando estes listo.

4. Cuando al menos dos jugadores esten listos, inicia la partida.

## Controles durante el juego

- `L`: lanzar dados cuando sea tu turno.
- Clic sobre una ficha: ver sus movimientos disponibles.
- Clic sobre una casilla marcada: mover la ficha a esa posicion.
- `R`: mostrar una recomendacion de jugada.

## Notas

- El servidor debe estar abierto antes de iniciar los clientes.
- Para jugar en la misma maquina, abre varias terminales y ejecuta `python main.py` en cada una.
- Si quieres reiniciar la partida, cierra las ventanas de los clientes y vuelve a iniciar `server.py`.
