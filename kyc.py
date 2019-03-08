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

def confirm():
    pass

def list(list_name):
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    if list_name == 'add':
        addlist_len = registrar.getWaitingAdditionCnt()

        if addlist_len == 0:
            print('No KYC registration requests found')
        else:
            addlist = {}
            phones_list = []
            for i in range(addlist_len):
                elem = registrar.addWaitingPhones(i)
                phones_list.append(elem[1])
                addlist[elem[1]] = elem[0]

            phones_list.sort()

            for phone in phones_list:
                addr = addlist[phone]
                print('{}: {}'.format(phone, addr))

    elif list_name == 'del':
        dltlist_len = registrar.getWaitingDeletionCnt()

        if dltlist_len == 0:
            print('No KYC unregistration requests found')
        else:
            dltlist = {}
            phones_list = []
            for i in range(dltlist_len):
                elem = registrar.delWaitingPhones(i)
                phones_list.append(elem[1])
                addlist[elem[1]] = elem[0]

            phones_list.sort()

            for phone in phones_list:
                addr = addlist[phone]
                print('{}: {}'.format(phone, addr))


commands = {
    'get': get,
    'confirm': confirm,
    'list': list
}


# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
