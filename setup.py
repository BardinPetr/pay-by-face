#!/usr/bin/env python

### Put your code below this comment ###
import sys
from requests import get as getData
from ethWrapper import ContractWrapper, gas_price, user_priv_key
from tools import parceJson, toAddress
from web3 import Web3, HTTPProvider
from json import dump



# === Init === #
network = parceJson('network.json')

try:
    gas_price = int(getData(network['gasPriceUrl']).json()['fast'] * 1000000000)
except:
    gas_price = int(network['defaultGasPrice'])

web3 = Web3(HTTPProvider(network['rpcUrl']))
user_priv_key = network['privKey']
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

    registrar_rcpt = contract.constructor()
    payment_rcpt = payment.constructor()

    with open('registrar.json', 'w') as f:
        dump({
            'registrar': { 'address': registrar_rcpt['contractAddress'], 'startBlock': registrar_rcpt['blockNumber'] },
            'payments': { 'address': payment_rcpt['contractAddress'], 'startBlock': payment_rcpt['blockNumber'] }
        })

    print('KYC Registrar: ' + registrar_rcpt['contractAddress'])
    print('Payment Handler: ' + payment_rcpt['contractAddress'])


commands = {
    'deploy': deploy
}



# === Entry point === # 
if __name__ == '__main__':
    commands[sys.argv[1]](*sys.argv[1:])