# _*_ coding : utf-8 _*_
# @Time : 2022/5/20 10:54
# @Author : 黄柯睿
# @File : TestDBPool
# @Project : index.html

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pprint import pprint
from socketserver import ThreadingMixIn
from dbutils.pooled_db import PooledDB
import psycopg2 as pg
from psycopg2.extensions import *

from Project2.Advance import Advance1


class Pool:
    def __init__(self):
        self.pool = PooledDB(
            creator=pg,
            mincached=1,
            maxcached=20,
            blocking=True,
            port=5432,
            database='project_2',
            user='postgres',
            password='123456',
            host='localhost',
            ping=0
        )

    def get_conn(self):
        con = self.pool.connection()
        self.status()
        return con

    def status(self):
        print('池子里目前有', len(self.pool._idle_cache))


if __name__ == '__main__':
    pool = Pool()
    con1 = pool.get_conn()
    advance = Advance1(pool)
    result = advance.get_enterprise_order('Netease')
    for i in result:
        for j in i:
            print(j)
    js = {}
    if result:
        js.setdefault('enterprise', 'Netease')
        js.setdefault('country', result[0][2])
        js.setdefault('city', result[0][3])
        js.setdefault('industry', result[0][4])
        js.setdefault('orders', [])
        for i in result:
            a = {}
            a.setdefault('product', i[0])
            a.setdefault('quantity', i[1])
            a.setdefault('price', int(i[5]))
            a.setdefault('total_price', int(i[6]))
            js['orders'].append(a)
    # pprint(j)
    pprint(json.dumps(js))

    pool.pool.close()
