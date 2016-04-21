import tornado.httpclient

import time
from urllib import urlencode

class EaseMob(object):
    def __init__(self):
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.accessToken = ""
        self.tokenTime = 0
        self.tokenResidue = 0
        self.client_id = "YXA6dBGzcAJdEeaFJu0a51US0w"
        self.secret = "YXA6CVsCrGA92IXki6p6JE1I8Sq3aeM"
        self.updateAccessToken()

    def updateAccessToken(self):
        if self.accessToken == "" or self.tokenTime + self.tokenResidue < time.time() - 5000:
            data = {
                "grant_type": "client_credential",
                "client_id": self.client_id,
                "client_secret": self.secret
            }

            url = "https://a1.easemob.com/yexing/wechatter/token"
            response = yield self.client.fetch(url, "POST", body = urlencode(data))

            data = eval(response.body)
            if data["access_token"]:
                self.accessToken = data["access_token"]
                self.tokenResidue = data["expires_in"]
                self.tokenTime = time.time()

    def register(self, name, password):
        data = {
            "username": name,
            "password": password
        }

        url = "https://a1.easemob.com/yexing/wechatter/users"
        response = yield self.client.fetch(url, "POST", body = urlencode(data))
