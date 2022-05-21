#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from lib2to3.pgen2 import token
from tornado import gen
import logging
import datetime
import sys
from os.path import dirname,abspath


project_path = dirname(dirname(abspath(__file__)))
#__file__用于获取文件的路径，abspath(__file__)获得绝对路径；
#dirname()用于获取上级目录，两个dirname（）相当于获取了当前文件的上级的上级即示例中project2
sys.path.append(project_path)
import libs.common as common
import web.base as webBase

tokens = {"admin": {"token": 'admin-token'},"editor": {"token": 'editor-token'}}
users = {'admin-token': {"roles": ['admin'],  "introduction": 'I am a super administrator',  "avatar": 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',  "name": 'Super Admin'},'editor-token': {  "roles": ['editor'],  "introduction": 'I am an editor',  "avatar": 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',  "name": 'Normal Editor'}}

# 登录接口，需要form表单的body
class LoginHandler(webBase.BaseHandler):
    @gen.coroutine
    def post(self):
        data = json.loads(self.request.body)
        logging.info(data)
        obj={
            "code": 20000,
            "data": tokens[data["username"]]
        }
        logging.info(obj)
        self.write(json.dumps(obj))
        

# 查询用户权限接口，根据params里面的token看用户信息
class LoginInfoHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        token = self.get_argument("token", default=0, strip=False)
        logging.info("get data####################")
        obj={
            "code": 20000,
            "data": users[token]
        }
        logging.info(obj)
        self.write(json.dumps(obj))
        
        
# 登出接口，虽然是post方法但是无参
class LogoutHandler(webBase.BaseHandler):
    @gen.coroutine
    def post(self):
        logging.info("get data####################")
        obj={
            "code": 20000,
            "data": "success"
        }
        logging.info(obj)
        self.write(json.dumps(obj))