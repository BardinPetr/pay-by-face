#!/usr/bin/env python

### Put your code below this comment ###
import sys
from ethWrapper import ContractWrapper, gas_price, user_priv_key
from tools import parceJson, getAccount
from web3 import Web3, HTTPProvider



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



# === Commands === #
def deploy():
    # TODO: разные байткоды и аби
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, bytecode=registrar_BYTECODE)
    payment = ContractWrapper(w3=web3, abi=ABI, bytecode=BYTECODE)

    registrar_rcpt = contract.constructor()
    payment_rcpt = payment.constructor()

    with open('registrar.json', 'w') as f:
        dump({
            'registrar': {'address': registrar_rcpt['contractAddress'], 'startBlock': registrar_rcpt['blockNumber']}
            'payment': {'address': payment_rcpt['contractAddress'], 'startBlock': payment_rcpt['blockNumber']}

    print('KYC Registrar: ' + registrar_rcpt['contractAddress'])
    print('Payment Handler: ' + registrar_rcpt['blockNumber'])


commands = {
    'deploy': deploy
}



# === Entry point === # 
if name == '__main__':
    comands(sys.args[1])(*sys.args[1:])