"""
HTTPServer部分的主程序

获取http请求
解析http请求
将请求发送给WebFrame
从WebFrame接收反馈数据
将数据组织为Response格式发送给客户端
"""
import json
from socket import *
from threading import Thread
import sys
from config import *
import re

ADDR = (HOST, PORT)


# 创建和webframe交互的套接字
def connect_frame(env):
    s = socket()
    frame_addr = (frame_ip, frame_port)
    try:
        s.connect(frame_addr)
    except Exception as e:
        print(e)
        sys.exit()
    # 将字典转换为json
    data = json.dumps(env)
    # 将解析后的请求发送给webframe
    s.send(data.encode())
    # 接收来自webframe的数据
    try:
        data = s.recv(4096 * 100).decode()
    except:
        return
    if not data:
        return
    return json.loads(data)


class HTTPServer:
    def __init__(self):
        self.address = ADDR
        self.create_socket()  # 和浏览器交互
        self.bind()

    # 创建套接字
    def create_socket(self):
        self.socket = socket()
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)

    # 绑定地址
    def bind(self):
        self.socket.bind(self.address)
        self.ip = self.address[0]
        self.port = self.address[1]

    # 接收请求
    def handle(self, connfd):
        while True:
            # 获取HTTP请求
            request = connfd.recv(4096).decode()
            # print(request)
            pattern = r"(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
            try:
                env = re.match(pattern, request).groupdict()
            except:
                # 客户端断开
                break
            else:
                data = connect_frame(env)
                if not data:
                    break
                self.response(connfd, data)
                break
        connfd.close()

    # 给浏览器发送数据
    def response(self, connfd, data):
        print(data)
        if data["status"] == "200":
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "\r\n"
            response_body = data["data"]
        elif data["status"] == "404":
            response_headers = "HTTP/1.1 404 NOT OK\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "\r\n"
            response_body = data["data"]
        response_data = response_headers + response_body
        connfd.send(response_data.encode())

    # 启动服务端
    def server_forever(self):
        self.socket.listen(5)
        print("Listen the port %d" % self.port)
        while True:
            connfd, addr = self.socket.accept()
            print("Connect from ", addr)
            client = Thread(target=self.handle, args=(connfd,))
            client.daemon = True
            client.start()


if __name__ == '__main__':
    httpd = HTTPServer()
    httpd.server_forever()
