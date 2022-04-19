# -*- coding: utf-8 -*-
# @Time    : 2022/04/18 14:35
# @Author  : Dou Chen
# @File    : 2021202130010窦晨-6.py

import turtle as t
import arcpy
import numpy as np

# 课外作业:读bount.shp图层中线的坐标，用turtle绘制图形

# 思路：
#  1、describe描述图层，用extent属性可获取shape图层的范围
#  2、读取各行政区的边界数据 => 解析shapefile文件 （arcpy SearchCursor）
#  3、经纬度坐标在canvas上对应的坐标 （坐标的 平移 和 转换）=> 需要获取最大最小经纬度坐标 进行映射 （矩阵计算）
#  4、利用turtle.goto(..., ...) 循环绘制

# 获取 minLng, minLat, maxLng, maxLat 范围数据
def getBoundary(path):
    # 利用describe的extent获取范围
    desc = arcpy.Describe(path)
    extent = desc.extent
    minLng = extent.XMin
    minLat = extent.YMin
    maxLng = extent.XMax
    maxLat = extent.YMax
    return minLng, minLat, maxLng, maxLat

# 获取绘制数据
def getPolygonPoint(file):
    drawingData = []
    # 利用SearchCursor获取shp文件的形状数据
    cursor = arcpy.da.SearchCursor(file, 'SHAPE@')
    for row in cursor:
        polygon = []
        for p in row[0].getPart(0):
            point = [p.X, p.Y]
            polygon.append(point)
        drawingData.append(polygon)
    del cursor
    return drawingData

# 求解坐标变换参数（矩阵形式）
def getParamsMatrix(minLng, minLat, maxLng, maxLat, width, height):
    # 地图上四个端点的坐标，加上一个常数1，用于矩阵运算
    rawLeftBottom, rawLeftTop, rawRightTop, rawRightBottom = [minLng, minLat, 1], [minLng, maxLat, 1], [maxLng, maxLat, 1], [maxLng, minLat, 1]
    # 画布上四个端点的坐标
    newLeftBottom, newLeftTop, newRightTop, newRightBottom = [-width / 2, -height / 2], [-width / 2, height / 2], [width / 2, height / 2], [width / 2, -height / 2]
    # 地图顶点坐标组成矩阵并转置 shape=3x4
    rawLocs = np.mat([rawLeftBottom, rawLeftTop, rawRightTop, rawRightBottom]).T
    # 画布顶点坐标组成矩阵并转置 shape=2x4
    newLocs = np.mat([newLeftBottom, newLeftTop, newRightTop, newRightBottom]).T
    # 矩阵运算求解系数矩阵， shape = 2x4 x 4x3 = 2x3
    paramsMatrix = newLocs.dot(rawLocs.I)
    return paramsMatrix

# 经纬度坐标转为画布中对应的xy坐标，即[Lng, Lat] => [x, y]
def lnglatTransToxy(lng, lat, paramsMatrix):
    # 地图坐标矩阵 shape = 3x1
    rawloc = np.mat([lng, lat, 1]).T
    # 画布坐标矩阵 shape = 2x3 x 3x1 = 2x1
    newloc = paramsMatrix.dot(rawloc)
    # 计算画布坐标
    x, y = newloc[0, 0], newloc[1, 0]
    return x, y

# 绘图函数
def turtleDraw(drawingData, paramsMatrix):
    # 设置窗体大小
    t.setup(width + 20, height + 20)
    # 设置画布大小和背景颜色
    t.screensize(width, height, 'white')
    # 抬起画笔
    t.penup()
    # 加速绘制
    # t.speed(0)
    # 直接绘制完毕显示
    t.tracer(0)
    # 开始绘制
    for item in drawingData:
        for i in range(len(item)):
            # 计算每个点的新坐标，并将画笔移到该位置
            x, y = lnglatTransToxy(item[i][0], item[i][1], paramsMatrix)
            t.goto(x, y)
            # 如果是起点，则需要下笔
            if i == 0:
                t.pendown()
        # 每一个行政区绘制完之后抬笔， 要移动到下一个行政区的起点
        t.penup()
    # 绘制完毕并保留图形
    t.done()

if __name__ == '__main__':
    arcpy.env.workspace = './bount'
    file = 'bount.shp'
    path = './bount/bount.shp'
    # 画布长宽
    width, height = 800.0, 600.0
    # 获取最大最小经纬度
    minLng, minLat, maxLng, maxLat = getBoundary(path)
    # 获取绘制数据
    drawingData = getPolygonPoint(file)
    # 计算变换参数
    paramsMatrix = getParamsMatrix(minLng, minLat, maxLng, maxLat, width, height)
    # 转换坐标并绘制图形
    turtleDraw(drawingData, paramsMatrix)
