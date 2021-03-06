from time import sleep

gas_price = None
user_priv_key = None


class ContractWrapper:
    def __init__(self, w3=None, **kwargs):
        """
        с w3.eth.defaultAccount будут отправляться транзакции.

        Методы автоматически определяются как call или buildTransaction
        > методы определенные как call возвращают результат функции
        > методы определенные как bT возвращают рецепт отправленной транзакции

        Args:
            w3 (Web3): экземпляр web3 для общения с блокчеином.
            **kwargs (type): парамтры как для eth.contract().
        """

        contract = w3.eth.contract(**kwargs)

        # setup events
        self.events = contract.events

        # setup constructor
        def construct(*args, **kwargs):
            tx_receipt = None

            tx = contract.constructor(*args, **kwargs).buildTransaction({
                'gasPrice': gas_price,
                'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount)
            })

            signed = w3.eth.account.signTransaction(tx, private_key=user_priv_key)
            tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            return tx_receipt

        setattr(self, 'constructor', construct)

        # setup contract methods
        for elem in kwargs['abi']:
            if 'name' in elem:
                try:
                    # choose call or buildTransaction
                    if elem['stateMutability'] == 'view':
                        def funct(name):
                            def func(*args, **kwargs):
                                return getattr(contract.functions, name)(*args, **kwargs).call()

                            return func
                    elif elem['stateMutability'] == 'nonpayable' or \
                            elem['stateMutability'] == 'pure' or \
                            elem['stateMutability'] == 'payable':
                        def funct(name):
                            def func(*args, **kwargs):
                                tx_receipt = None
                                value = 0 if 'value' not in kwargs.keys() else kwargs.pop('value')
                                data = contract.encodeABI(fn_name=name, args=args, kwargs=kwargs)

                                tx = {
                                    'to': contract.address,
                                    'value': value,
                                    'gas': 1000000,
                                    'gasPrice': gas_price,
                                    'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
                                    'data': data
                                }

                                signed = w3.eth.account.signTransaction(tx, private_key=user_priv_key)

                                tx_receipt = None
                                for i in range(15):
                                    try:
                                        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
                                        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                                        break
                                    except Exception as ex:
                                        if str(ex).find('Insufficient funds') != -1:
                                            return -666
                                        sleep(6)
                                        if i == 15:
                                            print(ex)

                                return tx_receipt

                            return func
                    setattr(self, elem['name'], funct(elem['name']))
                except:
                    pass
