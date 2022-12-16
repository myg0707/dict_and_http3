"""
dict 客户端
功能：根据用户输入，发送请求，得到结果
结构：一级界面-->注册，登录，退出
    二级界面-->查单词，历史记录，注销
"""
from socket import *
import sys
from getpass import getpass

# 全局变量
HOST = "192.168.74.133"
PORT = 8000
ADDR = (HOST, PORT)
# tcp套接字
s = socket()
s.connect(ADDR)


def do_query(name):
    while True:
        word = input("要查询的单词：")
        if word == "##":  # 输入特殊字符结束查询
            break
        msg = "Q %s %s" % (name, word)
        s.send(msg.encode())
        # 得到查询结果
        data = s.recv(2048).decode()
        print(data)


def do_history(name):
    msg = "H %s" % name
    s.send(msg.encode())
    data = s.recv(2048).decode()
    if data == "Fail":
        print("没有查询记录：")
    else:
        info = data.split("#_#")
        for item in info:
            print(item)


def login(name):
    # 二级界面
    while True:
        print("=" * 28, "二级界面", "=" * 28)
        print(" " * 14, "1. 查单词    2. 历史记录   3. 注销")
        print("=" * 66)
        select_num = input("请选择：")
        if select_num == "1":
            do_query(name)
        elif select_num == "2":
            do_history(name)
        elif select_num == "3":
            return
        else:
            print("输入错误！")


def do_register():
    while True:
        name = input("Username:")
        password = getpass()
        password1 = getpass("Password again:")
        if password != password1:
            print("两次密码不一致，请重新输入。")
            continue
        if " " in name or " " in password:
            print("用户名和密码不能有空格。")
            continue
        msg = "R %s %s" % (name, password)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == "OK":
            print("注册成功")
            login(name)
        else:
            print("注册失败")
        return


def do_login():
    name = input("Username:")
    password = getpass()
    msg = "L %s %s" % (name, password)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == "OK":
        print("登录成功")
        login(name)
    else:
        print("登录失败")


def main():
    # 一级界面
    while True:
        print("=" * 28, "一级界面", "=" * 28)
        print(" " * 17, "1. 注册    2. 登录   3. 退出")
        print("=" * 66)
        select_num = input("请选择：")
        if select_num == "1":
            do_register()
        elif select_num == "2":
            do_login()
        elif select_num == "3":
            s.send(b"E")
            sys.exit("谢谢使用")
        else:
            print("输入错误！")


main()
