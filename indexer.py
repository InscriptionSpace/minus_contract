import sys
import time
import json

import web3
import requests

PROVIDER_HOST = 'http://127.0.0.1:8545'
CHAIN_NAME = 'hardhat'

ETH_BRIDGE_CONTRACT = '0x5FbDB2315678afecb367f032d93F642f64180aa3'
ETH_BRIDGE_CONTRACT_ABI = '''[
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_committee",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "address",
          "name": "addr",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "LockEvent",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "address",
          "name": "addr",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "bytes32",
          "name": "txhash",
          "type": "bytes32"
        }
      ],
      "name": "ReleaseEvent",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "new_committee",
          "type": "address"
        }
      ],
      "name": "change_committee",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "new_operator",
          "type": "address"
        }
      ],
      "name": "change_operator",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "committee",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "live",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "lock",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "operator",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address payable",
          "name": "recipient",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        },
        {
          "internalType": "bytes32",
          "name": "txhash",
          "type": "bytes32"
        }
      ],
      "name": "release",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "shutdown",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]'''

#w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/31e7bd03dc644095ab751f082b17b395'))
w3 = web3.Web3(web3.Web3.HTTPProvider(PROVIDER_HOST))
contract = w3.eth.contract(address=ETH_BRIDGE_CONTRACT, abi=ETH_BRIDGE_CONTRACT_ABI)

f = contract.events.LockEvent.createFilter(fromBlock='0x0')
c = 0
for i in w3.eth.get_logs(f.filter_params):
    # print('  event', i)
    tx_hash = i['transactionHash'].hex()
    # tx = w3.eth.get_transaction(tx_hash)
    # # if tx['from'] == ETH_BRIDGE_CONTRACT or tx['to'] == ETH_BRIDGE_CONTRACT:
    # print('  tx', tx)

    # func, func_args = contract.decode_function_input(tx['input'])
    # print('  tx input', func_args)
    # print('')

    # block_hash = tx['blockHash'].hex()
    # block_number = tx['blockNumber']
    # sender = tx['from']
    # receiver = tx['to']

    receipt = w3.eth.get_transaction_receipt(tx_hash)
    # if receipt['from'] == ETH_BRIDGE_CONTRACT or receipt['to'] == ETH_BRIDGE_CONTRACT:
    # print('  receipt', receipt)
    receipt_args, = contract.events.LockEvent().processReceipt(receipt)
    # print('  receipt_args', receipt_args)
    addr = receipt_args['args']['addr']
    value = str(receipt_args['args']['value'])
    print('  receipt_args', addr, value)

    print('')
    c+=1

print(c)
# print(state.state)

block_filter = w3.eth.filter('latest')
# bridge_filter = contract.events.LockEvent.createFilter(fromBlock='latest')

while True:
    for block_hash in block_filter.get_new_entries():
        block = w3.eth.get_block(block_hash)
        blk = {'txs': [], 'block_number': block['number'], 'block_hash': block['hash'].hex(), 'chain': CHAIN_NAME}
        print('block', block.hash.hex())
        # print('block', block)
        for tx_hash in block['transactions']:
            tx = w3.eth.get_transaction(tx_hash)
            # print('  tx', tx)
            print('  tx', tx['from'], w3.toBytes(hexstr=tx['input']))
            try:
                info = {'sender': tx['from'], 'tx_hash': tx_hash.hex()}
                arg = json.loads(w3.toBytes(hexstr=tx['input']))
                blk['txs'].append([info, arg])
            except:
                pass

        bridge_filter = contract.events.LockEvent.createFilter(fromBlock=block['number'], toBlock=block['number'])

        # for i in bridge_filter.get_new_entries():
        for i in w3.eth.get_logs(bridge_filter.filter_params):
            tx_hash = i['transactionHash'].hex()
            print('  event', tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            # if receipt['from'] == ETH_BRIDGE_CONTRACT or receipt['to'] == ETH_BRIDGE_CONTRACT:
            # print('  receipt', receipt)
            receipt_args, = contract.events.LockEvent().processReceipt(receipt)
            # print('  receipt_args', receipt_args)
            addr = receipt_args['args']['addr']
            value = str(receipt_args['args']['value'])
            print('    receipt_args', addr, value)

            info = {'sender': tx['from'], 'tx_hash': tx_hash, 'invoke': 'event'}
            arg = {'p': 'minus', 'f': 'eth_deposit', 'args': [value]}
            blk['txs'].append([info, arg])

        if blk['txs']:
            data = json.dumps(blk)
            requests.post('http://127.0.0.1:8010/', data=data.encode('utf8'))

    time.sleep(2)
