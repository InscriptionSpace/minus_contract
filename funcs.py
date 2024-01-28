import json
import hashlib
import string

from state import state


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
    state.setdefault(sender, 0)
    state[sender] += int(d['amt'])

# assets related
def transfer(sender, d):
    assert d['f'] == 'transfer'
    # assert len(d['tick']) == 4
    assert int(d['amt']) > 0
    assert state[sender] >= int(d['amt'])
    state[sender] -= int(d['amt'])
    state.setdefault(d['to'], 0)
    state[d['to']] += int(d['amt'])

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
    committee_members = state.get(k, [])
    assert not committee_members
    state[k] = [sender]

def committee_add_member(sender, d):
    assert d['f'] == 'committee_add_member'
    committee_members = set(state.get('committee_members', []))
    assert sender in committee_members

    k = 'committee_propose_%s' % d['args'][0]
    state.setdefault(k, [])
    votes = set(state[k])
    votes.add(sender)

    print(len(votes), len(committee_members), len(committee_members)*2//3)
    if len(votes) >= len(committee_members)*2//3:
        committee_members.add(d['args'][0])
        state['committee_members'] = list(committee_members)
        del state[k]
    else:
        state[k] = list(votes)

def committee_remove_member(sender, d):
    assert d['f'] == 'committee_remove_member'

def function_propose(sender, d):
    assert d['f'] == 'function_propose'
    fname = d['args'][0]
    assert set(fname) <= set(string.ascii_lowercase+'_')
    sourcecode = d['args'][1]
    permission = d['args'][2]
    print(permission)
    assert type(permission) is list
    for i in permission:
        assert i == '*' or set(i) <= set(string.ascii_lowercase+'_')

    require = d['args'][3]
    for i in require:
        assert type(i) is list
        assert set(i[0]) <= set(string.ascii_lowercase+'_')
        assert type(i[1]) is list
        for j in i[1]:
            assert set(j) <= set(string.ascii_uppercase+'_')

    hexdigest = hashlib.sha256(sourcecode.encode('utf8')).hexdigest()
    k = 'function_propose_%s:%s' % (fname, hexdigest)
    state[k] = {'sourcecode': sourcecode, 'permission': permission, 'require': require, 'votes': []}


def function_vote(sender, d):
    assert d['f'] == 'function_vote'
    committee_members = set(state.get('committee_members', []))
    assert sender in committee_members

    fname = d['args'][0]
    sourcecode_hexdigest = d['args'][1]
    k = 'function_propose_%s:%s' % (fname, sourcecode_hexdigest)
    votes = set(state[k]['votes'])
    votes.add(sender)

    print(len(votes), len(committee_members), len(committee_members)*2//3)
    if len(votes) >= len(committee_members)*2//3:
        state['function_code_%s' % fname] = state[k]
        del state['function_code_%s' % fname]['votes']
        del state[k]
    else:
        state[k]['votes'] = list(votes)


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

    elif arg.get('f') == 'function_propose':
        function_propose(sender, arg)
    elif arg.get('f') == 'function_vote':
        function_vote(sender, arg)

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

    state['0x1'] = 1000
    transfer('0x1', d)
    print(state)

    # print(mint.__code__.co_code.hex())

