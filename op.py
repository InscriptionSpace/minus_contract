import json

import state

def mint(sender, s):
    d = json.loads(s)
    assert d['p'] == 'brc-20'
    assert d['op'] == 'mint'
    assert len(d['tick']) == 4
    assert int(d['max']) > 0
    assert int(d['lim']) > 0
    assert int(d['max']) > int(d['lim'])

def transfer(sender, s):
    d = json.loads(s)
    assert d['p'] == 'brc-20'
    assert d['op'] == 'transfer'
    assert len(d['tick']) == 4
    assert int(d['amt']) > 0
    assert state.state[sender] >= int(d['amt'])
    state.state[sender] -= int(d['amt'])
    state.state.setdefault(d['to'], 0)
    state.state[d['to']] += int(d['amt'])

# s = '''
# { 
#   "p": "brc-20",
#   "op": "mint",
#   "tick": "ordi",
#   "max": "100",
#   "lim": "10"
# }
# '''

# mint('0x1', s)

s = '''
{ 
  "p": "brc-20",
  "op": "transfer",
  "tick": "USDT",
  "amt": "100",
  "to": "0x02"
}
'''

state.state['0x1'] = 1000
transfer('0x1', s)
print(state.state)

# print(mint.__code__.co_code.hex())

