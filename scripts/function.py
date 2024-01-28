
import json
import hashlib

from brownie import accounts as a

mint_src = '''def mint(sender, d):
    assert d['f'] == 'mint'
    assert set(d['args'][0]) <= set(string.ascii_uppercase+'_')
    assert int(d['args'][1]) > 0
    sender = sender.lower()
    k = '%s-balance-%s' % (d['args'][0], sender)
    state.setdefault(k, 0)
    state[k] += int(d['args'][1])
'''

transfer_src = '''def transfer(sender, d):
    assert d['f'] == 'transfer'
    asset = d['args'][0]
    assert set(asset) <= set(string.ascii_uppercase+'_')
    assert type(d['args'][1]) is str
    sender = sender.lower()
    to = d['args'][1].lower()
    assert to.startswith('0x')
    assert set(to[2:]) <= set(string.digits+'abcdef')
    val = int(d['args'][2])
    assert val > 0

    k = '%s-balance-%s' % (asset, sender)
    assert state[k] >= val
    state[k] -= val
    k = '%s-balance-%s' % (asset, to)
    state.setdefault(k, 0)
    state[k] += val
'''


# brownie run function
def main():
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'committee_init'}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'committee_add_member', 'args': [a[0].address]}).encode())

    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_propose', 'args': ['mint', mint_src, ['*'], [['mint', ['USDT_']]]]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_vote', 'args': ['mint', hashlib.sha256(mint_src.encode('utf8')).hexdigest()]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_propose', 'args': ['transfer', transfer_src, ['*'], [['mint', ['USDT_']]]]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'function_vote', 'args': ['transfer', hashlib.sha256(transfer_src.encode('utf8')).hexdigest()]}).encode())

    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'mint', 'args': ['U', 100]}).encode())
    a[0].transfer(a[0], 10**18, gas_price=875000000, data=json.dumps({'p':'minus', 'f':'transfer', 'args': ['U', a[1].address, 100]}).encode())
