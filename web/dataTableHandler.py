#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from tkinter.messagebox import NO
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
import libs.stock_web_dic as stock_web_dic
import web.base as webBase


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
class GetStockHtmlHandler(webBase.BaseHandler):
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
        self.render("stock_web.html", stockWeb=stockWeb, date_now=date_now_str,
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 获得股票数据内容。
class GetStockDataHandler(webBase.BaseHandler):
    def get(self):
        print("get start")

        # 获得分页参数。
        page_param = self.get_argument("page", default=0, strip=False)
        limit_param = self.get_argument("limit", default=10, strip=False)
        print("page param:", page_param, limit_param)

        name_param = self.get_argument("name", default=None, strip=False)
        code_param = self.get_argument("code", default=None, strip=False)
        orderby_param = self.get_argument("orderby", default=None, strip=False)

        print("get stock data")
        print("name param:", name_param)

        # 查询数据库。
        order_by_sql = " order by "+orderby_param[1:]+(" desc " if orderby_param.startswith('+') else " asc ");
        where_sql=" "
        if (name_param!=None or code_param!=None):
            if(name_param!=None and code_param==None):
                where_sql="where name= %s" %(name_param)
            if(name_param==None and code_param!=None):
                where_sql="where code= %s" %(code_param)
            if (name_param!=None and code_param!=None):
                where_sql="where code= %s and name= %s" %(code_param,name_param)
        if((name_param==None or name_param=='') and (code_param==None or code_param=='')):
            where_sql=" "
        search_sql ="select code,name,latest_price,quote_change,ups_downs,volume,turnover,amplitude,high,low,open,closed,quantity_ratio,turnover_rate,pe_dynamic,pb from stock_data_dev.guess_indicators_daily "
        limit_sql = " limit %s ; " %(limit_param);

        sql = search_sql+where_sql+order_by_sql+limit_sql;

        logging.info("select sql : " + sql)
        stock_web_list = self.db.query(sql)

        obj = {
        "code":20000,
        "data": {"draw": 0,"items": stock_web_list,"recordsTotal":len(stock_web_list)}
        }

        logging.info("get data####################")
        logging.info(obj)
        self.write(json.dumps(obj))
