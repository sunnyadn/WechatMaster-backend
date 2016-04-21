# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

from hashlib import sha1

import weclient
import wechat

client = weclient.Client()
wc = wechat.WeChat()

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

        wc.setAppInfo(app_id, app_secret)

class WeChatHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if wc.checkSignature(signature, timestamp, nonce, echostr):
            self.write(echostr)

    def post(self):
        msg_type = self.get_argument("MsgType")
        source = self.get_argument("FromUserName")
        if msg_type == "text":
            content = self.get_argument("Content")
            print content

def make_app():
    return tornado.web.Application([
        (r"/login", LoginHandler),
        (r"/wechat", WeChatHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
