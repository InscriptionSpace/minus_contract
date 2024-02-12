import json
import hashlib
import string
import codeop

import setting
import database
import vm
import space
from space import get
from space import put

global_input = database.get_conn_tx()

def hop(info, d):
    assert d['f'] == 'hop'
    sender = info['sender'].lower()
    from_chain = info['chain']
    from_txhash = info['tx_hash']

    chain = d['args'][0]
    assert chain in setting.chains
    block_number = int(d['args'][1])
    asset = d['args'][2]
    assert asset in setting.assets
    value = int(d['args'][3])
    assert value > 0
    balance = get(asset, 'balance', 0, sender)
    balance -= value
    assert balance >= 0
    put(sender, asset, 'balance', balance, sender)

    to_sender = sender # in case sending to a chain with different 
    global_input.put(('%s-inject-%s-%s-%s' % (chain, setting.REVERSED_NO - block_number, from_chain, from_txhash)).encode('utf8'), json.dumps([asset, to_sender, value]).encode('utf8'))

def usdt_deposit(sender, d):
    assert d['f'] == 'usdt_deposit'

def eth_deposit(sender, d):
    assert d['f'] == 'eth_deposit'
    value = int(d['args'][0])
    assert value > 0
    sender = sender.lower()
    balance = get('ETH', 'balance', 0, sender)
    balance += value
    put(sender, 'ETH', 'balance', balance, sender)

# def withdraw(sender, d):
#     assert d['f'] == 'withdraw'

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
    sender = sender.lower()
    handle = d['args'][0]
    assert type(handle) is str
    assert set(handle) <= set(string.digits+string.ascii_lowercase+'_')
    assert len(handle) >= 5 and len(handle) < 20

    eth_address = get('handle', 'handle2eth', None, handle)
    sender_handle = get('handle', 'eth2handle', None, sender)
    assert eth_address is None and sender_handle is None

    # payment required
    put(sender, 'handle', 'handle2eth', sender, handle)
    put(sender, 'handle', 'eth2handle', handle, sender)

def handle_change(sender, d):
    assert d['f'] == 'handle_change'

    sender_handle = get('handle', 'eth2handle', None, sender)
    assert sender_handle
    eth_address = get('handle', 'handle2eth', None, sender_handle)


def resolve(sender, d):
    assert d['f'] == 'resolve'
    handle = d['args'][0]
    assert type(handle) is str
    assert set(handle) <= set(string.digits+string.ascii_lowercase+'_')
    assert len(handle) >= 5 and len(handle) < 20

    eth_address = get('handle', 'handle2eth', None, handle)
    print('resolve', eth_address)

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
    global global_input

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

    elif arg.get('f') == 'hop':
        hop(info, arg)

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
        print('native eth_deposit', info['invoke'])
        assert info['invoke'] == 'event'
        eth_deposit(sender, arg)

    elif arg.get('f') == 'resolve':
        print('native resolve')
        resolve(sender, arg)

    elif arg.get('f') == 'handle_reg':
        print('native handle_reg')
        handle_reg(sender, arg)

    elif arg.get('f') == 'mint':
        print('native mint')
        mint(sender, arg)

    elif arg.get('f') == 'transfer':
        print('native transfer')
        transfer(sender, arg)

    it = global_input.iteritems()
    it.seek(('%s-inject-%s-' % (chain, setting.REVERSED_NO - block_number)).encode('utf8'))
    for key, value_json in it:
        print(key)
        if not key.startswith(('%s-inject-%s-' % (chain, setting.REVERSED_NO - block_number)).encode('utf8')):
            break

        _, _, _, from_chain, from_tx_hash = key.decode('utf8').split('-')
        to_asset, to_sender, to_value = json.loads(value_json)

        print(from_chain, from_tx_hash, value_json)

        to_balance = get(to_asset, 'balance', 0, to_sender)
        assert to_value > 0
        to_balance += to_value
        put(to_sender, to_asset, 'balance', to_balance, to_sender)

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

