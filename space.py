import os

import rocksdb
import tornado


conn = None
def get_conn():
    global conn
    if conn:
        return conn

    if not os.path.exists('states'):
        os.makedirs('states')
    conn = rocksdb.DB('states/inspace.db', rocksdb.Options(create_if_missing=True))
    return conn


# os.removedirs('/dev/shm/tempspace.db')
temp_conn = None
def get_temp_conn():
    global temp_conn

    temp_conn = rocksdb.DB('/dev/shm/tempspace.db', rocksdb.Options(create_if_missing=True))
    return temp_conn


global_state = get_conn()
pending_state = get_temp_conn()

block_number = 0
sender = None

def put(_owner, _asset, _var, _value, _key = None):
    global global_state
    global pending_state
    global block_number
    global sender

    assert type(_var) is str
    # assert set(_var) <= STATE_KEY_LETTERS
    if _key is not None:
        assert type(_key) is str
        # assert set(_key) <= STATE_KEY_LETTERS
        var = '%s[%s]' % (_var, _key)
    else:
        var = _var

    asset_name = _asset
    addr = _owner.lower()
    value_json = tornado.escape.json_encode(_value)
    # console.log('globalstate_%s_%s_%s_%s' % (asset_name, var, addr, str(10**15 - block_number).zfill(16)), value_json)
    k = 'globalstate-%s-%s-%s-%s' % (asset_name, var, str(10**15 - int(block_number)).zfill(16), addr)
    print('put', k)
    pending_state.put(k.encode('utf8'), value_json.encode('utf8'))


def get(_asset, _var, _default = None, _key = None):
    global pending_state
    global block_number
    global sender
    #console.log(pending_state)
    #console.log(block_number)
    #console.log(asset_name)

    asset_name = _asset
    value = _default
    assert type(_var) is str
    # assert set(_var) <= STATE_KEY_LETTERS
    if _key is not None:
        assert type(_key) is str
        # assert set(_key) <= STATE_KEY_LETTERS
        var = '%s[%s]' % (_var, _key)
    else:
        var = _var

    k = 'globalstate-%s-%s-' % (asset_name, var)
    print('get1', k)
    it = pending_state.iteritems()
    it.seek(k.encode('utf8'))
    for key, value_json in it:
        if key.startswith(k.encode('utf8')):
            value = tornado.escape.json_decode(value_json)
            return value
        break

    it = global_state.iteritems()
    # console.log(('globalstate_%s_%s_%s' % (asset_name, var, addr)).encode('utf8'))
    it.seek(k.encode('utf8'))

    # value_json = _trie.get(b'state_%s_%s' % (asset_name, var.encode('utf8')))
    for key, value_json in it:
        if key.startswith(('globalstate-%s-%s-' % (asset_name, var)).encode('utf8')):
            # block_number = 10**15 - int(k.replace(b'%s_%s_' % (asset_name, var.encode('utf8')), b''))
            # console.log(k, value_json)
            # try:
            value = tornado.escape.json_decode(value_json)
            # except:
            #     pass
        break

    print('get2', value)
    return value


def merge(_block_hash, _pending_state):
    global global_state
    global pending_state
    # console.log('merge')
    for k, v in _pending_state.items():
        # console.log(k,v)
        _, asset_name, var, block_number, addr = k.split('_')
        global_state.put(('globalstate-%s-%s-%s-%s-%s' % (asset_name, var, str(10**15 - int(block_number)).zfill(16), _block_hash, addr)).encode('utf8'), v.encode('utf8'))

    pending_state = get_temp_conn()


def call(_addr, fn, params):
    global block_number
    global asset_name
    global sender

    addr = _addr.lower()
    # console.log(addr, fn, params)
    # console.log(contracts.vm_map[addr])
    func_params = []
    for k, v in zip(contracts.params_map[addr][fn], params):
        print('type', k, v)
        if k == 'address':
            func_params.append(web3.Web3.to_checksum_address(v))
        elif k == 'uint256':
            func_params.append(v)

    contracts.vm_map[addr].global_vars['_block_number'] = block_number
    contracts.vm_map[addr].global_vars['_call'] = call
    contracts.vm_map[addr].global_vars['_get'] = get
    contracts.vm_map[addr].global_vars['_put'] = put
    contracts.vm_map[addr].global_vars['_sender'] = sender.lower()
    asset_name = addr
    contracts.vm_map[addr].global_vars['_self'] = asset_name
    contracts.vm_map[addr].run(func_params, fn)
    return


if __name__ == '__main__':
    state['abc'] = 0
    print(state['abc'])
