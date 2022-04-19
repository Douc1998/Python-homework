# -*- coding: utf-8 -*-
# @Time    : 2022/4/18 12:31
# @Author  : Dou Chen
# @File    : 2021202130010窦晨-5.py

# 课外练习3-1:设计一个工具，可以新建图层、增加字段
# 要求:
# 1、指定图层存放的目录
# 2、输入图层名称
# 3、选择图层的类型
# 4、指定模板文件(可选参数)
# 5、能定义投影方式(可选参数)
# 6、增加字段:可以增加任意数量的字段，并定义字段类型、宽 度、字段过滤器等
# 选择图层的类型的方法:
# ✓ 数据类型为“字符串”
# ✓ 过滤器选择“值列表”
# ✓ 值列表增加Polygon、Polyline、Point

import arcpy
import os

# 定义输入参数
file_dir = arcpy.GetParameterAsText(0)  # 输出文件路径
file_name = arcpy.GetParameterAsText(1)  # 输出文件名
file_type = arcpy.GetParameterAsText(2)  # 图层类型
template = arcpy.GetParameterAsText(3)   # 模板文件（optional）
projection = arcpy.GetParameterAsText(4)  # 投影方式（optional）
new_fields = arcpy.GetParameterAsText(5)  # 新增字段

# 工作区
arcpy.env.workspace = file_dir

# 对保证对输出的文件进行复写
arcpy.env.overwriteOutput = True

# 路径全称
file_path = os.path.join(file_dir, file_name) + ".shp"

# 定义投影，如果是自选shp文件，则根据describe来定义投影
if(".shp" in projection):
    projection = arcpy.Describe(projection).spatialReference

# 创建属性表
arcpy.CreateFeatureclass_management(file_dir, file_name, file_type, template, None, None, projection)

# 复制模板文件字段到新建图层，如果template存在 => 将模板文件中的字段加入新建图层
if arcpy.Exists(template):
    fields = arcpy.ListFields(template)
    for field in fields:
        arcpy.AddField_management(file_path, field_name=str(field.name + "_t"), field_type="TEXT", field_length=10)  # 添加字段

# 批量添加字段，如果新增字段不为空，则添加
if new_fields is not '':
    for new_field in new_fields.split(';'):
        is_nullable = True
        # new_field 组成内容： "名称" 备用名称" true true is_nullable length type 0 field_precision
        field_item = new_field.split('')
        # 判断是否可以nullable
        if(field_item[4] == "false"):
            is_nullable = False
        # 新增字段
        arcpy.AddField_management(file_path, file_name=field_item[0], field_type=field_item[6], field_length=field_item[5], is_nullable=is_nullable)