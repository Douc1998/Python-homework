# -*- coding: utf-8 -*-
# @Time    : 2022/04/25 14:35
# @Author  : Dou Chen
# @File    : 2021202130010窦晨-7.py

import arcpy
from arcpy import env
import numpy as np

# 课外作业:对whtm.tif图像进行灰度拉伸、图像平滑、图像锐化

# 灰度拉伸
def greyStretch(myraster):
    print "正在进行灰度拉伸..."
    # 利用像素读取保存在数组中
    myarray = arcpy.RasterToNumPyArray(myraster)
    max_val = myarray.max()
    min_val = myarray.min()
    # 灰度值区间
    lowest_val = 0
    highest_val = 255
    print max_val, min_val
    # 计算线性拉伸系数
    a = float((highest_val - lowest_val)) / float((max_val - min_val))
    b = highest_val - a * max_val

    # 获取lower_left
    desc = arcpy.Describe(myraster)
    extent = desc.extent

    # 获取行数列数, cellsize
    desc_band = arcpy.Describe(myraster + "/Band_1")
    rows = desc_band.height
    cols = desc_band.width
    xCellSize = desc_band.meanCellheight
    yCellSize = desc_band.meanCellWidth
    print rows, cols, xCellSize, yCellSize

    # 计算新的灰度值
    myarray1 = arcpy.RasterToNumPyArray(myraster, nodata_to_value=0)
    for i in range(0, rows - 1):
        for j in range(0, cols - 1):
            myarray1[i][j] = myarray1[i][j] * a + b

    print "拉伸后的像素值：", myarray1

    # 数组转为整形
    myarray1 = myarray1.astype(int)
    # 转为array转为raster并保存
    out_raster = arcpy.NumPyArrayToRaster(myarray1, lower_left_corner=extent.lowerLeft, x_cell_size=xCellSize,
                                          y_cell_size=yCellSize)
    out_raster.save("./out_data/whtm_stretch.tif")
    print "拉伸完成"

# 图像卷积 => 平滑
# n 为卷积核大小
def imageSmoothing(myraster, cov_len):
    # 获取lower_left
    desc = arcpy.Describe(myraster)
    extent = desc.extent
    # 读取行数列数，cellsize
    desc_band = arcpy.Describe(myraster + "/Band_1")
    rows = desc_band.height
    cols = desc_band.width
    xCellSize = desc_band.meanCellheight
    yCellSize = desc_band.meanCellWidth
    # 计算新的灰度值
    myarray1 = arcpy.RasterToNumPyArray(myraster, nodata_to_value=0)
    newarray = np.zeros((rows, cols))  # 用于存放结果
    boundary_width = cov_len / 2  # 边界宽度, 如 3/2 = 1, 5 / 2 = 2
    print "读取数据成功，开始处理..."
    for i in range(boundary_width, rows - boundary_width):
        for j in range(boundary_width, cols - boundary_width):
            center = myarray1[i][j]  # 中心位置的值
            # 计算每个中心点周围的梯度倒数
            weight_list = []
            value_list = []
            weight = 0.0  # 权重和
            for m in range(i - boundary_width, i + boundary_width + 1):
                for n in range(j - boundary_width, j + boundary_width + 1):
                    # 储存像素值
                    value_list.append(myarray1[m][n])
                    gradient = 0.0  # 梯度初始化
                    if m == i & n == j:  # 如果是中间值则为 1/2
                        gradient = 1 / 2
                    else:
                        if center - myarray1[m][n] == 0:  # 如果差值为0，则赋值为1
                            gradient = 1.0
                        else:
                            gradient = 1.0 / abs(center - myarray1[m][n])  # 反之取倒数
                        weight += gradient
                    # 获得周围的点的梯度值，用于后续计算
                    weight_list.append(gradient)
            # 计算每个矩阵的值
            for k in range(len(weight_list)):
                if k != 4:  # 只要不是中心值，就归一化处理
                    weight_list[k] = weight_list[k] * 0.5 / weight
            # 计算结果
            newarray[i][j] = np.array(weight_list).dot(np.array(value_list))
            print "第{}行第{}列：原始值为{}，平滑值为{}".format(i, j, myarray1[i][j], newarray[i][j])
    # 计算边缘值，保留原始值
    for i in range(0, rows):
        for j in range(0, cols):
            if newarray[i][j] == 0.0:
                newarray[i][j] = myarray1[i][j]
    # 数组转为整形
    newarray = newarray.astype(int)
    # 转为array转为raster并保存
    out_raster = arcpy.NumPyArrayToRaster(newarray, lower_left_corner=extent.lowerLeft, x_cell_size=xCellSize,
                                          y_cell_size=yCellSize)
    out_raster.save("./out_data/whtm_smooth.tif")
    print "卷积核为{} x {} 的图像平滑完成".format(cov_len, cov_len)

# 图像锐化
# operator => 不同算子作为参数可以动态改变
def imageSharpening(myraster, operator_num):
    # 五种不同算子
    Prewitt_Y = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1])
    Prewitt_X = np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1])
    Sobel_Y = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1])
    Sobel_X = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1])
    Laplace = np.array([0, 1, 0, 1, -4, 1, 0, 1, 0])
    # 初始化为拉普拉斯算子
    operator = Laplace
    operator_name = 'Laplace'

    # 根据用户输入决定用哪个锐化算子
    if operator_num == 1:
        operator = Prewitt_Y
        operator_name = 'Prewitt_Y'
    elif operator_num == 2:
        operator = Prewitt_X
        operator_name = 'Prewitt_X'
    elif operator_num == 3:
        operator = Sobel_Y
        operator_name = 'Sobel_Y'
    elif operator_num == 4:
        operator = Sobel_X
        operator_name = 'Sobel_X'
    elif operator_num == 5:
        operator = Laplace
        operator_name = 'Laplace'

    # 获取lower_left
    desc = arcpy.Describe(myraster)
    extent = desc.extent
    # 读取行数列数，cellsize
    desc_band = arcpy.Describe(myraster + "/Band_1")
    rows = desc_band.height
    cols = desc_band.width
    xCellSize = desc_band.meanCellheight
    yCellSize = desc_band.meanCellWidth
    # 计算新的灰度值
    myarray1 = arcpy.RasterToNumPyArray(myraster, nodata_to_value=0)
    newarray = np.zeros((rows, cols))  # 用于存放结果
    boundary_width = 3 / 2  # 边界宽度, 如 3/2 = 1
    print "当前进行{}算子的图像锐化，开始处理...".format(operator_name)
    for i in range(boundary_width, rows - boundary_width):
        for j in range(boundary_width, cols - boundary_width):
            # 存储每个中心点及其周围的灰度值
            value_list = []
            for m in range(i - boundary_width, i + boundary_width + 1):
                for n in range(j - boundary_width, j + boundary_width + 1):
                    # 储存像素值
                    value_list.append(myarray1[m][n])
            # 计算中心的锐化值
            newarray[i][j] = abs(np.array(operator).dot(np.array(value_list)))
            print "第{}行第{}列：原始值为{}，锐化值为{}".format(i, j, myarray1[i][j], newarray[i][j])
    # 计算边缘值，保留原始值
    for i in range(0, rows):
        for j in range(0, cols):
            if newarray[i][j] == 0.0:
                newarray[i][j] = myarray1[i][j]
    # 数组转为整形
    newarray = newarray.astype(int)
    # 转为array转为raster并保存
    out_raster = arcpy.NumPyArrayToRaster(newarray, lower_left_corner=extent.lowerLeft, x_cell_size=xCellSize,
                                          y_cell_size=yCellSize)
    out_raster.save("./out_data/whtm_sharpening_" + operator_name + ".tif")
    print "锐化算子为{}的图像锐化完成".format(operator_name)



if __name__ == '__main__':
    # 通过许可管理器检索许可
    arcpy.CheckOutExtension("Spatial")
    # 工作区极其相关设置
    env.workspace = "./in_data/"
    env.overwriteOutput = True
    myraster = "whtm.tif"

    # 灰度值线性拉伸
    greyStretch(myraster)

    # 图像平滑，第二个参数为卷积核大小
    imageSmoothing(myraster, 3)

    # 图像锐化，第二个参数为锐化算子编号
    # operator_num = input('请选择锐化算子: \n 1.Prewitt_Y \n 2.Prewitt_Y \n 3.Sobel_Y \n 4.Sobel_Y \n 5.Laplace \n 请输入数字编号:')
    # imageSharpening(myraster, operator_num)

    # 每种算子都处理一遍
    for operator_num in range(1, 6):
        imageSharpening(myraster, operator_num)
