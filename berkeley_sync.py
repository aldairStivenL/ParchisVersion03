# ============================================================
#  Módulo: Sincronización de Tiempo - Algoritmo de Berkeley
#  Parchis3 - Sistemas Distribuidos UTP
#  Generado con asistencia de IA (Claude - Anthropic)
# ============================================================
"""
Algoritmo de Berkeley (simplificado):
1. El servidor maestro solicita la hora local a todos los clientes.
2. Cada cliente responde con su timestamp actual.
3. El servidor calcula el promedio de todos los tiempos (incluyendo el suyo).
4. El servidor envía a cada cliente el AJUSTE (delta) que debe aplicar.
5. Cada cliente ajusta su reloj local sumando el delta recibido.

Se integra con el servidor principal de Parchis3 en el momento
en que se inicia una nueva partida (todos los jugadores listos).
"""

import time
import json
import threading


class BerkeleyMaestro:
    """Ejecuta el rol de maestro del algoritmo de Berkeley en el servidor."""

    def __init__(self, clientes_registrados: list):
        """
        :param clientes_registrados: lista de objetos Cliente del servidor,
                                     cada uno con .socket y .enviar()
        """
        self.clientes = clientes_registrados
        self.tiempos_recibidos = {}   # nombre -> timestamp del cliente
        self.lock = threading.Lock()
        self.evento_listo = threading.Event()

    # ------------------------------------------------------------------
    # Paso 1 y 2: Solicitar hora a todos los clientes
    # ------------------------------------------------------------------
    def solicitar_tiempos(self):
        """Envía a cada cliente una solicitud de sincronización."""
        msj = {
            'tipo': 'sync_solicitud',
            'contenido': time.time()       # timestamp del maestro al enviar
        }
        for cliente in self.clientes:
            try:
                cliente.enviar(msj)
            except Exception as e:
                print(f'[Berkeley] No se pudo contactar a {cliente.name}: {e}')

    # ------------------------------------------------------------------
    # Paso 2 (receptor): Registrar la respuesta de un cliente
    # ------------------------------------------------------------------
    def registrar_tiempo(self, nombre: str, timestamp_cliente: float):
        with self.lock:
            self.tiempos_recibidos[nombre] = timestamp_cliente
            if len(self.tiempos_recibidos) == len(self.clientes):
                self.evento_listo.set()

    # ------------------------------------------------------------------
    # Paso 3: Calcular promedio
    # ------------------------------------------------------------------
    def _calcular_promedio(self) -> float:
        tiempo_maestro = time.time()
        todos = list(self.tiempos_recibidos.values()) + [tiempo_maestro]
        promedio = sum(todos) / len(todos)
        return promedio

    # ------------------------------------------------------------------
    # Paso 4 y 5: Enviar deltas a cada cliente
    # ------------------------------------------------------------------
    def enviar_deltas(self):
        promedio = self._calcular_promedio()
        print(f'[Berkeley] Tiempo promedio calculado: {promedio:.4f}')
        for cliente in self.clientes:
            t_cliente = self.tiempos_recibidos.get(cliente.name, time.time())
            delta = promedio - t_cliente
            msj = {
                'tipo': 'sync_delta',
                'contenido': delta
            }
            try:
                cliente.enviar(msj)
                print(f'[Berkeley] Delta para {cliente.name}: {delta:+.4f}s')
            except Exception as e:
                print(f'[Berkeley] Error enviando delta a {cliente.name}: {e}')

    # ------------------------------------------------------------------
    # Método principal: ejecutar sincronización completa
    # ------------------------------------------------------------------
    def sincronizar(self, timeout: float = 5.0):
        """
        Ejecuta el ciclo completo de sincronización Berkeley.
        Bloquea hasta que todos los clientes responden o se agota el timeout.
        """
        print('[Berkeley] Iniciando sincronización...')
        self.tiempos_recibidos.clear()
        self.evento_listo.clear()

        self.solicitar_tiempos()

        # Esperar respuestas (con timeout por si algún cliente no responde)
        self.evento_listo.wait(timeout=timeout)

        if not self.evento_listo.is_set():
            nombres_faltantes = [
                c.name for c in self.clientes
                if c.name not in self.tiempos_recibidos
            ]
            print(f'[Berkeley] Timeout. Clientes sin respuesta: {nombres_faltantes}')

        self.enviar_deltas()
        print('[Berkeley] Sincronización completada.')


class BerkeleyCliente:
    """
    Gestiona el ajuste de tiempo en el lado del cliente.
    El cliente de pygame mantiene un offset que suma a time.time()
    para obtener el "tiempo sincronizado".
    """

    def __init__(self):
        self._offset: float = 0.0    # segundos a sumar a time.time()

    # Llamar esto cuando llega un mensaje 'sync_delta' del servidor
    def aplicar_delta(self, delta: float):
        self._offset += delta
        print(f'[Berkeley-Cliente] Offset ajustado: {self._offset:+.4f}s')

    def tiempo_sync(self) -> float:
        """Devuelve el tiempo local ajustado por Berkeley."""
        return time.time() + self._offset

    def responder_solicitud(self, enviar_fn):
        """
        Llamar cuando el cliente recibe 'sync_solicitud'.
        :param enviar_fn: función enviar(dict) del cliente de red.
        """
        msj = {
            'tipo': 'sync_respuesta',
            'contenido': time.time()
        }
        enviar_fn(msj)
