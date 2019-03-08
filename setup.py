#!/usr/bin/env python

### Put your code below this comment ###
import sys
from ethWrapper import ContractWrapper
from json import dump
from network import *


# === Commands === #
def deploy():
    for i in range(100):
        try:
            registrar = ContractWrapper(w3=web3, abi=registrar_ABI, bytecode=registrar_BYTECODE)
            payment = ContractWrapper(w3=web3, abi=payment_ABI, bytecode=payment_BYTECODE)

            registrar_rcpt = registrar.constructor()
            payment_rcpt = payment.constructor()

            with open('registrar.json', 'w') as f:
                dump({
                    'registrar': {'address': registrar_rcpt['contractAddress'], 'startBlock': registrar_rcpt['blockNumber']},
                    'payments': {'address': payment_rcpt['contractAddress'], 'startBlock': payment_rcpt['blockNumber']}
                    }, f)

            print('KYC Registrar: ' + registrar_rcpt['contractAddress'])
            print('Payment Handler: ' + payment_rcpt['contractAddress'])
            break
        except:
            pass


def owner(contract_name):
    if contract_name == 'registrar':
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    print('Admin account: ' + contract.owner())


def chown(contract_name, addr):
    if contract_name == 'registrar':
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    # проверка на то, что аккаунт сендера является овнером
    if contract.isOwner():
        contract.transferOwnership(Web3.toChecksumAddress(addr))
        print('New admin account: ' + contract.owner())
    else:
        print('Request cannot be executed')


commands = {
    'deploy': deploy,
    'owner': owner,
    'chown': chown
}

# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
