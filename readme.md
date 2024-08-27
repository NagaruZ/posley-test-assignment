# Posley Test Project

## Introduction
This is an simple API server having two endpoints:
- An endpoint returns a wallet's balances of USDC, USDT and ETH
- An endpoint summarises a wallet's total transfer volume of USDC, USDT, and ETH in past 24 hours 

## Installation
1. Clone this repo
```bash
git clone https://github.com/NagaruZ/posley-test-assignment.git
cd posley-test-assignment
```

2. Rename `config.json.example` to `config.json`, then edit the value of `api_key` and `web3_provider_url` to your Etherscan API key and Web3 provider URL correspondingly

2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python server.py
```

