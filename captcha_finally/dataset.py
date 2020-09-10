#encoding=utf8
import os
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import Dataset,DataLoader
from torchvision.transforms import transforms

tf = transforms.Compose(
    [transforms.ToTensor()]
)





class CaptchaDataSet(Dataset):

    def __init__(self,images_dir):
        super().__init__()
        self.images_dir = images_dir
        self.img_name_list = os.listdir(images_dir)

    def __len__(self):
        return len(self.img_name_list)

    def __getitem__(self, index):
        img_name = self.img_name_list[index]
        text = img_name.replace('_',':').split('.')[0]

        img_path = os.path.join(self.images_dir,img_name)
        img = Image.open(img_path)
        img = tf(img)
        return img[:3,...],text


def get_loader(root,batch_size):
    train_dataset = CaptchaDataSet(root + '/train')


if __name__ == '__main__':
    dir = r"D:\start\ai_play\captcha_finally\image\train"
    dataset =CaptchaDataSet(dir)
    loader = DataLoader(dataset,3,True,drop_last=True)
    for img,text in loader:
        print('text:',text)
        print('img:',img.shape)