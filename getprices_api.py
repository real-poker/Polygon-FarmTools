# -*- coding: utf-8 -*-

import requests
import time
import json
import os

if os.path.isfile('tokendict.json'):
    with open('tokendict.json', 'r') as f:
        token_contract = json.loads(f.read())

token_ids = []
for token in token_contract:
    response = requests.get('https://api.coingecko.com/api/v3/coins/polygon-pos/contract/' + token_contract[token])
    token_ids.append(response.json()['id'])
    
prices = {x:[] for x in token_contract}
        
response = requests.get('https://api.coingecko.com/api/v3/coins/ball-token/history?date=12-08-2021&localization=false')
response.json()['market_data']['current_price']['usd']