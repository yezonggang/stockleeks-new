#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import logging
import os.path
from logging.handlers import TimedRotatingFileHandler
import torndb
import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.log import access_log
import dataTableHandler as dataTableHandler
import loginHandler as loginHandler
import base as webBase
import pandas as pd
import numpy as np
import akshare as ak
import bokeh as bh
from tornado.options import define, options
import sys
from os.path import dirname,abspath

from web.loginHandler import LoginHandler
project_path = dirname(dirname(abspath(__file__)))
#__file__用于获取文件的路径，abspath(__file__)获得绝对路径；
#dirname()用于获取上级目录，两个dirname（）相当于获取了当前文件的上级的上级即示例中project2
sys.path.append(project_path)
import libs.common as common



define('port', default=8888, help='run on the given port', type=int)
define('mode', default="info", help='run on info', type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # 设置路由
            # 使用datatable 展示报表数据模块。
            (r"/stock/api_data", dataTableHandler.GetStockDataHandler),
            (r"/stock/login", loginHandler.LoginHandler),
            (r"/stock/login_info", loginHandler.LoginInfoHandler),
            (r"/stock/logout", loginHandler.LogoutHandler),
            # 数据修改dataEditor。
            # 获得股票指标数据。
        ]

        # 配置
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,  # True,
            # cookie加密
            cookie_secret="027bb1b670eddf0392cdda8709268a17b58b7",
            debug=True,
            compress_response=True,
        )
        settings["log_function"] = log_func
        super(Application, self).__init__(handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            charset="utf8", max_idle_time=3600, connect_timeout=1000,
            host=common.MYSQL_HOST, database=common.MYSQL_DB,
            user=common.MYSQL_USER, password=common.MYSQL_PWD)


# 日志格式化
class LogFormatter(tornado.log.LogFormatter):

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def log_func(handler):
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    log_method("%d %s %s (%s) %s %s %.2fms",
               handler.get_status(), handler.request.method,
               handler.request.uri, handler.request.remote_ip,
               handler.request.headers["User-Agent"],
               handler.request.arguments,
               request_time)


def init_logging(log_file):
    # 使用TimedRotatingFileHandler处理器
    file_handler = TimedRotatingFileHandler(log_file, when="d", interval=1, backupCount=30)
    # 输出格式
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(lineno)d]  %(message)s"
    )
    file_handler.setFormatter(log_formatter)
    # 将处理器附加到根logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


# 首页handler。
class HomeHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        print("################## index.html ##################")
        pandasVersion = pd.__version__
        numpyVersion = np.__version__
        akshareVersion = ak.__version__
        bokehVersion = bh.__version__
        # talibVersion = talib.__version__
        # jupyterVersion = jupyter.__version__
        # stockstatsVersion = ss.__version__ # 没有这个函数，但是好久不更新了
        # https://github.com/jealous/stockstats
        self.render("index.html", pandasVersion=pandasVersion,
                    numpyVersion=numpyVersion,
                    akshareVersion=akshareVersion,
                    bokehVersion=bokehVersion,
                    stockstatsVersion="0.3.2",
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))



def main():
    tornado.options.parse_command_line()
    # [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9904
    http_server.listen(port)
    # tornado.options.options.logging = "debug"
    log_path = '/data/logs'
    init_logging("%s/web.%s.%s.log" % (log_path, tornado.options.options.mode, tornado.options.options.port))
    # 日志保存到文件
    # tornado.options.define("log_file_prefix", default="/data/logs/web.log")
    # 日志文件按时间日期分割
    # tornado.options.define("log_rotate_mode", default='time')  # 轮询模式: time or size
    # tornado.options.define("log_rotate_when", default='S')  # 单位: S / M / H / D / W0 - W6
    # tornado.options.define("log_rotate_interval", default=60)  # 间隔: 60秒
    tornado.options.parse_command_line()

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
