#encoding=utf8
import random
import os
import numpy as np
import string

# win size
WIN_W = 0
WIN_H = 0

# 辅助寻路 参数设置
MAP_INDEX = [0,1,2,3,4,5,6] #索引 对应下面列表的位置
MAP_POSITION = [[5,8],[78,8],[128,8],[5,59],[5,120],[100,100],[88,88]] #地图位置/坐标
BIGMAP_POSITION = [[5,8],[78,8],[128,8],[5,59],[5,120],[100,100],[88,88]] #Tab 地图坐标

# 系统坐标的 图像，crop的坐标位置
POSITION_X1 = 0
POSITION_Y1 = 0
POSITION_X2 = 0
POSITION_Y2 = 0
POSITION_PARAM_PATH = ''
ALL_POSITION_ELEMENT = 'XY:' + string.digits

# 跑路的时间，单位秒
RUN_TIME = 30

#坐标 举例的 阈值
DISTANCE_THRESHOLD = 100

#主窗口名称
MAIN_WIN_NAME = ''

if __name__ == '__main__':

    a = [30,10]
    x,y = a
    print(x,y)
