#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pymysql

ip = '127.0.0.1'
database ='db_xdag'
acc = 'root'
pw ='10300'
port = 3306






class SqlModel:
    def get_info_by_sql_data(self,sql_str,data):
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            cursor.execute(sql_str,data)
            record = cursor.fetchall()
            cursor.close()
            conn.close()
            return record
        except:
            #conn.rollback()
            pass
    def get_info_by_sql(self,sql_str):
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            cursor.execute(sql_str)
            record = cursor.fetchall()
            cursor.close()
            conn.close()
            return record
        except:
            #conn.rollback()
            pass
    def rows_info_by_sql(self, sql_str):#rows_info_by_sql
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            rows = cursor.execute(sql_str)
            #conn.commit()
            #rows =  cur.rowcount()
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            print(e)
    def rows_info_by_data(self, sql_str,data):#rows_info_by_sql
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            rows = cursor.execute(sql_str,data)
            #conn.commit()
            #rows =  cur.rowcount()
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            print(e)
    def mysql_com(self,sql_str):
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            try:
                # conn = pymysql.Connect(host=ip, port=3309, user=acc, passwd=pw, db=database, charset='utf8')
                # print("连接成功！！")
                cursor = conn.cursor()
                # print(sql_str)
                cursor.execute(sql_str)
                conn.commit()
                cursor.close()
                conn.close()
            except:
                conn.rollback()
        except Exception as e:
            print(e)
    def mysql_com_data(self, sql_str,data):
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            try:
                        # conn = pymysql.Connect(host=ip, port=3309, user=acc, passwd=pw, db=database, charset='utf8')
                        # print("连接成功！！")
                 cursor = conn.cursor()
                        # print(sql_str)
                 cursor.execute(sql_str,data)
                 conn.commit()
                 cursor.close()
                 conn.close()
            except:
                 conn.rollback()
        except Exception as e:
            print(e)


            #print(e)

    def put_info_by_sql_many(slef,sql_str,datalist):
        #print(sql_str,datalist)
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            cursor.executemany(sql_str, datalist)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)


    def put_info_by_sql(slef,sql_str,data):#put_info_by_sql
        try:
            conn = pymysql.Connect(host=ip, port=port, user=acc, passwd=pw, db=database, charset='utf8')
            cursor = conn.cursor()
            cursor.execute(sql_str, data)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)
