from web3 import Web3
import requests
from config import usdc_address

class data :

    def __init__(self):
        self.response = requests.get('https://api.binance.com/api/v3/depth?symbol=USDCUSDT&limit=1')
        self.result = self.response.json()
        self.usdc_address = Web3.to_checksum_address(usdc_address)
        self.usdc_price = self.result['asks'][0][0]
        self.usdc_amount = 0.1 
        self.usdc_decimals = 18
        self.slippage = 0.5
        self.file_path_usdc = 'usdc_abi.json'
        self.file_path_woofi = 'Woofi.json'