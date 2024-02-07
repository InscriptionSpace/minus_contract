
import tornado

import setting
import database


global_state = database.get_conn()
pending_state = database.get_temp_conn()

chain = None
block_number = 0
sender = None

def put(_owner, _asset, _var, _value, _key = None):
    global global_state
    global pending_state
    global chain
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
    # console.log('globalstate_%s_%s_%s_%s' % (asset_name, var, addr, str(setting.REVERSED_NO - block_number).zfill(16)), value_json)
    k = '%s-%s-%s-%s-%s' % (chain, asset_name, var, str(setting.REVERSED_NO - int(block_number)).zfill(16), addr)
    print('put', k, value_json)
    pending_state.put(k.encode('utf8'), value_json.encode('utf8'))


def get(_asset, _var, _default = None, _key = None):
    global pending_state
    global chain
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

    k = '%s-%s-%s-' % (chain, asset_name, var)
    it = pending_state.iteritems()
    it.seek(k.encode('utf8'))
    for key, value_json in it:
        if key.startswith(k.encode('utf8')):
            value = tornado.escape.json_decode(value_json)
            print('get1', k, value)
            return value
        break

    it = global_state.iteritems()
    # console.log(('globalstate_%s_%s_%s' % (asset_name, var, addr)).encode('utf8'))
    it.seek(k.encode('utf8'))

    # value_json = _trie.get(b'state_%s_%s' % (asset_name, var.encode('utf8')))
    for key, value_json in it:
        if key.startswith(k.encode('utf8')):
            # block_number = setting.REVERSED_NO - int(k.replace(b'%s_%s_' % (asset_name, var.encode('utf8')), b''))
            # console.log(k, value_json)
            # try:
            value = tornado.escape.json_decode(value_json)
            # except:
            #     pass
        break

    print('get2', k, value)
    return value


def merge(_block_hash):
    global global_state
    global pending_state
    print('merge')
    it = pending_state.iteritems()
    it.seek_to_first()
    for k, v in it:
        print(k, v)
        chain, asset_name, var, block_number, addr = k.split(b'-')
        global_state.put(b'%s-%s-%s-%s-%s-%s' % (chain, asset_name, var, block_number, _block_hash.encode('utf8'), addr), v)
        pending_state.delete(k)

    # pending_state = database.get_temp_conn()


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


