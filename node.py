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

import database
import funcs

global_state = database.get_conn()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/.*", MainHandler)]
        settings = {"debug":True}

        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global global_state
        # self.redirect('/dashboard')
        it = global_state.iteritems()
        it.seek_to_first()
        for key, value_json in it:
            self.write('%s %s<br>' % (key, value_json))
        # self.render('static/index.html')

    def post(self):
        # self.add_header('access-control-allow-methods', 'OPTIONS, POST')
        # self.add_header('access-control-allow-origin', 'moz-extension://52ed146e-8386-4e74-9dae-5fe4e9ae20c8')

        data = json.loads(self.request.body)
        info = data[0]
        arg = data[1]
        funcs.process(info, arg)
        self.finish()
        # print(req['method'], req['params'])


def main():
    server = Application()
    server.listen(8010, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

