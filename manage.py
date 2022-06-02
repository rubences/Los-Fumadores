#!/usr/bin/env python3
import os

from storage import codes, store


def get_port():
    while True:
        try:
            port = int(input('Puerto (1024 - 49151): '))
            if port >= 1024 and port <= 49151:
                break
        except Exception:
            pass
    return port


if __name__ == '__main__':
    os.system('clear')
    while True:
        print ('1. Agente')
        print ('2. Fumador')
        type = input('Opcion: ')
        if type in ['1', '2']:
            break
        else:
            os.system('clear')
    os.system('clear')
    if type == '1':
        # Agente
        print ('Agente')
        from agent import init
        init(get_port())
    else:
        # Fumador
        while True:
            print ('Fumador')
            for i in codes:
                print ('{}. {}'.format(i, store[i].get('name')))
            type = input('Opcion: ')
            if type in codes:
                break
            else:
                os.system('clear')

        ip = input('Ip del agente: ')
        from smoker import init
        init(ip, get_port(), type)
