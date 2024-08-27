from flask import Flask, jsonify
from web3 import Web3
import requests
import datetime
import traceback
import asyncio
from hexbytes import HexBytes
from collections import deque
import time
import decimal
import json

app = Flask(__name__)

# Read API Key and web provider URL from config file
with open('config.json') as f:
    config = json.load(f)

ETHERSCAN_API_KEY = config['api_key']
WEB3_PROVIDER_URL = config['web3_provider_url']

web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# Token Contract Information
USDC_CONTRACT_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
USDT_CONTRACT_ADDRESS = '0xdAC17F958D2ee523a2206206994597C13D831ec7'

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
    }, {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },]

usdc_contract = web3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=MIN_ABI)
usdt_contract = web3.eth.contract(address=USDT_CONTRACT_ADDRESS, abi=MIN_ABI)

def round_up_to_6_digits(number):
    """
    Rounds a number up to 6 digits after the decimal point.
    """
    return decimal.Decimal(number).quantize(decimal.Decimal('1E-6'), rounding=decimal.ROUND_HALF_UP)

async def rate_limited_queue(queue, max_requests_per_second=5):
    """
    A rate-limited queue that ensures a maximum number of requests per second.

    Args:
        queue: The queue to process.
        max_requests_per_second: The maximum number of requests allowed per second.

    Yields:
        Items from the queue, respecting the rate limit.
    """
    last_request_time = time.monotonic()
    while True:
        if queue:
            # Check if we've exceeded the rate limit
            if time.monotonic() - last_request_time < 1 / max_requests_per_second:
                await asyncio.sleep(1 / max_requests_per_second - (time.monotonic() - last_request_time))

            item = queue.popleft()
            last_request_time = time.monotonic()
            yield item
        else:
            await asyncio.sleep(0.1)  # Wait briefly if the queue is empty

async def _get_eth_transfers(wallet, start_block, end_block):
    """
    Fetches ETH transfers from/to a given wallet address.
    We will iterate through the chain from start_block to end_block
    to collect transaction info.

    Deprecated because iterating the chain by ourselves is extremly slow.
    """
    transfers = []
    transactions = []
    try:
        request_queue = deque()

        for block_number in range(start_block, end_block + 1):
            print(block_number)
            block = web3.eth.get_block(block_number)
            transaction_hashes = block['transactions']
        
            for tx_hash in transaction_hashes:
                request_queue.append(tx_hash)

        # Use a rate limited queue to meet the API rate limit of 40/sec
        async for tx_hash in rate_limited_queue(request_queue, max_requests_per_second=40):
            transaction = web3.eth.get_transaction(tx_hash)
            transactions.append(transaction)

        for tx in transactions:
            if tx['to'] == wallet or tx['from'] == wallet:
                transfers.append({
                    'amount': web3.fromWei(tx['value'], 'ether'),
                    'timestamp': datetime.fromtimestamp(block['timestamp'])
                })

        return transfers

    except Exception as e:
        raise e

def get_eth_transfers(wallet, start_block, end_block):
    """
    Fetches ETH transfers from/to a given wallet address.
    A warpper of Etherscan API.
    """
    try:
        etherscan_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&startblock={start_block}&endblock={end_block}&page=1&offset=10&sort=asc&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(etherscan_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        transactions = response.json()['result']
        return transactions

    # Let the outer function handle the exception
    except Exception as e:
        raise e

# --- Helper Functions ---
def get_token_transfers(contract_address, wallet, start_block, end_block):
    """
    Fetches transfer events for a given token contract and wallet address,
    considering both incoming and outgoing transfers.
    """
    contract = web3.eth.contract(address=contract_address, abi=MIN_ABI)
    
    outgoing = contract.events.Transfer.create_filter(
        from_block=start_block,
        to_block=end_block,
        argument_filters={'from': wallet}
    ).get_all_entries()

    incoming = contract.events.Transfer.create_filter(
        from_block=start_block,
        to_block=end_block,
        argument_filters={'to': wallet}
    ).get_all_entries()

    result = outgoing + incoming
    return result

def calculate_total_volume(wallet, start_block, end_block):
    """
    Calculates the total transfer volume for USDC, USDT, and ETH in the given block window.

    Here we are calculating the Gross Transfer Volume, which measures the total amount of
    tokens moved through the wallet, regardless of whether it's sending or receiving.
    """
    # Fetch transfer events for USDC, USDT, and ETH
    usdc_transfers = get_token_transfers(USDC_CONTRACT_ADDRESS, wallet, start_block, end_block)
    usdt_transfers = get_token_transfers(USDT_CONTRACT_ADDRESS, wallet, start_block, end_block)
    eth_transfers = get_eth_transfers(wallet, start_block, end_block)

    print(usdc_transfers, usdt_transfers)

    # Calculate total volume for each token
    total_usdc = sum([transfer['args']['value'] / 1e6 for transfer in usdc_transfers])
    total_usdt = sum([transfer['args']['value'] / 1e6 for transfer in usdt_transfers])
    total_eth = sum([int(transfer['value']) for transfer in eth_transfers])

    # Convert Wei to ether, round up the result
    total_usdc = str(round_up_to_6_digits(total_usdc))
    total_usdt = str(round_up_to_6_digits(total_usdt))
    total_eth = str(round_up_to_6_digits(Web3.from_wei(total_eth, 'ether')))

    return {
        'USDC': total_usdc,
        'USDT': total_usdt,
        'ETH': total_eth
    }

# --- Flask API Endpoints ---

@app.route('/api/v1/wallet/<address>/balances')
def get_wallet_balances(address):
    """
    Retrieves ETH, USDC, and USDT balances for a given address.
    """
    try:
        eth_balance_wei = web3.eth.get_balance(address)
        eth_balance_ether = str(round_up_to_6_digits(Web3.from_wei(eth_balance_wei, 'ether')))
        usdc_balance = str(round_up_to_6_digits(usdc_contract.functions.balanceOf(address).call() / 1e6))
        usdt_balance = str(round_up_to_6_digits(usdt_contract.functions.balanceOf(address).call() / 1e6))
        
        result = {
            'ETH': eth_balance_ether,
            'USDC': usdc_balance,
            'USDT': usdt_balance 
        }

        return jsonify(result)

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/wallet/<address>/volumes')
async def get_wallet_volumes(address):
    """
    Calculates the 24-hour transfer volume for a given address.
    """
    try:
        now = datetime.datetime.now(datetime.UTC)
        twenty_four_hours_ago = now - datetime.timedelta(hours=24)

        # Get start block number by timestamp, using Etherscan API
        etherscan_url = f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={int(twenty_four_hours_ago.timestamp())}&closest=before&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(etherscan_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        start_block = int(response.json()['result'])
        end_block = web3.eth.block_number

        result = calculate_total_volume(address, start_block, end_block)

        return jsonify(result)
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

async def main():
    app.run(debug=True, host="0.0.0.0")

if __name__ == '__main__':
    asyncio.run(main())
