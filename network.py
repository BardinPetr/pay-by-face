from requests import get as getData
import ethWrapper
from tools import parceJson, toAddress
from web3 import Web3, HTTPProvider
import os

# === Init === #
_datafile = parceJson('network.json')

try:
    ethWrapper.gas_price = int(getData(_datafile['gasPriceUrl']).json()['fast'] * 1000000000)
except:
    ethWrapper.gas_price = int(_datafile['defaultGasPrice'])

web3 = Web3(HTTPProvider(_datafile['rpcUrl']))
ethWrapper.user_priv_key = _datafile['privKey']
web3.eth.defaultAccount = toAddress(_datafile['privKey'])

registrar_ABI = parceJson('contracts/registrar/ABI.json')
registrar_BYTECODE = parceJson('contracts/registrar/bytecode.json')['object']

payment_ABI = parceJson('contracts/payment/ABI.json')
payment_BYTECODE = parceJson('contracts/payment/bytecode.json')['object']

contracts_data = None
try:
    contracts_data = parceJson('registrar.json')
except:
    pass
