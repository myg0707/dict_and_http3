"""
可以接收客户端什么样的数据访问
"""
from views import *

# 路由列表
urls = [
    ("/time", show_time),
    ("/guonei", guonei),
    ("/guoji", guoji)
]
