#encoding=utf8
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optimizer
import torchvision.transforms.functional as F
import string


from crnn_net import CaptchaNet
from dataset import CaptchaDataSet

device = torch.device("cuda:0" if (torch.cuda.is_available()) else "cpu")

class LabelConverter:
    def __init__(self, char_set):
        char = ['-'] + sorted(set(''.join(char_set)))
        self.vocab_size = len(char)
        self.int2char = dict(enumerate(char))
        self.char2int = {char: ind for ind, char in self.int2char.items()}

    def get_vocab_size(self):
        return self.vocab_size

    def encode(self, texts):
        text_length = []
        for t in texts:
            text_length.append(len(t))


        encoded_texts = []
        for t in texts:
            for c in t:
                encoded_texts.append(self.char2int.get(c))

        return torch.tensor(encoded_texts), torch.tensor(text_length)

    def decode(self, encoded_text):
        # decode
        text = []
        for i in encoded_text:
            text.append(self.int2char.get(i.item()))

        # remove duplicate
        decoded_text = ''
        for i, t in enumerate(text):
            if t == '-':
                continue
            if i > 0 and t == text[i-1]:
                continue
            decoded_text = decoded_text + t

        return decoded_text

def calculate_loss(inputs, texts, label_converter, device):
    criterion = nn.CTCLoss(blank=0)

    inputs = inputs.log_softmax(2)
    input_size, batch_size, _ = inputs.size()
    input_size = torch.full(size=(batch_size,), fill_value=input_size, dtype=torch.int32)

    encoded_texts, text_lens = label_converter.encode(texts)
    loss = criterion(inputs, encoded_texts.to(device), input_size.to(device), text_lens.to(device))
    return loss

def train(train_data_dir,test_dir):
    print('start training ...........')
    batch_size = 16
    num_epochs = 50

    # label_converter = LabelConverter(char_set=string.ascii_lowercase + string.digits)
    # vocab_size = label_converter.get_vocab_size()    #存在 最大数据的值  这里是 vacab = 26 + 10 + 1

    label_converter = LabelConverter(char_set='XY:' + string.digits)
    vocab_size = label_converter.get_vocab_size()  # 存在 最大数据的值  这里是 vacab = 3 + 10 + 1
    print('vocab:',vocab_size)


    model = CaptchaNet(vocab_size=vocab_size).to(device)
    train_dataset = CaptchaDataSet(train_data_dir)
    train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True,drop_last=True)

    test_dataset = CaptchaDataSet(test_dir)
    test_loader = DataLoader(test_dataset,batch_size=batch_size,shuffle=True,drop_last=True)

    opt = optimizer.Adam(model.parameters())

    if os.path.exists('output/position.pth'):
        model.load_state_dict(torch.load('output/position.pth'))

    train_loss = []
    for j in range(num_epochs):
        running_loss = 0
        for i,(img,label) in enumerate(train_loader):
            img = img.to(device)
            label = label
            outputs = model(img)

            opt.zero_grad()
            loss = calculate_loss(outputs,label,label_converter,device)
            running_loss += loss.item()
            loss.backward()
            opt.step()
        print('len:',len(train_loader))
        epoch_loss = running_loss / len(train_loader)
        print('[%d] train loss: %.4f' % (j,epoch_loss))

        train_loss.append(epoch_loss)

        if j % 5 == 0:
            torch.save(model.state_dict(),'output/position.pth')

            r_loss = 0
            model.eval()
            for i, (img_eval, label_eval) in enumerate(test_loader):

                img_eval = img_eval.to(device)
                label_eval = label_eval
                outputs_eval = model(img_eval)

                loss_ = calculate_loss(outputs_eval,label_eval,label_converter,device)
                r_loss += loss_.item()
            eval_loss = r_loss/len(test_loader)
            print('[%d] test loss: %.4f' % (j, eval_loss))

def recognize_captcha(img,weight_path):
    label_converter = LabelConverter(char_set='XY:' + string.digits)
    vocab_size = label_converter.get_vocab_size()  # 存在 最大数据的值  这里是 vacab = 3 + 10 + 1
    print('vocab:',vocab_size)

    model = CaptchaNet(vocab_size=vocab_size).to(device)
    model.load_state_dict(torch.load('output/weight.pth', map_location=device))
    model.eval()

    img = F.to_tensor(img).unsqueeze(0).to(device)

    output = model(img)
    encode_text = output.squeeze().argmax(1)
    decode_text = label_converter.decode(encode_text)

    return decode_text




if __name__ == '__main__':
    train_path = r"D:\start\ai_play\captcha_finally\image\train"
    test_path = r"D:\start\ai_play\captcha_finally\image\test"
    train(train_path,test_path)
