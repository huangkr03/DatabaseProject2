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
    con2 = pool.get_conn()
    con3 = pool.get_conn()
    con4 = pool.get_conn()
    con1 = pool.get_conn()
    pool.status()
    con1.close()
    pool.status()
    con2.close()
    pool.status()
    con3.close()
    pool.status()
    con4.close()
    pool.status()

    pool.pool.close()
