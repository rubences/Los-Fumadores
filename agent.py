import threading
import time
from random import choice

import socketserver
from storage import codes, packet_size, store, time_sleep, time_smoke
from utils import _print

global smoke
smoke = False
global smoke_code


class MyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MyTCPServerHandler(socketserver.BaseRequestHandler):

    bufer = ''

    def process(self):
        while True:
            message = self.request.recv(packet_size).decode('UTF-8')
            if message == 'need':
                _print('{}: Necesito {}!'.format(
                    store.get(self.code)['name'],
                    store.get(self.code)['required']
                ))
                if self.smoke_released:
                    self.smoke_released = False
                    global smoke
                    smoke = False

            elif message == 'enable':
                _print('{}: Termino de fumar!'.format(store.get(self.code)['name']))
                self.smoke_released = True
            elif message == 'ack':
                time.sleep(time_smoke)
            elif message == 'exit':
                break
            time.sleep(time_sleep)

    def handle(self):
        # Proceso de reconocimiento
        # cur_thread = threading.current_thread()
        self.code = self.request.recv(packet_size).decode('UTF-8')
        self.rejected = False
        self.smoke_released = False
        _print('Conectando fumador...')
        if store.get(self.code)['flag'] is False:
            store.get(self.code)['request'] = self.request
            store.get(self.code)['flag'] = True
            _print('Fumador aceptado *{}*'.format(store.get(self.code)['name']))
            self.request.send('accepte'.encode('UTF-8'))
            self.process()
        else:
            self.rejected = True
            _print('Fumador rechazado *{}*'.format(store.get(self.code)['name']))
            self.request.send('rejected'.encode('UTF-8'))

    def finish(self):
        _print('Fumador desconectado *{}*'.format(store.get(self.code)['name']))
        if self.rejected is False:
            store.get(self.code)['flag'] = False
        global smoke_code
        if smoke_code == self.code:
            global smoke
            smoke = False

    def handle_timeout(self):
        print('tiempo de espera agotado')


def verify_smoking():
    # Se verifica si estan todos los fumadores conectados
    while True:
        active_smokers = True
        for i in codes:
            if store[i].get('flag') is False:
                active_smokers = False
                break
        time.sleep(time_sleep)
        if active_smokers and smoke is False:
            break
        else:
            if active_smokers is False:
                _print('Agente: Esperando todos los fumadores')


def init(port):
    try:
        server = MyTCPServer(('0.0.0.0', port), MyTCPServerHandler)
        server.timeout = 10
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.timeout = 10
        # iniciando agente
        _print("Esperando fumadores...")
        server_thread.daemon = True
        server_thread.start()

        while True:
            verify_smoking()
            global smoke_code
            smoke_code = choice(codes)

            _print('Agente: Tengo disponible {}!'.format(
                store.get(smoke_code)['required']
            ))
            global smoke
            smoke = True
            store.get(smoke_code)['request'].send('enable'.encode('UTF-8'))
            _print('Agente: fumador {} servido!'.format(store.get(smoke_code)['name']))

    except KeyboardInterrupt:
        _print('Cerrando conexiones...')
        server.shutdown()
        server.server_close()
