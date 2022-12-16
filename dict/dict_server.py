"""
dict 服务端
功能：业务逻辑处理
模型：多进程tcp并发
"""
from socket import *
from multiprocessing import Process
import signal, sys
from mysql import Database

# 全局变量
HOST = "0.0.0.0"
PORT = 8000
ADDR = (HOST, PORT)
# 建立数据库对象，在全局位置建立连接，每个子进程都拥有
db = Database(database="dict")


# 服务端注册处理
def do_register(c, data):
    tmp = data.split(" ")
    name = tmp[1]
    password = tmp[2]
    if db.register(name, password):
        c.send(b"OK")
    else:
        c.send(b"Fail")


def do_login(c, data):
    tmp = data.split(" ")
    name = tmp[1]
    password = tmp[2]
    if db.login(name, password):
        c.send(b"OK")
    else:
        c.send(b"Fail")


def do_query(c, data):
    tmp = data.split(" ")
    name = tmp[1]
    word = tmp[2]

    # 没有找到返回None，找到返回单词解释
    mean = db.query(word)
    if not mean:
        c.send("没有找到该单词".encode())
    else:
        # 插入历史记录，（写在此处时有这个单词才插入历史记录，在if外面表示即使没有查询到单词也插入记录）
        db.insert_history(name, word)
        msg = "%s : %s" % (word, mean)
        c.send(msg.encode())


def do_history(c, data):
    tmp = data.split(" ")
    name = tmp[1]

    # 查询历史记录
    words = db.history(name)
    if not words:
        c.send("Fail".encode())
    else:
        c.send(words.encode())


# 接收客户端请求，分配处理函数
def request(c):
    db.create_cursor()  # 每个子进程单独生成游标，相互之间没有影响
    # 循环接收请求
    while True:
        try:
            data = c.recv(1024).decode()
        except:
            break
        if not data or data[0] == "E":
            break
        elif data[0] == "R":
            do_register(c, data)
        elif data[0] == "L":
            do_login(c, data)
        elif data[0] == "Q":
            do_query(c, data)
        elif data[0] == "H":
            do_history(c, data)
    sys.exit()  # 对应子进程退出


# 搭建网络
def main():
    # 创建tcp套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)
    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    # 循环等待客户连接
    print("Listen the port 8888")
    while True:
        try:
            c, addr = s.accept()
            print("Connect from ", addr)
        except KeyboardInterrupt:
            s.close()
            db.close()
            sys.exit("服务端退出")
        except Exception as e:
            print(e)
            continue

        # 为客户端创建子进程
        p = Process(target=request, args=(c,))
        p.daemon = True
        p.start()


if __name__ == "__main__":
    main()
