#!/usr/bin/env python

from network import contracts_data, payment_ABI
from ethWrapper import ContractWrapper, gas_price
from sys import argv
import json
from tools import *
import ethWrapper
from requests import get as getData
import re
from time import sleep
from datetime import datetime

### Put your code below this comment ###

web3 = Web3(HTTPProvider(parceJson('network.json')['rpcUrl']))

registrar_ABI = parceJson('contracts/registrar/ABI.json')

api_data = parceJson("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]


def request_balance(args):
    try:
        print("Your balance is " + ' '.join(weighing(
            get_balance_by_priv(web3, get_private_key(parceJson('person.json')['id'], args[0])))))
    except TypeError:
        print("ID is not found")


def send_add_user(args):
    addr, pk = None, None
    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except TypeError:
        print("ID is not found")
        return
    if len(args) > 1 and re.match("^\+\d{11}$", args[1]):
        if contracts_data is None:
            print("No contract address")
            return

        contract = None
        try:
            ethWrapper.user_priv_key = pk
            web3.eth.defaultAccount = addr
            contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])
            if contract.isInAddPending():
                print("Registration request already sent")
                return
            if contract.getByAddr(addr) != "":
                print("Such phone number already registered")
                return
        except:
            print("Seems that the contract address is not the registrar contract")
            return

        try:
            res = contract.add(args[1])
            print("Registration request sent by", res.transactionHash.hex())
        except:
            print("No funds to send the request")
            return
    else:
        print("Incorrect phone number")


def send_del_user(args):
    addr, pk = None, None

    if contracts_data is None:
        print("No contract address")
        return

    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except:
        print("ID is not found")
        return

    contract = None
    try:
        ethWrapper.user_priv_key = pk
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])
        if contract.getByAddr(addr) == "":
            print("Account is not registered yet")
            return
        if contract.isInDelPending():
            print("Unregistration request already sent")
            return
    except:
        print("Seems that the contract address is not the registrar contract")
        return

    try:
        res = contract.dlt()
        print("Unregistration request sent by", res.transactionHash.hex())
    except:
        print("No funds to send the request")


def send_cancel_user(args):
    addr, pk = None, None
    try:
        pk = get_private_key(parceJson('person.json')['id'], args[0])
        addr = toAddress(pk)
    except:
        print("ID is not found")
        return

    if contracts_data is None:
        print("No contract address")
        return

    contract, mode = None, -1
    try:
        ethWrapper.user_priv_key = pk
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])
        mode = contract.isInAddPending()
        if not mode and not contract.isInDelPending():
            print("No requests found")
            return
    except:
        print("Seems that the contract address is not the registrar contract")
        return

    try:
        res = contract.cancel()
        print(("R" if mode else "Unr") +
              "egistration canceled by", res.transactionHash.hex())
    except:
        print("No funds to send the request")


def send(a):
    pin = a[0]
    phone = a[1]
    val = int(a[2])

    if not re.match("^\+\d{11}$", phone):
        print("Incorrect phone number")
        return

    try:
        priv_key = get_private_key(parceJson('person.json')['id'], pin)
        addr = toAddress(priv_key)
    except:
        print("ID is not found")
        return

    if contracts_data is None:
        print("No contract address")
        return

    ethWrapper.user_priv_key = priv_key
    web3.eth.defaultAccount = addr
    registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=contracts_data['registrar']['address'])

    sendto_addr = registrar.get(phone)

    if sendto_addr != '0x0000000000000000000000000000000000000000':
        try:
            registrar.sending_point(val, phone, registrar.getByAddr(addr))

            transaction = {
                'from': addr,
                'to': sendto_addr,
                'value': val,
                'gas': 24000,
                'gasPrice': gas_price,
                'nonce': web3.eth.getTransactionCount(web3.eth.defaultAccount)
            }

            signed = web3.eth.account.signTransaction(transaction, priv_key)
            tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)

            tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

            val, tp = weighing(val)

            print('Payment of {} {} to {} scheduled'.format(val, tp, phone))
            print('Transaction Hash: ' + web3.toHex(tx_hash))

        except Exception as e:
            if str(e) == 'Low balance':
                print('No funds to send the payment')
            else:
                print(e)
                return
    else:
        print('No account with the phone number: ' + phone)


def gift(a):
    pin = a[0]
    value = int(a[1])
    exp_date = datetime.strptime(a[2], "%H:%M %d.%m.%Y")

    try:
        priv_key = get_private_key(parceJson('person.json')['id'], pin)
        addr = toAddress(priv_key)
    except:
        print("ID is not found")
        return

    if contracts_data is None:
        print("No contract address")
        return

    contract, mode = None, -1
    try:
        ethWrapper.user_priv_key = priv_key
        web3.eth.defaultAccount = addr
        contract = ContractWrapper(w3=web3, abi=payment_ABI, address=contracts_data['payments']['address'])
        if datetime.now() > exp_date:
            print("Expiration date is invalid")
            return
        if get_balance(web3, addr) < value:
            print("No funds to create a certificate")
            return
    except:
        print("Seems that the contract address is not the certificates contract")
        return

    try:
        tx_receipt = contract.create(int(exp_date.timestamp()), value=value)
        res = contract.events.CertificateCreated().processReceipt(tx_receipt)
        h = res[0].args.id.hex()
        signed_message = web3.eth.account.signHash(h, private_key=priv_key)
        print(signed_message.signature)
    except Exception as ex:
        print(ex)
        print("No funds to create a certificate")


def idetify_person(video):
    simple = not os.path.exists("actions.json")
    faces = create_frames_simple(video)
    if faces:
        if exist_group():
            res = check_all_right(cf.person_group.get, g_id)
            if res.setdefault("userData") == "trained":
                if simple:
                    candidate = get_predict(faces)
                    if candidate:
                        print(candidate, "identified")
                        with open('person.json', 'w') as outfile:
                            json.dump({"id": candidate}, outfile)
                    else:
                        print("The person was not found")
                    clear(5)
                else:
                    pass
            else:
                print("The service is not ready")
                if os.path.exists("person.json"):
                    os.remove("person.json")
        else:
            print("The service is not ready")
    else:
        print("The video does not follow requirements")


def ops(a):
    pvk, my_addr = None, None
    try:
        pvk = get_private_key(parceJson('person.json')['id'], a[0])
        my_addr = toAddress(pvk)
    except:
        print("ID is not found")
        return

    try:
        regstr = parceJson('registrar.json')['registrar']
    except:
        print('No contract address')
    else:
        response = getData('https://blockscout.com/poa/sokol/api', params={
            'module': 'account',
            'action': 'txlist',
            'address': regstr['address'],
            'startblock': regstr['startBlock']}).json()['result']

        contract_decoder = web3.eth.contract(abi=registrar_ABI, address=regstr['address'])
        registrar = ContractWrapper(w3=web3, abi=registrar_ABI, address=regstr['address'])

        history = []
        for tx in response:
            # addr_from = web3.toChecksumAddress(tx['from'])
            try:
                my_phone = registrar.getByAddr(my_addr)
            except:
                print('Seems that the contract address is not the certificates contract.')
                return

            func_name = ''
            try:
                decoded_inp = contract_decoder.decode_function_input(tx['input'])
                func_name = type(decoded_inp[0]).__name__
            except:
                pass
            else:
                if func_name == 'sending_point':
                    func_args = decoded_inp[1]

                    send_type = ''
                    phone = ''
                    if func_args['from_phone'] == my_phone:
                        phone = func_args['to_phone']
                        send_type = 'TO:'

                    elif func_args['to_phone'] == my_phone:
                        phone = func_args['from_phone']
                        send_type = 'FROM:'

                    val, tp = weighing(func_args['val'])
                    timing = datetime.utcfromtimestamp(int(tx['timeStamp'])).strftime('%H:%M:%S %d.%m.%Y')
                    history.append('{} {} {} {} {}'.format(timing, send_type, phone, val, tp))

    if len(history) == 0:
        print('No operations found')
    else:
        print('Operations:')
        for i in history:
            print(i)


commands = {
    'balance': request_balance,
    'add': send_add_user,
    'del': send_del_user,
    'cancel': send_cancel_user,
    'send': send,
    'find': idetify_person,
    'ops': ops,
    'gift': gift,
    # 'receive': receive_gift
}
# === Entry point === #
if __name__ == '__main__':
    try:
        commands[argv[1][2:]](argv[2:])
    except IndexError:
        pass
