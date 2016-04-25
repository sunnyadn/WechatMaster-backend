# -*- coding: utf-8 -*-

import requests
import json
from time import time
from requests.auth import AuthBase
from urllib import urlencode

WECHAT_HOST = "https://api.weixin.qq.com/cgi-bin"

DEBUG = True

def post(url, payload, auth = None):
    r = requests.post(url, data = json.dumps(payload), headers = JSON_HEADER, auth = auth, verify = False)
    return http_result(r)

def get(url, auth = None):
    r = requests.get(url, headers = JSON_HEADER, auth = auth, verify = False)
    return http_result(r)

def delete(url, auth = None):
    r = requests.delete(url, headers = JSON_HEADER, auth = auth, verify = False)
    return http_result(r)

def http_result(r):
    if DEBUG:
        error_log = {
                    "method": r.request.method,
                    "url": r.request.url,
                    "request_header": dict(r.request.headers),
                    "response_header": dict(r.headers),
                    "response": r.text
                }
        if r.request.body:
            error_log["payload"] = r.request.body
        print json.dumps(error_log)

    if r.status_code == requests.codes.ok:
        return True, r.json()
    else:
        return False, r.text


class Token:
    def __init__(self, token, exipres_in):
        self.token = token
        self.exipres_in = exipres_in + int(time())

    def is_not_valid(self):
        return time() > self.exipres_in

class WeChatAuth(AuthBase):
    def get_token(self):
        if (self.token is None) or (self.token.is_not_valid()):
            self.token = self.acquire_token() #refresh the token
        return self.token.token

    def acquire_token(self):
        pass

class AppClientAuth(WeChatAuth):
    def __init__(self, app_id, app_secret):
        query = {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret
        }
        self.url = WECHAT_HOST + "/token?" + urlencode(query)
        self.token = None

    def acquire_token(self):
        success, result = get(self.url)
        if success:
            return Token(result['access_token'], result['expires_in'])
        else:
            pass

class WeChat:
    def setAppInfo(self, app_id, app_secret, token):
        self.auth = AppClientAuth(app_id, app_secret)
        self.token = token

    def getUserInfo(self, open_id):
        query = {
            "access_token": self.auth.get_token(),
            "openid": open_id,
            "lang": "zh_CN"
        }
        url = WECHAT_HOST+"/info?"+urlencode(query)
        success, result = get(url)
        print result
        return result

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
