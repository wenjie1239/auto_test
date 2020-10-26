import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import pdb
import math


class Grid(object):
    def __init__(self, d1, d2, rotate=1, ratio=0.5, mode=0, prob=1.):
        self.d1 = d1
        self.d2 = d2
        self.rotate = rotate
        self.ratio = ratio
        self.mode = mode
        self.st_prob = self.prob = prob

    def set_prob(self, epoch, max_epoch):
        self.prob = self.st_prob * min(1, epoch / max_epoch)

    def __call__(self, img):
        '''

        :param img: imgdata shape=chw
        :return: imgdata
        '''
        if np.random.rand() > self.prob:
            return img
        h = img.size(1)
        w = img.size(2)

        # 1.5 * h, 1.5 * w works fine with the squared images
        # But with rectangular input, the mask might not be able to recover back to the input image shape
        # A square mask with edge length equal to the diagnoal of the input image
        # will be able to cover all the image spot after the rotation. This is also the minimum square.
        hh = math.ceil((math.sqrt(h * h + w * w)))   # 对 整个图片的 对角线长度  向下取整

        d = np.random.randint(self.d1, self.d2)      #  遮挡物 之间的 距离
        # d = self.d

        # maybe use ceil? but i guess no big difference
        self.l = math.ceil(d * self.ratio)           # 遮挡物 的长度

        mask = np.ones((hh, hh), np.float32)         # shape = （hh,hh） 数值都是 1 的 矩阵
        st_h = np.random.randint(d)                  # start_h   int
        st_w = np.random.randint(d)                  # start_w   int

        for i in range(-1, hh // d + 1):             # 取整， 能接受的 遮挡物个数
            s = d * i + st_h                         # s = 尺寸*第几次 + 开始高度
            t = s + self.l
            s = max(min(s, hh), 0)
            t = max(min(t, hh), 0)
            mask[s:t, :] *= 0                        #  将 mask s:t之间的 行 从1改成0
        for i in range(-1, hh // d + 1):
            s = d * i + st_w
            t = s + self.l
            s = max(min(s, hh), 0)
            t = max(min(t, hh), 0)
            mask[:, s:t] *= 0                       # 将  mask s:t之间的列 从1改成0
        #对 遮挡物进行旋转
        r = np.random.randint(self.rotate)          # 旋转
        mask = Image.fromarray(np.uint8(mask))      # 将 xx 转成图片
        mask = mask.rotate(r)                       # 旋转
        mask = np.asarray(mask)                     # 转成numpy

        mask = mask[(hh - h) // 2:(hh - h) // 2 + h, (hh - w) // 2:(hh - w) // 2 + w]    # mask.shape=（hh，hh） 转成 （h，w）

        mask = torch.from_numpy(mask).float().cuda()  #转成 torch
        if self.mode == 1:
            mask = 1 - mask   # 将原本的 0,1 数据转成 1,0 数据. 结果就是 原本条状数据格之间的1都 转成0，通过乘法 达到结构化遮挡物

        mask = mask.expand_as(img)
        img = img * mask

        return img


class GridMask(nn.Module):
    def __init__(self, d1, d2, rotate=1, ratio=0.5, mode=0, prob=1.):
        super(GridMask, self).__init__()
        self.rotate = rotate
        self.ratio = ratio
        self.mode = mode
        self.st_prob = prob
        self.grid = Grid(d1, d2, rotate, ratio, mode, prob)

    def set_prob(self, epoch, max_epoch):
        self.grid.set_prob(epoch, max_epoch)

    def forward(self, x):
        if not self.training:
            return x
        n, c, h, w = x.size()
        y = []
        for i in range(n):
            y.append(self.grid(x[i]))     #调用Grid类的 __call__方法
        y = torch.cat(y).view(n, c, h, w) #
        return y

if __name__ == '__main__':
    '''
    GridMask: 一个数据增强方法。 
    分属于 information dropping：
    核心问题：
    1、过度删除  造成目标信息缺失，成为noisy data
    2、保持连续区域  
    
    给定一个图像保存 比例 ratio
    通过这个比例， 在一定范围内 随机出 重要参数，
    通过参数 生成 固定规则的 正方形格子状 遮挡物
    
    原理：
    通过随机的遮挡 一部分区域。
    1. 有可能遮挡掉输入的一部分重点特征，让神经网络学习其他区域的特征。
    2. 能更加符合显示情况，泛化性好。
    
    
    '''


    d1 = ''
    d2 = ''
    rotate = ''   #旋转
    ratio = ''    #图像信息保留比例
    mode = ''     #默认是 1，不要改
    prob = ''     #概率 用于set_prob函数

    epoch = ''
    maxepoch = ''
    input = ''
    grid = GridMask(d1=d1,d2=d2,rotate=rotate,ratio=ratio,mode=mode,prob=prob)
    grid.set_prob(epoch,maxepoch)    # 得到一个值，当随机数小于这个值，      gridmask  prob * （epoch/maxepoch）
    input = grid(input)              # 调用 MaskGrid 的 forward 函数，传入的是一个批次的数据 NCHW