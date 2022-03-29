# -*- coding: utf-8 -*-
# @Time    : 2022/2/22 8:14 PM 
# @Author  : Dou Chen
# @File    : Test1.py

# test2-1: 输出九九乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print('{}x{}={}'.format(j, i, i * j), end='  ')
    print('\n') # 换行