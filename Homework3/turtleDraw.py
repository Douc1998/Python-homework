# -*- coding: utf-8 -*-
# @Time    : 2022/3/8 3:42 PM 
# @Author  : Dou Chen
# @File    : 2021202130010窦晨-3.py

# 思路：
#  1、利用ArcGIS获取湖北省Json文件
#  2、读取各行政区的边界数据 => 解析Json文件 （json库 + 字典解析和存储）
#  3、经纬度坐标在canvas上对应的坐标 （坐标的 平移 和 转换）=> 需要获取最大最小经纬度坐标 进行映射 （矩阵计算）
#  4、利用turtle.goto(..., ...) 循环绘制

import json
import numpy as np
import turtle as t


# 初始化json数据中最大经纬度坐标
minLat, minLng, maxLat, maxLng = 999, 999, -999, -999
# 画布长宽
width, height = 800.0, 600.0


# 读取json数据并转换为相应的绘图数据
# 即：[(polygon0):[[x, x], [x, x], ...]], (polygon1):[[x, x], [x, x], [x, x], ...], (polygon2):[...]...]
def transformJsonToDrawingData(filepath):
    drawingData = []
    with open(filepath, 'r') as fp:
        jsonData = json.load(fp)
        # 解析Json数据, features下存有所有的形状数据
        features = jsonData['features']
        # 对每一个ploygon进行数据解析和存储
        for item in features:
            # 获取每个polygon的形状数据 即所有边界点坐标
            paths = item['geometry']['paths'][0]
            # 存储在drawingData数组中
            drawingData.append(paths)
    fp.close()
    # 遍历数组 获取经纬度最大最小值
    for item in drawingData:
        for loc in item:
            lat = float(loc[0])
            lng = float(loc[1])
            global minLat, minLng, maxLat, maxLng  # 全局变量
            # 经纬度最大最小值修改
            if lat > maxLat:
                maxLat = lat
            if lat < minLat:
                minLat = lat
            if lng > maxLng:
                maxLng = lng
            if lng < minLng:
                minLng = lng
    # print(maxLat, maxLng, minLat, minLng)
    return drawingData


# 求解坐标变换参数 (矩阵形式)
def getParamsMatrix():
    global minLat, minLng, maxLat, maxLng, width, height
    # 地图上四个端点的坐标，加上一个常数1 用于矩阵运算
    rawLeftBottom, rawLeftTop, rawRightTop, rawRightBottom = [minLat, minLng, 1], [minLat, maxLng, 1], [maxLat, maxLng, 1], [maxLat, minLng, 1]
    # 画布上四个端点的坐标
    newLeftBottom, newLeftTop, newRightTop, newRightBottom = [-width / 2, -height / 2], [-width / 2, height / 2], [width / 2, height / 2], [width / 2, -height / 2]
    # 地图顶点坐标组成矩阵并转置 shape = 3x4
    rawLocs = np.mat([rawLeftBottom, rawLeftTop, rawRightTop, rawRightBottom]).T
    # 画布顶点坐标组成矩阵并转置 shape = 2x4
    newLocs = np.mat([newLeftBottom, newLeftTop, newRightTop, newRightBottom]).T
    # 矩阵运算求解 系数矩阵，shape = 2x4 x 4x3 = 2x3
    paramsMatrix = newLocs.dot(rawLocs.I)
    return paramsMatrix


#  经纬度坐标转为画布中对应的xy坐标 即 [lat, lon] => [x ,y]
def latlngTransToxy(lat, lng, paramsMatrix):
    # 地图坐标矩阵 shape = 3x1
    rawloc = np.mat([lat, lng, 1]).T
    # 画布坐标矩阵 shape = 2x3 x 3x1 = 2x1
    newloc = paramsMatrix.dot(rawloc)
    x, y = newloc[0, 0], newloc[1, 0]
    # 返回画布坐标
    return x, y


# 绘图函数
def trutleDraw(drawingData, paramsMatrix):
    t.setup(width + 20, height + 20)  # 设置窗体大小
    t.screensize(width, height, 'white')  # 设置画布大小和背景颜色
    t.penup()  # 抬起画笔
    t.speed(0)  # 加快绘制速度
    # t.tracer(0)  # 直接绘制完毕显示
    for item in drawingData:
        for i in range(len(item)):
            # 计算出每个点的新坐标，并将画笔移到该位置
            x, y = latlngTransToxy(item[i][0], item[i][1], paramsMatrix)
            t.goto(x, y)
            # 如果是起点，则需要下笔
            if i == 0:
                t.pendown()
        # 每一个行政区绘制完之后抬笔，要移动到下一个行政区的起点
        t.penup()
    # 绘制完毕并保留图形
    t.done()

if __name__ == '__main__':
    filepath = './data/hbbount_to_json.json'
    # 获取绘制数据
    drawingData = transformJsonToDrawingData(filepath)
    # 计算变换参数
    paramsMatrix = getParamsMatrix()
    # 转换坐标并绘制图形
    trutleDraw(drawingData, paramsMatrix)