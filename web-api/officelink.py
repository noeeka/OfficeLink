#!/usr/bin/env python
# -*- coding:utf8 -*-

import tornado.ioloop
import tornado.web
import os.path, json, pymysql, logging, os
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler
import hashlib

FORMAT = '[%(asctime)-15s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s'
formatter = logging.Formatter(FORMAT)
loghandler = RotatingFileHandler('officelink.log', 'a', 10*1024*1024, 10)
loghandler.setFormatter(formatter)

logger = logging.getLogger('officelink')
logger.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

class JsonHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def prepare(self):
        logger.debug(self.request)
        if 'GET' == self.request.method:
            return
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.json_args = json.loads(self.request.body.decode('utf-8'))
        else:
            self.json_args = None

class MainHandler(JsonHandler):
    executor = ThreadPoolExecutor(4)

    @run_on_executor
    def cmd_ps(self):
        pfile = os.popen("ps")
        data = pfile.read()
        pfile.close()
        return data

    @gen.coroutine
    def get(self):
        if not self.current_user:
            self.write('no user')
            return
        self.application.db.ping()
        sql = 'select * from users;'
        cursor = self.application.db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        data = yield self.cmd_ps()
        #result.append(data)
        logger.debug(result)
        self.write(json.dumps(result))
        
class LoginHandler(JsonHandler):
    def get(self):
        self.write("get Hello, world")
        
    def post(self):
        data = self.json_args
        self.set_secure_cookie("user", data["user"])
        md5 = hashlib.md5(data["user"].encode('utf-8')).hexdigest()
        logger.debug('%s %s %s %s', data["user"], data["password"], md5, data)
        self.write(json.dumps(data))
        
    def put(self):
        data = self.json_args
        self.write("put Hello, world")
        logger.debug(data["user"], data["password"])
        
    def delete(self):
        data = self.json_args
        self.write("delete Hello, world")
        logger.debug(data["user"], data["password"])
        
class HelloApp(tornado.web.Application):
    def __init__(self):
        settings = {
            "cookie_secret": 'officelink',
        }
        handlers = [
            (r"/api", MainHandler),
            (r"/api/login", LoginHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        
        config = {
            'host': '192.168.1.220',
            'port': 3306,
            'user': 'systec',
            'password': '123456',
            'db': 'officelink',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        
        self.db = pymysql.connect(**config)

if __name__ == "__main__":
    app = HelloApp()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

