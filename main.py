import logging
from threading import Thread
from attack import attack
from clients import clients_attack, address_create

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    a_addr = address_create()
    b_addr = address_create()
    ab = Thread(target=clients_attack, args=[a_addr, b_addr], daemon=True)
    sniff = Thread(target=attack, args=[a_addr], daemon=True)
    sniff.start()
    ab.start()
    ab.join(10)
    sniff.join(10)
