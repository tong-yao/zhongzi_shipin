# -*- coding=utf-8 -*-
# @Time : 2019/6/25 16:16 
# @Author : piller
# @File : settings.py 
# @Software: PyCharm
import requests
from fake_useragent import UserAgent
import json


class Proxies(object):
    """获取联卓信息企业代理(旗云代理网站)"""
    BASE_URL = "http://dev.110zy.cn/api/?apikey=45be735b785e8ed00752c4777e0dea8b1e200c2a" \
               "&num=30&type=json&line=mac&proxy_type=putong&sort=1&model=all&protocol=" \
               "http&address=%E5%8C%97%E4%BA%AC&kill_address=&port=&kill_port=&today=false&abroad=1" \
               "&isp=&anonymity=2"
    USERAGENT = UserAgent(verify_ssl=False).random

    def __init__(self):
        self.base_url = Proxies.BASE_URL
        self.user_agent = Proxies.USERAGENT
        self.response = None
        self.headers = {
            "User-Agent": self.user_agent
        }

    def proxies_get(self):
        if self.response is None:
            self.response = requests.get(self.base_url, headers=self.headers, verify=False, timeout=10).content

    def proxies_del(self):
        self.response = None
        self.proxies_get()

    def response_split(self):
        """response json to list to split to return"""
        self.response = json.loads(self.response.decode())

    def proxies_return(self):
        return self.response


def proxies():
    while True:
        try:
            P = Proxies()
            P.proxies_del()
            P.response_split()
            proxies_list = P.proxies_return()
        except json.decoder.JSONDecodeError:
            continue
        else:
            break
    return proxies_list


def user_agent():
    """获取UA"""
    u_a = UserAgent().random
    return u_a
