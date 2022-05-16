#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import requests  # requests模块需要使用 pip 命令安装
import libs.common as common
import datetime


def get_ip():
    headers = {
        'cache-control': 'no-cache',
    }

    response = requests.get('http://ip.cip.cc')

    print('ip address:')
    print(response.text.strip('\n'))

    return response.text.strip('\n')


def restart_stock():
    server_ip = get_ip()

    url = "http://" + server_ip + ":7777/job/stock888_restart/build?token=stock369"
    print(url)
    response = requests.get(url, timeout=5)

    print('restart stock:')
    print(response.text)


# 检查job是否执行成功，不成功就重启服务重新执行
def check_job():
    tmp_datetime_show = datetime.datetime.now()  # 修改成默认是当日执行 + datetime.timedelta()
    datetime_int = tmp_datetime_show.strftime("%Y%m%d")

    sql_count = """
    SELECT count(1) FROM stock_data.stock_zh_ah_name WHERE `date` = %s and `latest_price` > 0
    """
    total_count = common.select_count(sql_count, params=[datetime_int])
    print("total count :", total_count)

    sql_guess_count = """
        SELECT count(1) FROM stock_data.guess_indicators_daily WHERE `date` = %s and `latest_price` > 0
        """
    guess_count = common.select_count(sql_guess_count, params=[datetime_int])
    print("guess count :", guess_count)

    if total_count > 0 and guess_count < total_count:
        tmp_hour_int = int(tmp_datetime_show.strftime("%H"))
        if tmp_hour_int < 18:
            print("not yet")
        else:
            print("starting restart stock")
            restart_stock()
            print("start done")
    else:
        print("do not have to do this")


# main函数入口
if __name__ == '__main__':
    check_job()
