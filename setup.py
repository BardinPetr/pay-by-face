#!/usr/bin/env python

### Put your code below this comment ###
import sys
from requests import get as getData
from ethWrapper import ContractWrapper
import ethWrapper
from tools import parceJson, toAddress
from web3 import Web3, HTTPProvider
from json import dump



# === Init === #
network = parceJson('network.json')

try:
    ethWrapper.gas_price = int(getData(network['gasPriceUrl']).json()['fast'] * 1000000000)
except:
    ethWrapper.gas_price = int(network['defaultGasPrice'])

web3 = Web3(HTTPProvider(network['rpcUrl']))
ethWrapper.user_priv_key = network['privKey']
web3.eth.defaultAccount = toAddress(network['privKey'])


# TODO:  payment
registrar_ABI = parceJson('contracts/registrar/ABI.json')
registrar_BYTECODE = parceJson('contracts/registrar/bytecode.json')['object']

payment_ABI = parceJson('contracts/payment/ABI.json')
payment_BYTECODE = parceJson('contracts/payment/bytecode.json')['object']



# === Commands === #
def deploy():
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, bytecode=registrar_BYTECODE)
    payment = ContractWrapper(w3=web3, abi=payment_ABI, bytecode=payment_BYTECODE)

    registrar_rcpt = registrar.constructor()
    payment_rcpt = payment.constructor()

    with open('registrar.json', 'w') as f:
        dump({
            'registrar': { 'address': registrar_rcpt['contractAddress'], 'startBlock': registrar_rcpt['blockNumber'] },
            'payments': { 'address': payment_rcpt['contractAddress'], 'startBlock': payment_rcpt['blockNumber'] }
        }, f)

    print('KYC Registrar: ' + registrar_rcpt['contractAddress'])
    print('Payment Handler: ' + payment_rcpt['contractAddress'])

def owner(contract_name):
    data = parceJson('registrar.json')
    if contract_name == 'registrar':
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=data['registrar']['address'])

    print('Admin account: ' + contract.owner())



commands = {
    'deploy': deploy,
    'owner': owner
}



# === Entry point === #
if __name__ == '__main__':
    commands[sys.argv[1][2:]](*sys.argv[2:])
