# -*- coding: utf-8 -*-

import requests
import json
from time import time
from requests.auth import AuthBase

JSON_HEADER = {'content-type': 'application/json'}
EASEMOB_HOST = "https://a1.easemob.com"

DEBUG = True

def parse_appkey(appkey):
    return tuple(appkey.split('#'))

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

class EasemobAuth(AuthBase):
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.get_token()
        return r

    def get_token(self):
        if (self.token is None) or (self.token.is_not_valid()):
            self.token = self.acquire_token() #refresh the token
        return self.token.token

    def acquire_token(self):
        pass

class AppClientAuth(EasemobAuth):
    def __init__(self, org, app, client_id, client_secret):
        super(AppClientAuth, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = EASEMOB_HOST+("/%s/%s/token" % (org, app))
        self.token = None

    def acquire_token(self):
        payload = {'grant_type':'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        success, result = post(self.url, payload)
        if success:
            return Token(result['access_token'], result['expires_in'])
        else:
            pass

class EaseMob:
    def __init__(self):
        f = file("./config.json")
        s = json.load(f)
        config = s['easemob']
        appkey = config['appkey']
        self.org, self.app = parse_appkey(appkey)
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.user_pwd = config['user_pwd']

        self.auth = AppClientAuth(self.org, self.app, self.client_id, self.client_secret)
        print "Get app token with client id/secret: " + self.auth.get_token()

    def user_exists(self, username):
        url = EASEMOB_HOST+("/%s/%s/users/%s" % (self.org, self.app, username))
        return get(url, self.auth)

    def register_new_user(self, username):
        payload = {"username":username, "password":self.user_pwd}
        url = EASEMOB_HOST+("/%s/%s/users" % (self.org, self.app))
        return post(url, payload, self.auth)

    def delete_user(self, username):
        url = EASEMOB_HOST+("/%s/%s/users/%s" % (self.org, self.app, username))
        return delete(url, self.auth)

    def send_text(self, username, text, source):
        payload = { "target_type": "users",
                    "target": [username],
                    "msg": {
                        "type": "txt",
                        "msg": text,
                    },
                    "from": source
                }
        url = EASEMOB_HOST+("/%s/%s/messages" % (self.org, self.app))
        return post(url, payload, self.auth)

    def send_file(self, file_path):
        url = EASEMOB_HOST+("/%s/%s/chatfiles" % (self.org, self.app))
        # files = {'file': open(file_path, 'rb')}
        files = {'file': ('report.xls', open(file_path, 'rb'), 'image/jpeg', {'Expires': '0'})}

        r = requests.post(url, files = files, auth = self.auth)
        return http_result(r)
