# -*- coding=utf-8 -*-
# @Time : 2019/7/3 17:33 
# @Author : piller
# @File : bloom_filter.py 
# @Software: PyCharm

import redis
from hashlib import md5


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        # 5，7，11，13，31，37，61
        self.seed = seed
    # 调用
    # value ：经过md5加密后的字符串
    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self, host='localhost', port=6379, db=0, blockNum=1, key='bloomfilter'):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param blockNum: one blockNum for about 90,000,000; if you have more strings for filtering, increase it.
        :param key: the key's name in Redis
        """
        self.server = redis.Redis(host=host, port=port)
        # <<表示二进制向左移动位数，比如2<<2,2的二进制表示000010，向左移2位，就是001000，就是十进制的8
        self.bit_size = 1 << 29  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            # hashfunc 列表添加 SimpleHash函数 ，
            self.hashfunc.append(SimpleHash(self.bit_size, seed))
    # str_input 网站url的字符串
    def isContains(self, str_input):
        print(type(str_input))
        print(111111111111)
        # 判断是否有url
        if not str_input:
            print(2222222222222)
            # 没有返回 false
            return False
        # 创建md5对象
        m5 = md5()
        print(3333333333)
        # 编码格式
        m5.update(str_input.encode())

        print(4444444)
        # 加密
        str_input = m5.hexdigest()
        print(5555555)
        ret = True
        print(66666666)
        # key ： redis的名字
        #       name = key + str（ 切割 加密后的字符串转换成16进制后 拼接blockNum ）
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        print(7777777)
        # 循环列表
        for f in self.hashfunc:
            print(888888)
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        print(999999)
        return ret

    # redis中没有url 走这个函数
    def insert(self, str_input):
        m5 = md5()
        m5.update(str_input.encode())
        str_input = m5.hexdigest()
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)

def func1(url):
    print("执行不拢")
    bf = BloomFilter()
    if bf.isContains(url):  # 判断字符串是否存在
        print("存在")
        return 0
    else:
        print('not exists!')
        bf.insert(url)
        return 1


# if __name__ == '__main__':
#     """ 第一次运行时会显示 not exists!，之后再运行会显示 exists! """
#     bf = BloomFilter()
#     if bf.isContains('http://www.bai.com'):  # 判断字符串是否存在
#         print('exists!')
#     else:
#         print('not exists!')
#         bf.insert('http://www.bai.com')
