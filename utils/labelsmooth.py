import torch.nn as nn
import torch.nn.functional as F

class LabelSmoothingCrossEntropy(nn.Module):

    def __init__(self, eps=0.1, reduction='mean'):
        super(LabelSmoothingCrossEntropy, self).__init__()
        self.eps = eps
        self.reduction = reduction

    def forward(self, output, target):
        c = output.size()[-1]
        log_preds = F.log_softmax(output, dim=-1)
        if self.reduction=='sum':
            loss = -log_preds.sum()
        else:
            loss = -log_preds.sum(dim=-1)
            if self.reduction=='mean':
                loss = loss.mean()
        return loss*self.eps/c + (1-self.eps) * F.nll_loss(log_preds, target, reduction=self.reduction)


if __name__ == '__main__':
    loss_fn = LabelSmoothingCrossEntropy()


    '''
    lebal_smooth :
    
    将 标签中 的分类由   [[0,0,1],[0,1,0]]   改成 [[0.05,0.05,0.9],[0.05,0.9,0.05]]
    
    al
    '''