# -*- coding: utf-8 -*-

import requests
import time
import json
import os

def currentblock(akey):
    # pulls current block number from API
    try:
        response = requests.get('https://api.polygonscan.com/api?module=proxy&action=eth_blockNumber&apikey=' + akey)
        data = int(response.json()['result'][2:], 16)
    except Exception:
        print("Error in accessing API for current block number.")
        return 0
    return data
     
def startblock(address, akey):
    # pulls block number of the first transaction at an address from API
    try:
        response = requests.get("https://api.polygonscan.com/api?module=account&action=tokentx&address=" + address + "&startblock=0&endblock=999999999999&sort=asc&apikey=" + akey)
    except Exception:
        print("Error in accessing API. Link may be out of date.")
        return 0
    else:
        if response.status_code != 200:
            print("API returned bad status " + str(response.status_code))
            return 0
        try:
            data = int(response.json()['result'][0]['blockNumber'])
        except Exception:
            print('API response empty. Please retry.')
            return 0
    return data
        
def scanaddress(address, akey):
    # scans address and compiles dictionary of all tokens/token contracts interacted with
    block_inc = 3000
    api_max = 10000
    token_symbols, contract_addresses = set(), set()
    
    block = startblock(address, akey)   
    end_block = currentblock(akey)    
    
    while block < end_block:
        response = requests.get("https://api.polygonscan.com/api?module=account&action=tokentx&address=" + address + "&startblock=" + str(block) + "&endblock=" + str(block+block_inc-1) + "&sort=asc&apikey=" + akey)
        if response.status_code != 200:
            print('API returned bad status ' + str(response.status_code) + 'during reading loop.')
            return
        elif len(response.json()['result']) >= api_max:
            block_inc = int(block_inc/2)
            continue
        for transaction in response.json()['result']:
            token_symbols.add(transaction['tokenSymbol'])
            contract_addresses.add(transaction['contractAddress'])
        block += block_inc
    return {x:y for x,y in zip(token_symbols, contract_addresses)}
      
def main():
    api_key = 'ACXH82BAMGXAWA4FAD8SCHZKAWVCAG1TJH'
    pooladdress = '0xb5f383998d4e58c140c15c441c75bb79170b6b45'
    block_inc = 3000
    api_max = 10000
    
    end_block = currentblock(api_key)
    time.sleep(0.5) 
    end_block = currentblock(api_key)
    
    if os.path.isfile('tokendict.json'):
        with open('tokendict.json', 'r') as f:
            token_contract = json.loads(f.read())
    else:
        token_contract = scanaddress(pooladdress, api_key)
        with open('tokendict.json', 'w') as f:
            json.dump(token_contract, f)
    
    if os.path.isfile('transactions.json'):
        with open('transactions.json', 'r') as f:
            results = json.loads(f.read())
        block = int(results['last_block'])
    else:
        block = startblock(pooladdress, api_key)
        results = {x:[] for x in token_contract}
        results['last_block'] = block
    
    if os.path.isfile('addresses.json'):
        with open('addresses.json','r') as f:
            addresses = set(json.loads(f.read()))
    else:
        addresses = set()
        
    count = 0    
    while block < end_block:
        response = requests.get("https://api.polygonscan.com/api?module=account&action=tokentx&address=" + pooladdress + "&startblock=" + str(block) + "&endblock=" + str(block+block_inc-1) + "&sort=asc&apikey=" + api_key)
        if response.status_code != 200:
            print('API returned bad status ' + str(response.status_code) + 'during reading loop.')
            break
        elif len(response.json()['result']) >= api_max:
            block_inc = int(block_inc/2)
            continue
        
        for transaction in response.json()['result']:
            [transaction.pop(x) for x in ['hash','nonce','blockHash','tokenName','transactionIndex','gas','gasPrice','gasUsed','cumulativeGasUsed','input','confirmations']]
            results[transaction['tokenSymbol']].append(transaction)
            results['last_block'] = transaction['blockNumber']
            [addresses.add(x) for x in [transaction['to'], transaction['from']]]
            count += 1
               
        print('Reading block ' + str(block) + ' of ' + str(end_block))
        block += block_inc  
        time.sleep(0.2)    
    
    print('Updated ' + str(count) + ' transaction entries')
    with open('transactions.json', 'w') as f:
        json.dump(results, f)
    
    with open('addresses.json','w') as f:
        json.dump(list(addresses), f)
        
if __name__ == '__main__':
    main()