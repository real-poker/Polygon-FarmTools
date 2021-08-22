# -*- coding: utf-8 -*-

import json
import matplotlib.pyplot as plt

def getBlocknum(transaction_list):
    return [int(x['blockNumber']) for x in transaction_list]
        
def getTime(transaction_list):
    return [int(x['timeStamp']) for x in transaction_list]
    
def getBalance(transaction_list, pooladdress):
    total = 0
    balance = []
    decimal = int(transaction_list[0]['tokenDecimal'])
    
    for entry in transaction_list:
        if entry['from'] == pooladdress:
            total -= int(entry['value'])/(10**decimal)
        else:
            total += int(entry['value'])/(10**decimal)
        balance.append(total)
    return balance


pooladdress = '0xb5f383998d4e58c140c15c441c75bb79170b6b45'
    
with open('transactions.json', 'r') as f:
    results = json.loads(f.read())
    
time = [float(x)/(60*60)-452250 for x in getTime(results['USDC'])] 

results.pop('last_block')
for count, token in enumerate(results):
    print(token)
    time = [float(x)/(60*60)-452250 for x in getTime(results[token])]
    plt.figure(count)
    plt.plot(time, getBalance(results[token], pooladdress))
    plt.xlabel('Hours')
    plt.ylabel(token)