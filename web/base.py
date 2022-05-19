#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import tornado.web
import sys
from os.path import dirname,abspath


project_path = dirname(dirname(abspath(__file__)))
#__file__用于获取文件的路径，abspath(__file__)获得绝对路径；
#dirname()用于获取上级目录，两个dirname（）相当于获取了当前文件的上级的上级即示例中project2
sys.path.append(project_path)
import libs.stock_web_dic as stock_web_dic


# 基础handler，主要负责检查mysql的数据库链接。
class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")    # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")
    @property
    def db(self):
        try:
            # check every time。
            self.application.db.query("SELECT 1 ")
        except Exception as e:
            print(e)
            self.application.db.reconnect()
        return self.application.db


class LeftMenu:
    def __init__(self, url):
        self.leftMenuList = stock_web_dic.STOCK_WEB_DATA_LIST
        self.current_url = url


# 获得左菜单。
def GetLeftMenu(url):
    return LeftMenu(url)
