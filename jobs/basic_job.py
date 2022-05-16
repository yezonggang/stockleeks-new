#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import sys
from os.path import dirname,abspath
project_path = dirname(dirname(abspath(__file__)))
#__file__用于获取文件的路径，abspath(__file__)获得绝对路径；
#dirname()用于获取上级目录，两个dirname（）相当于获取了当前文件的上级的上级即示例中project2
sys.path.append(project_path)
import libs.common as common
# import MySQLdb
import pymysql

# 创建新数据库。
def create_new_database():
    with pymysql.connect(host=common.MYSQL_HOST, user=common.MYSQL_USER, password=common.MYSQL_PWD, database="mysql", charset="utf8") as db:
        try:
            create_sql = " CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8 COLLATE utf8_general_ci " % common.MYSQL_DB
            print(create_sql)

            db.autocommit(True)
            db.cursor().execute(create_sql)
        except Exception as e:
            print("error CREATE DATABASE :", e)


# main函数入口
if __name__ == '__main__':

    # 检查，如果执行 select 1 失败，说明数据库不存在，然后创建一个新的数据库。
    try:
        with pymysql.connect(host=common.MYSQL_HOST, user=common.MYSQL_USER, password=common.MYSQL_PWD, database=common.MYSQL_DB,
                             charset="utf8") as db:
            db.autocommit(True)
            db.cursor().execute(" select 1 ")
            print("########### db exists ###########")
    except Exception as e:
        print("check  MYSQL_DB error and create new one :", e)
        # 检查数据库失败，
        create_new_database()
    # 执行数据初始化。
