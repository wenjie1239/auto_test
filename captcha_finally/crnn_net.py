#encoding=utf8

import torch
import torch.nn as nn
import os


class ConvolutionLayer(nn.Module):

    def __init__(self,filter_in,filter_out,kernel_size=3,stride=1):
        '''
        input data: x.shape = N,filter_in,H,W
        :param in_channel:
        :param out_channel:
        :return out.shape =  N,filter_out,H,W
        '''
        super(ConvolutionLayer, self).__init__()
        pad = (kernel_size - 1) // 2 if kernel_size else 0
        self.conv = nn.Sequential(
            nn.Conv2d(filter_in,filter_out,kernel_size,stride,pad),
            nn.BatchNorm2d(filter_out),
            nn.LeakyReLU(),
        )

    def forward(self,x):
        return self.conv(x)


class CaptchaNet(nn.Module):
    #n,3,16,90
    def __init__(self,vocab_size = 14,num_rnn_layers=1,rnn_hidden_size=128,dropout=0):
        super().__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3,32,kernel_size=(2,4),stride=(2,2)),   # N,32,8,44
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Dropout2d(dropout)
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32,64,kernel_size=(2,4),stride=(2,2)),  #N,64,4,21
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(dropout)
        )
        self.layer3 = nn.Sequential(
            nn.Conv2d(64,128,kernel_size=(4,4),stride=(1,1),padding=(0,1)),   #N,128,1,20  -> n,128,1*20  NSV
            nn.BatchNorm2d(128),
            nn.ReLU()
        )

        self.gru = nn.GRU(128,rnn_hidden_size,num_rnn_layers,batch_first=True,dropout=dropout)

        self.fc = nn.Linear(128,vocab_size)

    def forward(self,x):
        '''

        :param x: image data, x.shape =  N,3,90,16
        :param hidden:   h0.shape =
        :return:
        '''
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)  # N,128,1,20 nchw   -> N,128,20  nsv   N,20,128
        out = out.reshape(out.size(0),128,-1)
        out = out.permute(0,2,1)
        out,_ = self.gru(out)     # N,S,V  N,20,128

        fc = self.fc(out)         #N,S,vocab_size
        fc_out = fc.permute(1,0,2)    #S,N,vocab_size

        return fc_out


class TextNet(nn.Module):

    def __init__(self):
        super(TextNet, self).__init__()
        self.gru = nn.GRU()

    def forward(self,x):
        pass


if __name__ == '__main__':

    HEIGHT =  16  #48
    WIDTH = 90   #128

    #Encode input
    x = torch.randn((64,3,16,90))
    hidden = torch.zeros((2,64,128))

    cn = CaptchaNet()
    out = cn(x)







