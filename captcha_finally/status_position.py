import string
import re
import numpy as np
from PIL import Image
import torch
import torchvision.transforms.functional as F
import matplotlib.pyplot as plt

import os

from train_net import LabelConverter
from crnn_net import CaptchaNet


class RecognizePosition():

    def __init__(self,position_param_path,all_positon_element):
        self.device = torch.device("cuda:0" if (torch.cuda.is_available()) else "cpu")
        self.lc = LabelConverter(all_positon_element)
        self.vocab_size = self.lc.get_vocab_size()

        self.model = CaptchaNet(vocab_size=self.vocab_size).to(self.device)

        if os.path.exists(position_param_path):
            self.model.load_state_dict(torch.load(position_param_path, map_location=self.device))
        else:
            raise FileNotFoundError('系统找不到文件：{0}，请查看识别任务走遍模型的参数设置'.format(position_param_path))

        self.model.eval()

    def return_position(self,img_data):
        image = F.to_tensor(img_data).unsqueeze(0).to(self.device)
        output = self.model(image)
        encoded_text = output.squeeze().argmax(1)
        decoded_text = self.lc.decode(encoded_text)
        return clean_position_data(decoded_text)

    def clean_position_data(self,position_text):
        #识别
        datalist = position_text.split(':')
        if len(datalist) == 4:
            x = re.findall('\d{1,3}',datalist[1])[0]
            y = re.findall('\d{1,3}',datalist[3])[0]
            return [x,y]
        else:
            return None


def clean_position_data(position_text):
    datalist = position_text.split(':')
    # print('date set:',position_text,datalist)
    if len(datalist) == 3:
        x = re.findall('\d{1,3}',datalist[1])[0]
        y = re.findall('\d{1,3}',datalist[2])[0]
        return [x,y]
    else:
        return None


if __name__ == '__main__':
    device = torch.device("cuda:0" if (torch.cuda.is_available()) else "cpu")
    label_converter = LabelConverter('XY:0123456789')
    # label_converter = LabelConverter(char_set='XY:' + string.digits)
    vocab_size = label_converter.get_vocab_size()

    model = CaptchaNet(vocab_size=vocab_size).to(device)
    model.load_state_dict(torch.load('output/position.pth', map_location=device))
    model.eval()

    correct = 0.0
    image_dir = r"D:\start\ai_play\captcha_finally\image\eval"
    name_list = os.listdir(image_dir)
    for image_name in name_list:
        ground_truth = image_name.split('/')[-1].split('.')[0]
        gt = ground_truth.split('_')
        ground_truth = [gt[1].replace('Y',''),gt[2]]
        print('ground truth:',ground_truth)
        image = Image.open(os.path.join(image_dir,image_name)).convert('RGB')
        image = F.to_tensor(image).unsqueeze(0).to(device)
        output = model(image)    # 20,1,14    s,N,CLASS
        encoded_text = output.squeeze().argmax(1)   #  S,N,CLASS  S,CLASS  S
        decoded_text = label_converter.decode(encoded_text)
        decoded_text = clean_position_data(decoded_text)
        print('decode:',decoded_text)


        if ground_truth == decoded_text:
            correct += 1

    print('accuracy =', correct/len(name_list))
    # print('accuracy =', correct/len(image_list))

    # print('XY:' + string.digits)
