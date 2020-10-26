import numpy as np
import win32gui
import win32ui, win32con
from threading import Thread, Lock
import time
#DEBUG
# from skimage.io import imread,imsave

from PIL import Image

#Asyncronously captures screens of a window. Provides functions for accessing
#the captured screen.
class ScreenViewer:
    
    def __init__(self):
        self.mut = Lock()
        self.hwnd = None        # 通过函数GetHWND 获得的 窗口句柄
        self.its = None         #Time stamp of last image 
        self.i0 = None          #i0 is the latest image; 
        self.i1 = None          #i1 is used as a temporary variable
        self.cl = False         #Continue looping flag
        #Left, Top, Right, and bottom of the screen window
        self.l, self.t, self.r, self.b = 0, 0, 0, 0
        #Border on left and top to remove
        self.bl, self.bt, self.br, self.bb = 12, 31, 12, 20
        # self.bl, self.bt, self.br, self.bb = 0, 0, 0,0
        self.i = 0
        print('-1 l,t,r,b:', self.l, self.t, self.r, self.b)

    def GetHWND(self, wname = None):
        '''
        Gets handle of window to view
        wname:         Title of window to find
        Return:        True on success; False on failure
        '''
        if wname is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, wname)

        print('hwnd:',self.hwnd)
        if self.hwnd == 0:
            self.hwnd = None
            return False
        self.l, self.t, self.r, self.b = win32gui.GetWindowRect(self.hwnd)
        return True
            
    def GetScreen(self):
        '''
        Get's the latest image of the window
        '''
        while self.i0 is None:      #Screen hasn't been captured yet
            pass
        self.mut.acquire()
        s = self.i0
        self.mut.release()
        return s
        
    def GetScreenWithTime(self):
        '''
        Get's the latest image of the window along with timestamp
        '''
        while self.i0 is None:      #Screen hasn't been captured yet
            pass
        self.mut.acquire()
        s = self.i0
        t = self.its
        self.mut.release()
        return s, t
        
    def GetScreenSize(self):
        return (self.b - self.t, self.r - self.l)
        
    def GetScreenTime(self):
        '''
        Get the timestamp of the last image of screen
        '''
        while self.i0 is None:      #Screen hasn't been captured yet
            pass
        self.mut.acquire()
        s = self.its
        self.mut.release()
        return s
        
    def switch_to_now_window(self):
        win32gui.SetForegroundWindow(self.hwnd)
        
    def GetScreenImg(self):
        '''
        Gets the screen of the window referenced by self.hwnd
        '''
        if self.hwnd is None:
            raise Exception("HWND is none. HWND not called or invalid window name provided.")
        print('0 l,t,r,b:', self.l, self.t, self.r, self.b)
        self.l, self.t, self.r, self.b = win32gui.GetWindowRect(self.hwnd)
        print('l,t,r,b:',self.l,self.t,self.r,self.b)

        #Remove border around window (8 pixels on each side)
        #Remove 4 extra pixels from left and right 16 + 8 = 24
        w = self.r - self.l - self.br - self.bl
        #Remove border on top and bottom (31 on top 8 on bottom)
        #Remove 12 extra pixels from bottom 39 + 12 = 51
        h = self.b - self.t - self.bt - self.bb
        print('wh:',w,h)
        wDC = win32gui.GetWindowDC(self.hwnd)   #根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        dcObj = win32ui.CreateDCFromHandle(wDC) #根据窗口的DC获取dcObj
        cDC = dcObj.CreateCompatibleDC()        #创建可兼容的DC
        dataBitMap = win32ui.CreateBitmap()     #创建bigmap准备保存图片
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)  #为bitmap开辟空间
        cDC.SelectObject(dataBitMap)                 #高度cDC，将截图保存到saveBitmap中
        #First 2 tuples are top-left and bottom-right of destination
        #Third tuple is the start position in source
        cDC.BitBlt((0,0), (w, h), dcObj, (self.bl, self.bt), win32con.SRCCOPY)   #截取从左上角（0，0）长宽为（w，h）的图片
        print('cdc:',cDC)
        bmInfo = dataBitMap.GetInfo()
        print('bmInfo:',type(bmInfo),bmInfo)
        im = np.frombuffer(dataBitMap.GetBitmapBits(True), dtype = np.uint8)
        print('im:',type(im),im.shape,sum(im),im)
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        #Bitmap has 4 channels like: BGRA. Discard Alpha and flip order to RGB
        #31 pixels from border on top, 8 on bottom
        #8 pixels from border on the left and 8 on right
        #Remove 1 additional pixel from left and right so size is 1278 | 9
        #Remove 14 additional pixels from bottom so size is 786 | 6
        #return im.reshape(bmInfo['bmHeight'], bmInfo['bmWidth'], 4)[31:-22, 9:-9, -2::-1]
        #For 800x600 images:
        #Remove 12 pixels from bottom + border
        #Remove 4 pixels from left and right + border

        # print('image:',im.reshape(bmInfo['bmHeight'], bmInfo['bmWidth'], 4))
        # imsave(fname=f'./image/{i}.png',arr=im.reshape(bmInfo['bmHeight'], bmInfo['bmWidth'], 4))

        im = im.reshape(bmInfo['bmHeight'], bmInfo['bmWidth'], 4)[:, :, -2::-1]
        print(im.shape)
        # img = Image.new("RGB",(1005,1912))
        #保存图片 或者返回图片数据。
        # img = Image.fromarray(im)
        # img.save(f'image/{self.i}.png')
        return im

    def GetWindowPos(self):
        '''
        Gets the left, top, right, and bottom coordinates of the window
        '''
        return self.l + self.bl, self.t + self.bt, self.r - self.br, self.b - self.bb
        
    def Start(self):
        '''
        #Begins recording images of the screen
        #wf:        Write flag; write screen captures to file
        '''
        #if self.hwnd is None:
        #    return False
        self.cl = True
        thrd = Thread(target = self.ScreenUpdateT)
        thrd.start()
        return True
        
    def Stop(self):
        '''
        Stop the async thread that is capturing images
        '''
        self.cl = False
        
    def ScreenUpdateT(self):
        '''
        Thread used to capture images of screen
        '''
        i = 1
        while self.cl:      #Keep updating screen until terminating
            self.i1 = self.GetScreenImg()
            self.mut.acquire()
            self.i0 = self.i1               #Update the latest image in a thread safe way
            self.its = time.time()
            self.mut.release()       
            i += 1
            time.sleep(0.5)
            self.i += 1

    def WindowDraw(self, rect):
        '''
        Draws a rectangle to the window
        '''
        if self.hwnd is None:
            return
            #raise Exception("HWND is none. HWND not called or invalid window name provided.")
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        #Set background mode to transparent
        #dcObj.SetBkColor(0x12345)
        #dcObj.SetBkMode(0)
        dcObj.Rectangle(rect)
        # Free Resources
        dcObj.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)


if __name__ == '__main__':
    '''
    1、实例化类
    2、GetHWND(name)，
    '''

    sv = ScreenViewer()
    name = r'start [D:\start] - ...\ai_play\ScreenViewer.py [start] - PyCharm (Administrator)'
    # name = 'mysteel.xlsm - Microsoft Excel'
    # name = 'QQ'
    print(win32gui.GetWindowRect(20515968))


    #给出窗口的标题，获取到 该标题窗口的 句柄
    sv.GetHWND(name)

    # print(type(sv.hwnd),sv.hwnd)
    print('anchor:',sv.l,sv.r,sv.t,sv.b)

    # 调用start 启动, 每0.5s 获取一次指定窗口 的图像， 0点5s
    # sv.Start()
    # time.sleep(2)
    # print('sv:',type(sv.i0),sv.i0.shape)
    # sv.Stop()



    # 返回 一个 窗口名称 = name的 图片数据 格式 hwc
    sv.GetScreenImg()

    '''
    0.0、寻路系统，或者 固定路线的系统
    0.1、 血量和蓝量 相加的 系统。

    1、截图  , 用view xxx

    2、目标侦测，给出目标所在 框 boxes .     #需要手工标注

    3.1、确定是否 是目标，给出 目标坐标 bounding_1 . 
    3.2、移动坐标 bounding_2  

    4、如果是。  点击路径，移动到 目标附近。
    5、点击 bounding_1
    '''