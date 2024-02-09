# from __future__ import print_function

# import os
# import time
# import uuid
# import tracemalloc
# import hashlib
import json

# import tornado.options
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.gen
import tornado.escape

import setting
import database
import funcs

global_state = database.get_conn()
global_input = database.get_conn_tx()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/blocks", BlocksHandler),
            (r"/block", BlockHandler),
            (r"/tx", TxHandler),
            (r"/input", InputHandler),
            (r"/", MainHandler),
            ]
        settings = {"debug":True}

        tornado.web.Application.__init__(self, handlers, **settings)

class BlocksHandler(tornado.web.RequestHandler):
    def get(self):
        global global_state
        global global_input
        it = global_input.iteritems()

        it.seek(b'hardhat-block-')
        self.recent_blocks = []
        for key, value_json in it:
            print(key)
            if not key.startswith(b'hardhat-block-'):
                break
            # self.write('%s %s<br>' % (key, value_json))
            _, _, block_height, block_hash = key.decode('utf8').split('-')
            self.recent_blocks.append([setting.REVERSED_NO-int(block_height), block_hash])

        it.seek(b'hardhat-tx-')
        self.recent_transactions = []
        for key, value_json in it:
            print(key)
            if not key.startswith(b'hardhat-transaction-'):
                break
            _, _, tx_hash, block_hash = key.decode('utf8').split('-')
            self.recent_transactions.append([tx_hash, block_hash])

        self.render('template/blocks.html')

class BlockHandler(tornado.web.RequestHandler):
    def get(self):
        block_hash = self.get_argument('blockhash')
        global global_state
        global global_input
        it = global_input.iteritems()

        it.seek(b'hardhat-blocktx-%s' % block_hash.encode('utf8'))
        self.txs = []
        for key, value_json in it:
            print(key)
            if not key.startswith(b'hardhat-blocktx-'):
                break
            # self.write('%s %s<br>' % (key, value_json))
            _, _, block_hash, tx_hash = key.decode('utf8').split('-')
            self.txs.append([block_hash, tx_hash])

        self.render('template/block.html')

class TxHandler(tornado.web.RequestHandler):
    def get(self):
        tx_hash = self.get_argument('txhash')
        global global_state
        global global_input

        it = global_input.iteritems()
        it.seek(b'hardhat-tx-%s' % tx_hash.encode('utf8'))
        self.txs = []
        for key, value_json in it:
            print(key)
            if not key.startswith(b'hardhat-tx-%s' % tx_hash.encode('utf8')):
                break

            # self.write('%s %s<br>' % (key, value_json))
            _, _, tx_hash, block_hash = key.decode('utf8').split('-')
            self.txs.append([tx_hash, block_hash])
        self.render('template/tx.html')

class InputHandler(tornado.web.RequestHandler):
    def get(self):
        global global_state
        global global_input

        it = global_input.iteritems()
        it.seek_to_first()
        self.txs = []
        for key, value_json in it:
            print(key)
            # if not key.startswith(b'hardhat-tx-%s' % tx_hash.encode('utf8')):
            #     break

            self.write('%s %s<br>' % (key, value_json))
            # _, _, tx_hash, block_hash = key.decode('utf8').split('-')
            # self.txs.append([tx_hash, block_hash])
        # self.render('template/tx.html')
        self.finish()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/blocks')

    def post(self):
        # self.add_header('access-control-allow-methods', 'OPTIONS, POST')
        # self.add_header('access-control-allow-origin', 'moz-extension://52ed146e-8386-4e74-9dae-5fe4e9ae20c8')
        global global_input

        blk = json.loads(self.request.body)
        global_input.put(('%s-block-%s-%s' % (blk['chain'], setting.REVERSED_NO - blk['block_number'], blk['block_hash'])).encode('utf8'), b'[]')
        # print(txs)
        for data in blk['txs']:
            print(data)
            info = data[0]
            info['block_number'] = blk['block_number']
            info['block_hash'] = blk['block_hash']
            info['chain'] = blk['chain']
            arg = data[1]
            global_input.put(('%s-blocktx-%s-%s' % (blk['chain'], blk['block_hash'], info['tx_hash'])).encode('utf8'), b'[]')
            global_input.put(('%s-tx-%s-%s' % (blk['chain'], info['tx_hash'], blk['block_hash'])).encode('utf8'), b'[]')
            try:
                funcs.process(info, arg)
            except:
                pass
        self.finish()
        # print(req['method'], req['params'])


def main():
    server = Application()
    server.listen(8010, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

