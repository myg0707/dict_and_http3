"""
数据库操作模块
思路：
将数据库操作封装成一个类，将dict_server需要
的数据库操作功能分别写成方法，在dict_server
中实例化对象，需要什么方法直接调用。
"""

import pymysql
import hashlib

SALT = "#A&id_"  # 加盐码


class Database:
    def __init__(self,
                 host="localhost",
                 port=3306,
                 user="myg",
                 password="551054",
                 charset="utf8",
                 database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.database = database
        self.connect_database()  # 初始化的时候就与数据库建立连接

    # 连接数据库
    def connect_database(self):
        self.db = pymysql.connect(host=self.host,
                                  port=self.port,
                                  user=self.user,
                                  password=self.password,
                                  charset=self.charset,
                                  database=self.database)

    # 关闭数据库
    def close(self):
        self.db.close()

    # 创建游标
    def create_cursor(self):
        self.cur = self.db.cursor()

    # 注册操作
    def register(self, name, password):
        sql = "select * from user where name='%s'" % name
        self.cur.execute(sql)
        r = self.cur.fetchone()
        # 如果用户已经存在
        if r:
            return False

        # 密码加密
        hash_ = hashlib.md5((name + SALT).encode())  # 加盐，用name+SALT更容易迷惑别人
        hash_.update(password.encode())  # 算法加密
        password = hash_.hexdigest()  # 获取加密后的密码

        # 无此用户则将用户信息插入数据库表user中
        try:
            sql = "insert into user (name,password) values (%s,%s)"
            self.cur.execute(sql, [name, password])
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    # 登录操作
    def login(self, name, password):
        # 密码加密
        hash_ = hashlib.md5((name + SALT).encode())  # 加盐，用name+SALT更容易迷惑别人
        hash_.update(password.encode())  # 算法加密
        password = hash_.hexdigest()  # 获取加密后的密码

        # 数据库查找
        sql = "select * from user where name=%s and password=%s"
        self.cur.execute(sql, [name, password])
        r = self.cur.fetchone()
        if r:
            return True
        else:
            return False

    # 查单词
    def query(self, word):
        sql = "select exp from words where word='%s'" % word
        self.cur.execute(sql)
        r = self.cur.fetchone()
        if r:
            return r[0]

    # 插入历史记录
    def insert_history(self, name, word):
        sql = "insert into history (name,word) values (%s,%s)"
        try:
            self.cur.execute(sql, [name, word])
            self.db.commit()
        except Exception:
            self.db.rollback()

    # 查询历史记录
    def history(self, name):
        sql = "select name,word,time from history where name='%s' order by time desc limit 10" % name
        self.cur.execute(sql)
        hist = self.cur.fetchmany(10)
        print(hist)
        if hist:
            # words_list = []
            # for item in hist:
            #     info = "%s %-16s %s" % item
            #     words_list.append(info)
            # return "#_#".join(words_list)
            return "#_#".join(["%s %-16s %s" % item for item in hist])
