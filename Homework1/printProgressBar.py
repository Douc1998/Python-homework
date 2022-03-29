# -*- coding: utf-8 -*-
# @Time    : 2022/2/22 8:19 PM 
# @Author  : Dou Chen
# @File    : Test2.py

# test2-2: 输出进度条
import time

# 加载进度条函数, 两个参数, totalTime为加载时间（以时间表示速度）、 length为进度条长度
def printProgressBar(totalTime, length):
    for i in range(totalTime + 1):
        # load：表示已加载部分 (不保留小数，format()返回str类型，需要转为int)
        load = format(i * length / totalTime, '.0f')
        # unload: 表示未加载部分
        unload = length - int(load)
        # 进度条百分比计算
        progress = str(format(i * 100 / totalTime, '.0f')) + '%'
        # 判断是否加载到100% 若是在输出 finish! 反之输出百分比
        if i == totalTime:
            print('\r', '[' + '>' * length + ']' + 'finish! ', end='', flush=True)
        else:
            print('\r', '[' + '>' * int(load) + '-' * unload + ']' + progress, end='', flush=True)
        time.sleep(0.1) # 睡眠 => 实现动画效果

if __name__ == '__main__':
    printProgressBar(100, 50)