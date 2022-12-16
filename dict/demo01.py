"""
终端密码输入隐藏
密码加密
"""
import getpass
import hashlib

pwd = getpass.getpass("请输入密码：")
print(pwd)

# hash对象
# hash = hashlib.md5()  # 生成对象
hash = hashlib.md5("myg@#_007".encode())  # 加盐，对密码加密时先拼接加盐字节串，再进行加密
hash.update(pwd.encode())  # 加密
pwd = hash.hexdigest()  # 提取加密后的密码
print(pwd)
