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
import libs.stock_web_dic
import base as webBase
import logging
import datetime
import re


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
class GetEditorHtmlHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        print("table name:", name)
        stockWeb = stock_web_dic.STOCK_WEB_DATA_MAP[name]
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        date_now = datetime.datetime.now()
        date_now_str = date_now.strftime("%Y%m%d")
        # 每天的 16 点前显示昨天数据。
        if date_now.hour < 16:
            date_now_str = (date_now + datetime.timedelta(days=-1)).strftime("%Y%m%d")

        try:
            # 增加columns 字段中的【查看股票 东方财富】
            logging.info(eastmoney_name in stockWeb.column_names)
            if eastmoney_name in stockWeb.column_names:
                tmp_idx = stockWeb.column_names.index(eastmoney_name)
                logging.info(tmp_idx)
                try:
                    # 防止重复插入数据。可能会报错。
                    stockWeb.columns.remove("eastmoney_url")
                except Exception as e:
                    print("error :", e)
                stockWeb.columns.insert(tmp_idx, "eastmoney_url")
        except Exception as e:
            print("error :", e)
        logging.info("####################GetStockHtmlHandlerEnd")
        self.render("data_editor.html", stockWeb=stockWeb, date_now=date_now_str,
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


class SaveEditorHandler(webBase.BaseHandler):
    @gen.coroutine
    def post(self):
        action = self.get_argument("action", default=None, strip=False)
        print(action)
        logging.info(action)
        table_name = self.get_argument("table_name", default=None, strip=False)
        print(table_name)
        stockWeb = stock_web_dic.STOCK_WEB_DATA_MAP[table_name]
        # 临时map数组。
        update_param_map = {}
        where_param_map = {}
        date = self.get_argument("date", default=None, strip=False)
        code = self.get_argument("code", default=None, strip=False)
        type = self.get_argument("type", default=None, strip=False)
        color = self.get_argument("color", default=None, strip=False)
        where_param_map['date'] = date
        where_param_map['code'] = code
        update_param_map['type'] = type
        update_param_map['color'] = color


        print(where_param_map)
        if action == "create":
            logging.info("###########################create")
            # 更新sql。
            insert_sql = "INSERT INTO livermore_guess_daily(date, `code`, `name`, latest_price, quote_change, ups_downs, turnover_rate) " \
                         "SELECT date, `code`, `name`, latest_price, quote_change, ups_downs, turnover_rate FROM stock_zh_ah_name" \
                         " WHERE `code`= '%s' and date='%s'; " % (code, date)
            logging.info(insert_sql)
            try:
                self.db.execute(insert_sql)
            except Exception as e:
                err = {"error": str(e)}
                logging.info(err)
                self.write(err)
                return

        elif action == "update":
            logging.info("###########################update")
            # 拼接where 和 update 语句。
            update_columns = ['type', 'color']
            tmp_update = genSql(update_columns, update_param_map, ",")
            tmp_where = genSql(stockWeb.primary_key, where_param_map, "and")
            # 更新sql。
            update_sql = " UPDATE %s SET %s WHERE %s " % (stockWeb.table_name, tmp_update, tmp_where)
            logging.info(update_sql)
            print(update_sql)
            try:
                self.db.execute(update_sql)
                print("success")
            except Exception as e:
                err = {"error": str(e)}
                logging.info(err)
                self.write(err)
                return
        elif action == "remove":
            logging.info("###########################remove")
            # 拼接where 语句。
            tmp_where = genSql(stockWeb.primary_key, where_param_map, "and")
            # 更新sql。
            delete_sql = " DELETE FROM %s WHERE %s " % (stockWeb.table_name, tmp_where)
            logging.info(delete_sql)
            try:
                self.db.execute(delete_sql)
            except Exception as e:
                err = {"error": str(e)}
                logging.info(err)
                self.write(err)
                return
        self.write("{\"data\":[{}]}")


# 拼接sql，将value的key 和 value 放到一起。
def genSql(primary_key, param_map, join_string):
    tmp_sql = ""
    idx = 0
    for tmp_key in primary_key:
        print(tmp_key)
        tmp_val = param_map[tmp_key]
        print(tmp_val)
        if idx == 0:
            tmp_sql = " `%s` = '%s' " % (tmp_key, tmp_val)
        else:
            tmp_sql += join_string + (" `%s` = '%s' " % (tmp_key, tmp_val))
        idx += 1
    return tmp_sql
