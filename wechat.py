import tornado.httpclient

import time
from urllib import urlencode
from hashlib import sha1

class WeChat(object):
    def __init__(self):
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.accessToken = ""
        self.tokenTime = 0
        self.tokenResidue = 0
        self.updateAccessToken()

    def checkSignature(self, sn, timestamp, nonce):
        array = [timestamp, nonce, self.token]
        array.sort()
        combined = "".join(array)
        signature = sha1(combined).hexdigest()
        if sn == signature:
            print "Success!"
            return True
        else:
            print "Failure!", "Signature from wechat is:", sn, "The calculated one is:", signature
            return False

    def setAppInfo(self, id, secret, token):
        self.id = id
        self.secret = secret
        self.token = token

    def updateAccessToken(self):
        if self.accessToken == "" or self.tokenTime + self.tokenResidue < time.time() - 5000:
            query = {
                "grant_type": "client_credential",
                "appid": self.id,
                "secret": self.secret
            }

            url = "https://api.weixin.qq.com/cgi-bin/token?" + urlencode(query)
            response = yield self.client.fetch(url)

            data = eval(response.body)
            if data["access_token"]:
                self.accessToken = data["access_token"]
                self.tokenResidue = data["expires_in"]
                self.tokenTime = time.time()
