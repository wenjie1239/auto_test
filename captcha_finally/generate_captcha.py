#encoding=utf8
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import torchvision.transforms as transforms
import torch
import random

IMG_W = 90
IMG_HEIGHT = 16


# img = Image.open('X_6Y_4.png')
# print(img.size)
# colors = img.getcolors()
# print(len(colors),colors)
# nps = torch.Tensor([0,0,0])
# for color in colors:
#     if color[1] == (255, 255, 255):   #102
#         continue
#     nps = nps + torch.Tensor(color[1])*color[0]
#     print('count:',color[0],'color:',color[1])
#
# print(nps/1700)


# test_img = Image.new('RGB',(90,16),(30,74,70))
# test_img.save('test.png')


# 产生一张空白图
# new_img = Image.new('RGB', (100, 200), 0)
# # 合并
# img_dir_path = r"D:\start\captche_int\captche"
# x = y = 0
#
# for name in os.listdir(img_dir_path):
#     if 'png' in name:
#         img_path = os.path.join(img_dir_path,name)
#         img = Image.open(img_path)
#         width, height = img.size
#         new_img.paste(img, (x, y))
#         y += 16
#         # y += height
#
#
# new_img.save('0.png')



#生成验证码  长度在 6 - 10 之间， 高度在 14 长度在 7
def generate_captcha(img_type='train'):
    font1 = ImageFont.truetype(r'C:\Windows\Fonts\simsun.ttc',14)
    count = 0
    while count < 2:
        img = Image.open('test.png')
        draw = ImageDraw.Draw(img)
        x_ = random.randint(0,289)
        y_ = random.randint(0,289)

        x_text = list('X:' + str(x_))
        y_text = list('Y:' + str(y_))

        x_len = len(x_text)
        y_len = len(y_text)

        for i in range(x_len):
            if i == 1:
                draw.text((5 + 7 * i + 2, 0), x_text[i], font=font1, color=(255, 255, 255))
            else:
                draw.text((5 + 7*i,0),x_text[i],font=font1,color=(255,255,255))

        y_max_gap = IMG_W  - (5 + 7 * x_len) - (7 * y_len)
        y_gap = random.randint(0,y_max_gap)

        for j in range(y_len):
            if j == 1:
                draw.text((5 + 7 * x_len + y_gap + 7 * j + 1, 0), y_text[j], font=font1, color=(255, 255, 255))
            else:
                draw.text((5 + 7 * x_len + y_gap + 7 * j, 0), y_text[j], font=font1, color=(255, 255, 255))
        string = (''.join(x_text) + ''.join(y_text)).replace(':','_')
        print('count:',count,string)
        img.save(f'image/{img_type}/{string}.png')
        # img.save(f'{string}.png')

        count += 1

generate_captcha('eval')