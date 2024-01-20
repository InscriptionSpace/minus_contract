import json

import state

def mint(sender, d):
    assert d['p'] == 'minus'
    assert d['f'] == 'mint'
    # assert len(d['tick']) == 4
    # assert int(d['max']) > 0
    # assert int(d['lim']) > 0
    # assert int(d['max']) > int(d['lim'])
    assert int(d['amt']) > 0
    state.state.setdefault(sender, 0)
    state.state[sender] += int(d['amt'])

def transfer(sender, d):
    assert d['p'] == 'minus'
    assert d['f'] == 'transfer'
    # assert len(d['tick']) == 4
    assert int(d['amt']) > 0
    assert state.state[sender] >= int(d['amt'])
    state.state[sender] -= int(d['amt'])
    state.state.setdefault(d['to'], 0)
    state.state[d['to']] += int(d['amt'])

def process(sender, arg):
    # d = json.loads(s)
    # print(s)
    if arg.get('f') == 'mint':
        mint(sender, arg)
    elif arg.get('f') == 'transfer':
        transfer(sender, arg)

# s = '''
# { 
#   "p": "minus",
#   "op": "mint",
#   "tick": "ordi",
#   "max": "100",
#   "lim": "10"
# }
# '''

# mint('0x1', s)

if __name__ == '__main__':
    d = { 
        "p": "minus",
        "f": "transfer",
        "tick": "USDT",
        "amt": "100",
        "to": "0x02"
    }

    state.state['0x1'] = 1000
    transfer('0x1', d)
    print(state.state)

    # print(mint.__code__.co_code.hex())

