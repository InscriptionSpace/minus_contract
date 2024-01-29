
import json
import hashlib

from brownie import accounts as a

mint_src = '''def mint(sender, d):
    assert d['f'] == 'mint'
    asset = d['args'][0]
    assert set(asset) <= set(string.ascii_uppercase+'_')
    value = int(d['args'][1])
    assert value > 0
    sender = sender.lower()
    balance = get(asset, 'balance', 0, sender)
    balance += value
    put(sender, asset, 'balance', balance, sender)
'''

transfer_src = '''def transfer(sender, d):
    assert d['f'] == 'transfer'
    asset = d['args'][0]
    assert set(asset) <= set(string.ascii_uppercase+'_')
    assert type(d['args'][1]) is str
    sender = sender.lower()
    receiver = d['args'][1].lower()
    assert receiver.startswith('0x')
    assert set(receiver[2:]) <= set(string.digits+'abcdef')
    value = int(d['args'][2])
    assert value > 0

    sender_balance = get(asset, 'balance', 0, sender)
    assert sender_balance >= value
    sender_balance -= value
    put(sender, asset, 'balance', sender_balance, sender)
    receiver_balance = get(asset, 'balance', 0, receiver)
    receiver_balance += value
    put(receiver, asset, 'balance', receiver_balance, receiver)
'''


# brownie run function
def main():
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'committee_init'}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'committee_add_member', 'args': [a[0].address]}).encode())

    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_proposal', 'args': ['mint', mint_src, ['*'], [['mint', ['USDT_']]]]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_vote', 'args': ['mint', hashlib.sha256(mint_src.encode('utf8')).hexdigest()]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_proposal', 'args': ['transfer', transfer_src, ['*'], [['mint', ['USDT_']]]]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_vote', 'args': ['transfer', hashlib.sha256(transfer_src.encode('utf8')).hexdigest()]}).encode())

    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'mint', 'args': ['U', 100]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'transfer', 'args': ['U', a[1].address, 100]}).encode())
