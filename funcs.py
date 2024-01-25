import json

import state


def bridge(sender, d):
    assert d['f'] == 'bridge'

def hop(sender, d):
    assert d['f'] == 'hop'

# def deploy(sender, d):
#     assert d['f'] == 'deploy'

def mint(sender, d):
    assert d['f'] == 'mint'
    # assert len(d['tick']) == 4
    # assert int(d['max']) > 0
    # assert int(d['lim']) > 0
    # assert int(d['max']) > int(d['lim'])
    assert int(d['amt']) > 0
    state.state.setdefault(sender, 0)
    state.state[sender] += int(d['amt'])

# assets related
def transfer(sender, d):
    assert d['f'] == 'transfer'
    # assert len(d['tick']) == 4
    assert int(d['amt']) > 0
    assert state.state[sender] >= int(d['amt'])
    state.state[sender] -= int(d['amt'])
    state.state.setdefault(d['to'], 0)
    state.state[d['to']] += int(d['amt'])

def transfer_from(sender, d):
    assert d['f'] == 'transfer_from'

def approve(sender, d):
    assert d['f'] == 'approve'

# handle related
def handle_reg(sender, d):
    assert d['f'] == 'handle_reg'

def resolve(sender, d):
    assert d['f'] == 'resolve'

def reverse(sender, d):
    assert d['f'] == 'reverse'

# committee
def committee_init(sender, d):
    assert d['f'] == 'committee_init'
    k = 'committee_members'
    committee_members = state.state.get(k, [])
    assert not committee_members
    state.state[k] = [sender]

def committee_add_member(sender, d):
    assert d['f'] == 'committee_add_member'
    committee_members = set(state.state.get('committee_members', []))
    assert sender in committee_members

    k = 'committee_propose_%s' % d['args'][0]
    state.state.setdefault(k, [])
    votes = set(state.state[k])
    votes.add(sender)

    print(len(votes), len(committee_members), len(committee_members)*2//3)
    if len(votes) >= len(committee_members)*2//3:
        committee_members.add(d['args'][0])
        state.state['committee_members'] = list(committee_members)
        del state.state[k]
    else:
        state.state[k] = list(votes)

def committee_remove_member(sender, d):
    assert d['f'] == 'committee_remove_member'

def code_propose(sender, d):
    assert d['f'] == 'code_propose'

def code_vote(sender, d):
    assert d['f'] == 'code_vote'

def tick_propose(sender, d):
    assert d['f'] == 'tick_propose'

def tick_vote(sender, d):
    assert d['f'] == 'tick_vote'

def process(sender, arg):
    assert arg['p'] == 'minus'
    # print(sender, arg.get('f'))
    if arg.get('f') == 'mint':
        mint(sender, arg)
    elif arg.get('f') == 'transfer':
        transfer(sender, arg)
    elif arg.get('f') == 'committee_init':
        committee_init(sender, arg)
    elif arg.get('f') == 'committee_add_member':
        committee_add_member(sender, arg)
    elif arg.get('f') == 'committee_remove_member':
        committee_remove_member(sender, arg)
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

