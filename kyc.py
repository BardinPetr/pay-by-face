#!/usr/bin/env python

### Put your code below this comment ###
import sys
from ethWrapper import ContractWrapper
from network import *


# === Commands === #
from tools import get_private_key


def get(phone_number):
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    res = registrar.get(phone_number)
    if res != '0x0000000000000000000000000000000000000000':
        print('Registered correspondence: ' + res)
    else:
        print('Correspondence not found')


def confirm(addr):
    try:
        _datafile = parceJson('network.json')
        ethWrapper.user_priv_key = _datafile['privKey']
        web3.eth.defaultAccount = toAddress(_datafile['privKey'])
    except TypeError:
        print("ID is not found")
        return

    data = None
    try:
        data = parceJson('registrar.json')
        _ = data['registrar']
    except:
        print("No contract address")
        return

    contract, mode = None, 0
    try:
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])
        mode = contract.getByAddr(addr) == ""
    except Exception:
        print("Seems that the contract address is not the registrar contract.")
        return

    try:
        res = contract.approve(addr)
        if not res[0]['status']:
            print("Failed but included in", res[0]['transactionHash'].hex())
        else:
            print("Confirmed by", res[0]['transactionHash'].hex())
    except Exception:
        print("No funds to send the request")
        return


def list(list_name):
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    if list_name == 'add':
        addlist_len = registrar.getWaitingAdditionCnt()

        if addlist_len == 0:
            print('No KYC registration requests found')
        else:
            phones_list = []
            for i in range(addlist_len):
                elem = registrar.addWaitingPhones(i)
                phones_list.append(elem)

            phones_list.sort(key=lambda x: (x[1], x[0]))

            for addr, phone, _ in phones_list:
                print('{}: {}'.format(addr, phone))

    elif list_name == 'del':
        dltlist_len = registrar.getWaitingDeletionCnt()

        if dltlist_len == 0:
            print('No KYC unregistration requests found')
        else:
            phones_list = []
            for i in range(dltlist_len):
                elem = registrar.delWaitingPhones(i)
                phones_list.append(elem)

            phones_list.sort(key=lambda x: (x[1], x[0]))

            for addr, phone, _ in phones_list:
                print('{}: {}'.format(addr, phone))


commands = {
    'get': get,
    'confirm': confirm,
    'list': list
}

# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
