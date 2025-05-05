from web3 import Web3
import json
from data import data
from config import rpc, private_key, my_contract_address, usdc_address, eth_faddress
import traceback


class sendUSDC:

    def __init__(self):
        try: 
            self.w3 =  Web3(provider = Web3.HTTPProvider(endpoint_uri = rpc))
            print(f'web3 connection: {self.w3.is_connected()}')
        except Exception as err:
            print(f'w3: {err}')
            
        self.account = self.w3.eth.account.from_key(private_key=private_key)
        self.dates = data()
        self.min_to_amount = float(self.dates.usdc_price) * self.dates.usdc_amount * (1 - self.dates.slippage / 100)
        self.usdc_decimals = self.usdc_contract().functions.decimals().call()
        self.usdc_amount = int(self.dates.usdc_amount * 10 ** self.dates.usdc_decimals)
        self.eth_amount = int(self.min_to_amount * 10 ** self.usdc_decimals)

    def woofi_contract(self):
        try:
            woofi_contract_address = Web3.to_checksum_address(my_contract_address)
            with open(self.dates.file_path_woofi, 'r') as f:
                woofi_contract_abi = json.load(f)
            m_contract = self.w3.eth.contract(address=woofi_contract_address, abi=woofi_contract_abi)    
            print(f'woofi contract is work!')
            return m_contract
        except Exception as err:
            traceback.print_exc()
            return print(f"meta contract: {err}")

    def usdc_contract(self):
        try:
            usdc_contract_address = Web3.to_checksum_address(usdc_address)
            with open(self.dates.file_path_usdc, 'r') as f:
                usdc_contract_abi = json.load(f) 
            usdc_c = self.w3.eth.contract(address=usdc_contract_address, abi=usdc_contract_abi)
            print(f'usdc contract is work!')
            return usdc_c
        except Exception as err:
            raise err(f"{usdc_contract_address} Don't opened file {err}" )

    def tx_args(self, tx_type):
        mcontract = self.woofi_contract()
        ucontract = self.usdc_contract()
        try:
            if tx_type == 'approve':
                data_tx = ucontract.encode_abi(
                    'approve',
                    args = (
                        Web3.to_checksum_address(my_contract_address),
                        self.usdc_amount
                )
                )
                to = ucontract.address

            elif tx_type == 'swap':
                data_tx = mcontract.encode_abi(
                    'swap',
                    args = (
                        self.dates.usdc_address,
                        Web3.to_checksum_address(eth_faddress),
                        self.usdc_amount,
                        self.eth_amount,
                        self.account.address,
                        self.account.address
                    )
                )    
                to = mcontract.address

            print(f'tx_args is work!')
            return data_tx, to
        except Exception as err:
            traceback.print_exc()
            print(f'tx_args: {err}')
    
    def tx_params(self, tx_type):
       try:
        data_tx, to = self.tx_args(tx_type=tx_type)
        if data_tx is None:
            raise ValueError('tx_args: error')
        
        tx_parametrs = {
            'chainId': self.w3.eth.chain_id,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'from': self.account.address,
            'to': to,
            'data': data_tx,
            
            }
        
        tx_parametrs['gas'] = self.w3.eth.estimate_gas(tx_parametrs)
        print(f'tx_params is work!: {tx_parametrs["gas"]}')
        return tx_parametrs
       except Exception as err:
           traceback.print_exc()
           print(f'tx_params: {err}')
           return None

    def sign(self, tx_type):
        try:
            tx = self.tx_params(tx_type=tx_type)
            if not tx:
                print('sign error: no tx')
                return None
            sign = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(sign.raw_transaction)
            
            if sign:
                print(f'sign: success!')

            return tx_hash, self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)

        except Exception as err:
            traceback.print_exc()
            print('sign: ', err)
            return None
            
    def wait_trans_send(self):
        try:
            tx_hash_a, ap_receipt = self.sign('approve')
            if ap_receipt and ap_receipt.status == 1:
                print(f'transaction was successful: {tx_hash_a.hex()}, waiting swapp...')
                tx_hash_s, swap_receipt = self.sign('swap')
                if swap_receipt and swap_receipt.status == 1:
                    print(f'swap success {tx_hash_s.hex()}')

            else:
                print(f'transaction failed {tx_hash_s["transactionHash"].hex()}')
        except Exception as err:
            traceback.print_exc()
            return print(f"wait_trans error: {err}")
        
    def main(self):
        return self.wait_trans_send()

