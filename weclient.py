# -*- coding: utf-8 -*-
# import tornado.httpclient
import requests

from hashlib import md5
from urllib import urlencode
import re
import random

class Client(object):
    def __init__(self):
        self.httpclient = requests.session()

    def login(self, name, pwd, imgcode = "", callback = None):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://mp.weixin.qq.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        pwd = md5(pwd[0:16]).hexdigest()
        print pwd
        body = {
            "username": name,
            "pwd": pwd,
            "imgcode": imgcode,
            "f": "json"
        }
        # req = tornado.httpclient.HTTPRequest("https://mp.weixin.qq.com/cgi-bin/login", "POST", headers, body)

        # self.httpclient.fetch(req, self.saveToken)
        res = self.httpclient.post("https://mp.weixin.qq.com/cgi-bin/login", headers = headers, data = body, verify = False)
        body = eval(res.text)
        print body
        if body["base_resp"] and body["base_resp"]["ret"] == 0:
            url = body["redirect_url"]
            self.token = re.findall(r".+?=(\d+)$", url)[0]
            print self.token
            self.name = name
            callback(name);
        elif body["base_resp"]:
            print body["base_resp"]["err_msg"]

    def saveToken(self, res):
        body = eval(res.body)
        print body
        url = body["redirect_url"]
        self.token = re.findall(r".+?=(\d+)$", url)[0]
        print self.token

    def sendMsg(self, target, msg, imgcode = ""):
        query = {
            "t": "ajax-response",
            "f": "json",
            "token": self.token,
            "lang": "zh_CN"
        }

        url = "https://mp.weixin.qq.com/cgi-bin/singlesend?" + urlencode(query)
        print url

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7&token=" + self.token + "&lang=zh_CN",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        body = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "random": "0.4150608658290731",
            "mask": "false",
            "tofakeid": target,
            "imgcode": "",
            "type": "1",
            "content": msg,
            "appmsg": "",
        }

        print body

        res=self.httpclient.post(url, data = body, headers = headers, verify = False)
        print res.text

    def onMessageSent(self, res):
        print res.body

    def getUserInfo(self, openid):
        """
        {
            "base_resp":{"ret":0,"err_msg":""},
            "group_info":{
                "group_info_list":[
                    {"group_name":"未分组","group_cnt":6,"group_create_time":1445356773,"group_id":0},
                    {"group_name":"黑名单","group_cnt":0,"group_create_time":1445356773,"group_id":1},
                    {"group_name":"星标组","group_cnt":0,"group_create_time":1445356773,"group_id":2}
                ]
            },
            "user_list":{
                "user_info_list":[
                    {
                        "user_openid":"ogCtWv9jhHIhvgF27NVIxSjgqjn4",
                        "user_name":"Sunny",
                        "user_remark":"",
                        "user_group_id":[],
                        "user_create_time":1446008057,
                        "user_signature":"Keep sunny, keep young.",
                        "user_city":"南京",
                        "user_province":"江苏",
                        "user_country":"中国",
                        "user_head_img":"http:\/\/wx.qlogo.cn\/mmopen\/0RMVBOVagxNg78gfesfYC09jw9wtBbN0x0pNT9xy3UVo2bicN07FMgjKc7yC4OBvcibxKjI56Gc3gCyRvcZaBKPupOibw3IH5pL\/0",
                        "user_gender":1,
                        "user_msg_cnt":26
                    }
                ]
            }
        }
        """

        url = "https://mp.weixin.qq.com/cgi-bin/user_tag?action=get_fans_info"

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://mp.weixin.qq.com/cgi-bin/user_tag?action=get_all_data&lang=zh_CN&token=" + self.token,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        body = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "random": "0.4150608658290731",
            "user_openid": openid
        }

        res=self.httpclient.post(url, data = body, headers = headers, verify = False)
        print res.text
        return res["user_list"]["user_info_list"]
