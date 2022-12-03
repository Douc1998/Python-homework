# -*- coding: utf-8 -*-
# @Time    : 2022/3/22 16:26 
# @Author  : Dou Chen
# @File    : 2021202130010窦晨-4.py

from urllib.request import urlopen
from urllib.parse import quote
import json
import string

# Title:
# 寻找武汉市中学(或小学)周围500米(或其他)内的网吧， 要求:提交代码py文件及运行结果文件(txt),txt文件格式如下
# 1，XXX小学 
# 1-1，XXX网吧 
# 1-2， XXX网吧 
# 2，XXX小学 
# 2-1，XXX网吧 
# 2-2， XXX网吧

# 爬取结果
def get_json(url):
    url = quote(url, safe=string.printable)  # 解析URL地址
    url_file = urlopen(url)
    json_file = url_file.read()
    json_result = json.loads(json_file)  # 获取json数据
    return json_result

# 分割矩形
def split_area(bound, bound_list):
    row_num = 2  # 按照2 X 2进行分割
    step_lat = (bound[3] - bound[1]) / row_num
    step_lon = (bound[2] - bound[0]) / row_num
    for i in range(0, row_num):
        for j in range(0, row_num):
            bound_temp = []
            bound_temp.append(bound[0] + step_lon * j)
            bound_temp.append(bound[1] + step_lat * i)
            bound_temp.append(bound[0] + step_lon * (j + 1))
            bound_temp.append(bound[1] + step_lat * (i + 1))
            bound_list.append(bound_temp)
    return bound_list

# 动态分割
def Dynamic_segmentation(bound_list):
    new_bound_list = []
    old_length = len(bound_list)
    split_index = []
    # 如果是第一次分割
    if old_length == 1:
        split_area(bound_list[0], new_bound_list)  # 分割结果加入到bound_list中
    else:
        for i in range(old_length):
            if (i + 1) % 3 != 0:  # 不能整出3，则不分割，丢进新的list中，并在old_list中删除
                new_bound_list.append(bound_list[i])
            else:
                split_index.append(i)
        for index in split_index:  # 将需要分割的进行分割，分割结果插入到新的bound_list中
            split_area(bound_list[index], new_bound_list)
    # 如果长度大于50，则不继续分割，并返回new_bound_list
    if len(new_bound_list) >= 50:
        return new_bound_list
    else:     # 反之继续递归
        result = Dynamic_segmentation(new_bound_list)
        return result

# 多边形poi搜索
# params: 左下右上边界点数组bound， 存储result的数组
def get_polygon_data(bound, polygon_result):
    ak = 'xxxxx'  # 你的高德地图API key
    key_word = '武汉'
    page_size = 20
    page_num = 1
    poi_type = 141202  # 根据poi码表对应 "中学"
    url = 'https://restapi.amap.com/v5/place/polygon?keywords=' + str(key_word) + '&' + 'types=' + str(poi_type) + '&' \
          + 'show_fields=name,location&output=json' + '&' + 'polygon=' + str(bound[0]) + ',' + str(bound[1]) + '|' \
          + str(bound[2]) + ',' + str(bound[3]) + '&' + 'page_size=' + str(page_size) + '&' + 'page_num=' + str(page_num) \
          + '&' + 'key=' + str(ak)
    print(url)
    json_result = get_json(url)
    print('Request data ...')
    print(json_result)
    for text in json_result['pois']:
        poi_list = []
        poi_list.append(text['name'])
        poi_list.append(text['location'])
        polygon_result.append(poi_list)

# 查找网吧
def look_for_Internet_Bar(center, radius, around_result):
    name = center[0]
    location = center[1].split(',')
    ak = 'xxxxx'  # 你的高德地图API key
    page_size = 20
    page_num = 2
    poi_type = '080308'  # 根据poi码表对应 "网吧"
    url = 'https://restapi.amap.com/v5/place/around?' + 'types=' + str(poi_type) + '&' \
          + 'show_fields=name,location&output=json' + '&' + 'location=' + str(location[0]) + ',' + str(location[1]) \
          + '&' + 'radius=' + str(radius) + 'page_size=' + str(page_size) + '&' + 'page_num=' + str(page_num) + '&' + 'key=' + str(ak)
    print(url)
    # 请求数据
    json_result = get_json(url)
    print('Request data ...')
    print(json_result)
    # 存储网吧名称
    center_bar_list = []
    for text in json_result['pois']:
        center_bar_list.append(text['name'])
    around_result[name] = center_bar_list

def write_file(obj, write_path):
    # 写入文件
    w_file = open(write_path, 'w')
    count = 1
    # 遍历写入
    for key in obj.keys():
        w_file.write(str(count) + '.' + str(key) + '\n')
        for i in range(len(obj[key])):
            w_file.write('{}-{}.{}\n'.format(count, i + 1, obj[key][i]))
        count += 1
        w_file.write('\n')
    w_file.close()
    print('write file ok !')

if __name__ == '__main__':

    # 武汉市边界
    wuhan_bound = [113.696570, 29.971688, 115.077072, 31.363301]
    bound_origin_list = []
    bound_origin_list.append(wuhan_bound)

    # 动态分割
    bound_list = Dynamic_segmentation(bound_origin_list)
    print('Dynamic segmentation result\'s length is', len(bound_list))

    # 找到范围内的所有中学
    polygon_result = []
    for item in bound_list:
        get_polygon_data(item, polygon_result)
    print('The num of wuhan middle school is:', len(polygon_result))
    print('middle school result is:')
    for item in polygon_result:
        print(item)

    around_list = {}  # 创建字典
    print('...Seeking for Internet Bar')
    for item in polygon_result:
        look_for_Internet_Bar(item, 500, around_list)
    print('Internet Bar results are:')
    print(around_list)

    write_path = './result.txt'
    write_file(around_list, write_path)



