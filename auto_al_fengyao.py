#encoding=utf8

import random
import time
from pymouse import PyMouse
from pykeyboard import PyKeyboard

from .ScreenViewer import ScreenViewer
from .captcha_finally.status_position import RecognizePosition
from .al_fig import *

class AutoMoney():

    def __init__(self,wnname,sleep_time = 10):
        self.status = 0
        self.sv = ScreenViewer()
        self.sv.GetHWND(wnname)
        self.left_x,self.left_y,_ = self.sv.GetWindowPos()
        self.sleep_time = sleep_time
        self.now_img = 0
        self.recognize_position = RecognizePosition()
        self.map_index = 0
        self.k = PyKeyboard()
        self.m = PyMouse()


    def screen_img_data(self):
        return self.sv.GetScreenImg()

    def map_position_distance(self,now_position):
        '''
        :param true_position:  now status position
        :return:  distance of  the label position and now status position
        '''
        map_index_position = MAP_POSITION[self.map_index]
        return (map_index_position[0] - now_position[0]) ** 2 + (map_index_position[1] - now_position[1]) ** 2

    def change_map_index(self):
        #先 随机 获取前进的 point  index
        random_step = random.randint(1,3)
        #人物 走到 一个位置
        self.map_index = (self.map_index + random_step) % len(MAP_INDEX)

    def move_big_map(self):
        # 切换到 当前窗口 现在 pass

        #按下 Tab 键，打开大地图   tap_key 是按一下按键 press_key是 按住按键
        self.k.tap_key(self.k.tab_key)
        #点击 窗口的 位置
        win_x,win_y = BIGMAP_POSITION[self.map_index]
        win_x = win_x + self.left_x
        win_y = win_y + self.left_y
        self.m.move(win_x,win_y)
        self.m.click(win_x,win_y)
        #在按一下 tab键 关闭 大地图
        self.k.tap_key(self.k.tab_key)
        self.status = 1


    def route_plan(self):
        #获取 xy坐标图像的位置  hwc
        position_img = self.now_img[POSITION_Y1:POSITION_Y2,POSITION_X1:POSITION_X2,:]
        position_data = self.recognize_position.return_position(position_img)   # None or [x,y]
        if position_data:
            distince = self.map_position_distance(position_data)
            if distince <= 50:
                # 需要将 self.map_index 换成下一个，然后在 寻路。
                self.change_map_index()
                self.move_big_map()
            else:
                self.move_big_map()
        else:
            self.move_big_map()

    def run(self):
        while self.status == 0:
            self.now_img = self.screen_img_data()
            boxes = []
            if boxes:
                pass
            else:
                self.route_plan()
                time.sleep(30)
                # 点击人物中心 ，让人物停止移动
                self.m.click(self.left_x + WIN_W/2,self.left_y + WIN_H/2)
                self.status = 0






a = '''
加载0的数据 -> 1   -> 2 -> 3 -> 1
1/2/6 需要 智能训练。


0、任务所在地图(AL,ZZ)

1、人物状态  #自己定义  status

self.status = 0
截图 -> 输出boxes -> 不存在 -> 自动寻路 -> self.status = 1 -> 点击屏幕，人物静止 -> self.status = 0
                  -> 判断是否存在需要的目标 -> 不存在 -> self.status = 0
                                            -> 点击 进入战斗 -> self.status = 2 -> 判断战斗是否结束 -> 已经结束 self.status = 0
                                                                                                    -> 没有结束 self.status = 2 
                                                                                                    -> 掉线   self.status = 3  -> 人工处理  -> self.status = 0
                                                                                                    -> 断网   self.status = 4  -> 人工处理  -> self.status = 0
自动寻路：
1. 判断自己的坐标位置 
2. 通过这个坐标， 抽取 下一个坐标的位置 self.next_position
3. 点击下一个坐标 位置的操作 （1、切换到当前窗口 2、 按下Tab键，打开大地图  3、 点击self.next_position 对应的坐标 4、再按tab 关闭大地图 ）                                                                                                    
                                                                                                
                                                                                                    

1.1 静止 （0）
1.2 寻路 （1）
1.3 战斗 （2）

1.4 掉线 (3) 别人掉线 请等待 
1.5 断网 （4） 自己掉线是蓝屏/请等待  ?


2、侦测 是否存在 目标   (训练神经网络 识别目标)
2.1 yolov4 训练识别 目标 输出目标位置/类别  M,5(cls,x1,y1,x2,y2)
2.2 通过设定的 cls 和 目标框中的 颜色 进行对比, 符合条件 则 输出 N,4 [x1,y1,x2,y2], 否则 输出 [] 

3、点击目标，进入状态  （可能是 只需要点击固定地方 多次）
3.1 点击目标输出框的 中心点
3.2 判断 目标 存不存在
3.3 不存在 点击 ”关闭“，存在点击”继续“，进入战斗

4、战斗状态   （点击固定位置）
重置 “自动”

5、人物状态
5.1 查看 红蓝 状态 （自动填满）

6 寻路系统：   （需要 训练网络识别 人物所在 位置）
6.0 将地图分为 X大块
6.1 通过 坐标, 判断人物所在X大块中的位置，输出一个地图点击的位置 map_click_position [x1,y1,x2,y2]。
6.2 按“Tab” 键，点击 map_click_position 位置。

7、意外情况 转到1.
7.1 掉线 （个别掉线）
7.2 断网 （所有都掉线）

8、获取窗口截图
获取窗口 handle， 通过handle 获取窗口名称。
通过名称，获取handdle，然后截图。



'''



