#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from tornado import gen
import sys
from os.path import dirname,abspath


project_path = dirname(dirname(abspath(__file__)))
#__file__用于获取文件的路径，abspath(__file__)获得绝对路径；
#dirname()用于获取上级目录，两个dirname（）相当于获取了当前文件的上级的上级即示例中project2
sys.path.append(project_path)
import libs.common as common
import libs.stock_web_dic as stock_web_dic
import web.base as webBase
import logging
import datetime

# info 蓝色 云财经
# success 绿色
#  danger 红色 东方财富
#  warning 黄色
WEB_EASTMONEY_URL = u"""
    <a class='btn btn-danger btn-xs tooltip-danger' data-rel="tooltip" data-placement="right" data-original-title="东方财富，股票详细地址，新窗口跳转。"
    href='http://quote.eastmoney.com/%s.html' target='_blank'>东财</a>

    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showIndicatorsWindow('%s');">指标</a>

    <a class='btn btn-warning btn-xs tooltip-warning' data-rel="tooltip" data-placement="right" data-original-title="东方财富，研报地址，本地弹窗窗口。"
    onclick="showDFCFWindow('%s');">东研</a>


    """
# 和在dic中的字符串一致。字符串前面都不特别声明是u""
eastmoney_name = "查看股票"


# 获得页面数据。
class GetBargainHuntingHtmlHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        print("bargain hunting table name:", name)
        stock_web = stock_web_dic.STOCK_WEB_DATA_MAP[name]
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        date_now = datetime.datetime.now()
        date_now_str = date_now.strftime("%Y%m%d")
        # 每天的 16 点前显示昨天数据。
        if date_now.hour < 16:
            date_now_str = (date_now + datetime.timedelta(days=-1)).strftime("%Y%m%d")

        try:
            # 增加columns 字段中的【查看股票 东方财富】
            logging.info(eastmoney_name in stock_web.column_names)
            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)
                logging.info(tmp_idx)
                try:
                    # 防止重复插入数据。可能会报错。
                    stock_web.columns.remove("eastmoney_url")
                except Exception as e:
                    print("error :", e)
                stock_web.columns.insert(tmp_idx, "eastmoney_url")
        except Exception as e:
            print("error :", e)
        logging.info("####################GetBargainHuntingHtmlHandler")
        self.render("stock_bargain_hunting.html", stockWeb=stock_web, date_now=date_now_str,
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 获得股票数据内容。
class GetBargainHuntingDataHandler(webBase.BaseHandler):
    def get(self):
        print("get start")

        # 获得分页参数。
        start_param = self.get_argument("start", default=0, strip=False)
        length_param = self.get_argument("length", default=10, strip=False)
        print("page param:", length_param, start_param)

        name_param = self.get_argument("name", default=None, strip=False)
        # count = self.get_argument("count", default=None, strip=False)
        count = 0
        type_param = self.get_argument("type", default=None, strip=False)

        print("get bargain hunting stock data")
        print("name param:", name_param)
        # print("count:", count)

        stock_web = stock_web_dic.STOCK_WEB_DATA_MAP[name_param]

        # https://datatables.net/manual/server-side
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        order_by_column = []
        order_by_dir = []
        # 支持多排序。使用shift+鼠标左键。

        search_by_column = []
        search_by_data = []

        # 返回search字段。
        for item, val in self.request.arguments.items():
            # logging.info("item: %s, val: %s" % (item, val))
            if str(item).startswith("columns[") and str(item).endswith("[search][value]"):
                logging.info("item: %s, val: %s" % (item, val))
                str_idx = item.replace("columns[", "").replace("][search][value]", "")
                int_idx = int(str_idx)
                # 找到字符串
                str_val = val[0].decode("utf-8")
                if str_val != "":  # 字符串。
                    search_by_column.append(stock_web.columns[int_idx])
                    search_by_data.append(val[0].decode("utf-8"))  # bytes转换字符串

        # 打印日志。
        search_sql = ""
        search_idx = 0
        logging.info("search_sql")

        for item in search_by_column:
            val = search_by_data[search_idx]
            logging.info("idx: %s, column: %s, value: %s " % (search_idx, item, val))
            if item == 'count':
                count = val

            search_idx = search_idx + 1

        order_by_sql = ""
        # 增加排序。

        # 查询数据库。
        limit_sql = ""
        if int(length_param) > 0:
            limit_sql = " LIMIT %s , %s " % (start_param, length_param)

        sql = " select date,`code`,`name`,latest_price,ups_downs,quote_change,count( * ) AS count from guess_indicators_lite_sell_daily" \
              "  GROUP BY name HAVING count(*) > %s ORDER BY date DESC,count ASC %s " % (count, limit_sql)
        count_sql = " select count(DISTINCT `code`) as num from guess_indicators_lite_sell_daily "

        logging.info("select sql : " + sql)
        logging.info("count sql : " + count_sql)
        stock_web_list = self.db.query(sql)

        for tmp_obj in (stock_web_list):
            if type_param == "editor":
                tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
            # logging.info(tmp_obj)
            try:
                # 增加columns 字段中的【东方财富】
                # logging.info("eastmoney_name : %s " % eastmoney_name)
                if eastmoney_name in stock_web.column_names:
                    tmp_idx = stock_web.column_names.index(eastmoney_name)

                    code_tmp = tmp_obj["code"]
                    # 判断上海还是 深圳，东方财富 接口要求。
                    if code_tmp.startswith("6"):
                        code_tmp = "SH" + code_tmp
                    else:
                        code_tmp = "SZ" + code_tmp

                    tmp_url = WEB_EASTMONEY_URL % (tmp_obj["code"], tmp_obj["code"], code_tmp)
                    tmp_obj["eastmoney_url"] = tmp_url
                    # logging.info(tmp_idx)
                    # logging.info(tmp_obj["eastmoney_url"])
                    # logging.info(type(tmp_obj))
                    # tmp.column_names.insert(tmp_idx, eastmoney_name)
            except Exception as e:
                print("error :", e)

        stock_web_size = self.db.query(count_sql)
        # logging.info("stockWebList size : %s " % stock_web_size)

        obj = {
            "draw": 0,
            "recordsTotal": stock_web_size[0]["num"],
            "recordsFiltered": stock_web_size[0]["num"],
            "data": stock_web_list
        }

        # logging.info("get data####################")
        # logging.info(obj)
        self.write(json.dumps(obj))
