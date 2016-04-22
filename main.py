# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

from hashlib import sha1

import xmltodict

import weclient
import wechat

client = weclient.Client()
wc = wechat.WeChat()

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("{'status': 'running'}");

class LoginHandler(tornado.web.RequestHandler):
    # def get(self):
    #     self.write("Hello, world")
    #     client.sendMsg("ogCtWv9jhHIhvgF27NVIxSjgqjn4", "LoggedIn")

    def post(self):
        name = self.get_argument("name")
        pwd = self.get_argument("pwd")
        imgcode = self.get_argument("imgcode")

        client.login(name, pwd, imgcode)

        app_id = self.get_argument("app_id")
        app_secret = self.get_argument("secret")
        token = self.get_argument("token")

        wc.setAppInfo(app_id, app_secret, token)

class WeChatHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if wc.checkSignature(signature, timestamp, nonce):
            self.write(echostr)

    def post(self):
        self.write("success")

        print self.request.uri
        print self.request.body
        data = xmltodict.parse(self.request.body)["xml"]
        print data
        msg_type = data["MsgType"]
        source = data["FromUserName"]
        if msg_type == "text":
            content = data["Content"]
            print content

def make_app():
    return tornado.web.Application([
        (r"/status", StatusHandler),
        (r"/login", LoginHandler),
        (r"/wechat", WeChatHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    print "Server starts and is listening on port 80"
    tornado.ioloop.IOLoop.current().start()
