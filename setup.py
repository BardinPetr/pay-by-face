#!/usr/bin/env python

### Put your code below this comment ###
import sys
from ethWrapper import ContractWrapper



# === Init === #


try:
    GAS_PRICE = int(getData('https://gasprice.poa.network').json()['fast'] * 1000000000)
except:
    GAS_PRICE = 0



# === Commands === #

def deploy():
    pass    


commands = {
    'deploy': deploy
}



# === Entry point === # 
if name == '__main__':
    comands(sys.args[1])(*sys.args[1:])