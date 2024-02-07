import json
import hashlib
import string
import codeop

import vm
import space
from space import get
from space import put


def usdt_deposit(sender, d):
    assert d['f'] == 'usdt_deposit'

def eth_deposit(sender, d):
    assert d['f'] == 'eth_deposit'
    value = int(d['args'][0])
    assert value > 0
    sender = sender.lower()
    balance = get('eth', 'balance', 0, sender)
    balance += value
    put(sender, 'eth', 'balance', balance, sender)

def withdraw(sender, d):
    assert d['f'] == 'withdraw'

def hop(sender, d):
    assert d['f'] == 'hop'

# def deploy(sender, d):
#     assert d['f'] == 'deploy'

def mint(sender, d):
    assert d['f'] == 'mint'
    asset = d['args'][0]
    assert set(asset) <= set(string.ascii_uppercase+'_')
    value = int(d['args'][1])
    assert value > 0
    sender = sender.lower()
    balance = get(asset, 'balance', 0, sender)
    balance += value
    put(sender, asset, 'balance', balance, sender)

# assets related
def transfer(sender, d):
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
    committee_members = get('committee', 'members', [])
    print(committee_members)
    assert not committee_members
    put(sender, 'committee', 'members', [sender])


def committee_add_member(sender, d):
    assert d['f'] == 'committee_add_member'
    committee_members = set(get('committee', 'members', []))
    assert sender in committee_members

    user = d['args'][0]
    votes = set(get('committee', 'proposal', [], user))
    votes.add(sender)

    # print(len(votes), len(committee_members), len(committee_members)*2//3)
    if len(votes) >= len(committee_members)*2//3:
        committee_members.add(d['args'][0])
        put(sender, 'committee', 'members', list(committee_members))
    else:
        put(sender, 'committee', 'proposal', list(votes), user)

def committee_remove_member(sender, d):
    assert d['f'] == 'committee_remove_member'

def function_proposal(sender, d):
    assert d['f'] == 'function_proposal'
    fname = d['args'][0]
    assert set(fname) <= set(string.ascii_lowercase+'_')
    sourcecode = d['args'][1]

    require = d['args'][2]
    for i in require:
        assert type(i) is list
        assert set(i[0]) <= set(string.ascii_lowercase+'_')
        assert type(i[1]) is list
        for j in i[1]:
            assert set(j) <= set(string.ascii_uppercase+'_')

    asset_permission = d['args'][3]
    assert type(asset_permission) is list
    for i in asset_permission:
        assert i == '*' or set(i) <= set(string.ascii_lowercase+'_')

    invoke_permission = d['args'][4]
    assert type(invoke_permission) is list
    for i in invoke_permission:
        assert i == '*' or set(i) <= set(string.ascii_lowercase+'_')

    hexdigest = hashlib.sha256(sourcecode.encode('utf8')).hexdigest()
    k = 'function-proposal-%s:%s' % (fname, hexdigest)
    put(sender, 'function', 'proposal', {'sourcecode': sourcecode, 'asset_permission': asset_permission, 'require': require, 'votes': []}, '%s:%s' % (fname, hexdigest))


def function_vote(sender, d):
    assert d['f'] == 'function_vote'
    committee_members = set(get('committee', 'members', []))
    assert sender in committee_members

    fname = d['args'][0]
    sourcecode_hexdigest = d['args'][1]
    proposal = get('function', 'proposal', None, '%s:%s' % (fname, sourcecode_hexdigest))
    votes = set(proposal['votes'])
    votes.add(sender)

    print(len(votes), len(committee_members), len(committee_members)*2//3)
    if len(votes) >= len(committee_members)*2//3:
        del proposal['votes']
        put(sender, 'function', 'code', proposal, fname)
    else:
        proposal['votes'] = list(votes)
        put(sender, 'function', 'proposal', proposal, '%s:%s' % (fname, sourcecode_hexdigest))


def token_proposal(sender, d):
    assert d['f'] == 'token_proposal'

def token_vote(sender, d):
    assert d['f'] == 'token_vote'

def process(info, arg):
    sender = info['sender']
    block_number = info['block_number']
    space.block_number = block_number
    block_hash = info['block_hash']
    chain = info['chain']
    space.chain = chain
    assert arg['p'] == 'minus'

    fname = arg.get('f', '')
    code = get('function', 'code', None, fname)
    if arg.get('f') == 'committee_init':
        committee_init(sender, arg)
    elif arg.get('f') == 'committee_add_member':
        committee_add_member(sender, arg)
    elif arg.get('f') == 'committee_remove_member':
        committee_remove_member(sender, arg)

    elif arg.get('f') == 'function_proposal':
        function_proposal(sender, arg)
    elif arg.get('f') == 'function_vote':
        function_vote(sender, arg)

    elif code is not None:
        print(code['sourcecode'])
        c = codeop.compile_command(code['sourcecode'], symbol="exec")
        f = c.co_consts[0]
        # print(c.co_consts[0].co_code.hex())
        print(c.co_consts[0].co_varnames)
        print(c.co_consts[0].co_argcount)
        v = vm.VM()
        v.import_src(f)
        v.global_vars['string'] = string
        v.global_vars['get'] = get
        v.global_vars['put'] = put
        v.global_vars['print'] = print
        v.native_vars.add(get)
        v.native_vars.add(put)
        v.native_vars.add(print)
        v.run([sender, arg])
        space.merge(block_hash)

    elif arg.get('f') == 'eth_deposit':
        print('native eth_deposit')
        assert info['invoke'] == 'event'
        eth_deposit(sender, arg)

    elif arg.get('f') == 'mint':
        print('native mint')
        mint(sender, arg)

    elif arg.get('f') == 'transfer':
        print('native transfer')
        transfer(sender, arg)

    # print(state)

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
    print(mint.__code__.co_code.hex())

