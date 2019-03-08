#!/usr/bin/env python

### Put your code below this comment ###
import sys
from ethWrapper import ContractWrapper
from network import *

# === Commands === #
def get(phone_number):
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    res = registrar.get(phone_number)
    if res != '0x0000000000000000000000000000000000000000':
        print('Registered correspondence: ' + res)
    else:
        print('Correspondence not found')


commands = {
    'get': get
}


# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
