# from __future__ import print_function

# import os
# import time
# import uuid
# import tracemalloc
import hashlib
import json
import binascii

# import tornado.options
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.gen
import tornado.escape


import funcs

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler)]
        settings = {"debug":True}

        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # self.redirect('/dashboard')
        pass

    def post(self):
        self.add_header('access-control-allow-methods', 'OPTIONS, POST')
        # self.add_header('access-control-allow-origin', 'moz-extension://52ed146e-8386-4e74-9dae-5fe4e9ae20c8')

        data = json.loads(self.request.body)
        sender = data[0]
        arg = data[1]
        funcs.process(sender, arg)
        # print(req['method'], req['params'])


def main():
    server = Application()
    server.listen(8010, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

