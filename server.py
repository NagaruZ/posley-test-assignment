from flask import Flask, jsonify
from datetime import datetime, timedelta
from web3 import Web3, EthereumTesterProvider
import requests

app = Flask(__name__)

# Web3 Configuration
WEB3_PROVIDER_URL = 'https://prettiest-green-gadget.quiknode.pro/dc58342758f94b6480bdbc080ada992297797e28' 
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
# web3 = Web3(EthereumTesterProvider())

# Token Contract Information (replace with actual values)
USDC_CONTRACT_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
USDT_CONTRACT_ADDRESS = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
USDC_ABI = [{'constant': False, 'inputs': [{'name': 'newImplementation', 'type': 'address'}], 'name': 'upgradeTo', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'newImplementation', 'type': 'address'}, {'name': 'data', 'type': 'bytes'}], 'name': 'upgradeToAndCall', 'outputs': [], 'payable': True, 'stateMutability': 'payable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'implementation', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'newAdmin', 'type': 'address'}], 'name': 'changeAdmin', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'admin', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'name': '_implementation', 'type': 'address'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'payable': True, 'stateMutability': 'payable', 'type': 'fallback'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'previousAdmin', 'type': 'address'}, {'indexed': False, 'name': 'newAdmin', 'type': 'address'}], 'name': 'AdminChanged', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'implementation', 'type': 'address'}], 'name': 'Upgraded', 'type': 'event'}]
USDT_ABI = [{'constant': True, 'inputs': [], 'name': 'name', 'outputs': [{'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_upgradedAddress', 'type': 'address'}], 'name': 'deprecate', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'approve', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'deprecated', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_evilUser', 'type': 'address'}], 'name': 'addBlackList', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'totalSupply', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_from', 'type': 'address'}, {'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'transferFrom', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'upgradedAddress', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}], 'name': 'balances', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'maximumFee', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': '_totalSupply', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [], 'name': 'unpause', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '_maker', 'type': 'address'}], 'name': 'getBlackListStatus', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}, {'name': '', 'type': 'address'}], 'name': 'allowed', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'paused', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'who', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [], 'name': 'pause', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getOwner', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'owner', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'symbol', 'outputs': [{'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'transfer', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'newBasisPoints', 'type': 'uint256'}, {'name': 'newMaxFee', 'type': 'uint256'}], 'name': 'setParams', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'amount', 'type': 'uint256'}], 'name': 'issue', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'amount', 'type': 'uint256'}], 'name': 'redeem', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}], 'name': 'allowance', 'outputs': [{'name': 'remaining', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'basisPointsRate', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}], 'name': 'isBlackListed', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_clearedUser', 'type': 'address'}], 'name': 'removeBlackList', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'MAX_UINT', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'newOwner', 'type': 'address'}], 'name': 'transferOwnership', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_blackListedUser', 'type': 'address'}], 'name': 'destroyBlackFunds', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'name': '_initialSupply', 'type': 'uint256'}, {'name': '_name', 'type': 'string'}, {'name': '_symbol', 'type': 'string'}, {'name': '_decimals', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'amount', 'type': 'uint256'}], 'name': 'Issue', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'amount', 'type': 'uint256'}], 'name': 'Redeem', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'newAddress', 'type': 'address'}], 'name': 'Deprecate', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'feeBasisPoints', 'type': 'uint256'}, {'indexed': False, 'name': 'maxFee', 'type': 'uint256'}], 'name': 'Params', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': '_blackListedUser', 'type': 'address'}, {'indexed': False, 'name': '_balance', 'type': 'uint256'}], 'name': 'DestroyedBlackFunds', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': '_user', 'type': 'address'}], 'name': 'AddedBlackList', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': '_user', 'type': 'address'}], 'name': 'RemovedBlackList', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'owner', 'type': 'address'}, {'indexed': True, 'name': 'spender', 'type': 'address'}, {'indexed': False, 'name': 'value', 'type': 'uint256'}], 'name': 'Approval', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'from', 'type': 'address'}, {'indexed': True, 'name': 'to', 'type': 'address'}, {'indexed': False, 'name': 'value', 'type': 'uint256'}], 'name': 'Transfer', 'type': 'event'}, {'anonymous': False, 'inputs': [], 'name': 'Pause', 'type': 'event'}, {'anonymous': False, 'inputs': [], 'name': 'Unpause', 'type': 'event'}]
MIN_ABI = [{
        "constant": True,
        "inputs": [
            {
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },]

usdc_contract = web3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=MIN_ABI)
usdt_contract = web3.eth.contract(address=USDT_CONTRACT_ADDRESS, abi=MIN_ABI)

# --- Flask API Endpoints ---

@app.route('/api/v1/wallet/<address>/balances')
def get_wallet_balances(address):
    """Retrieves ETH, USDC, and USDT balances for a given address."""
    try:
        eth_balance_wei = web3.eth.get_balance(address)
        eth_balance_ether = Web3.from_wei(eth_balance_wei, 'ether')
        usdc_balance = str(usdc_contract.functions.balanceOf(address).call() / 10**6)
        usdt_balance = str(usdt_contract.functions.balanceOf(address).call() / 10**6)
        
        return jsonify({
            'address': address,
            'balance': {
                'ETH': eth_balance_ether,
                'USDC': usdc_balance,
                'USDT': usdt_balance 
            },
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
