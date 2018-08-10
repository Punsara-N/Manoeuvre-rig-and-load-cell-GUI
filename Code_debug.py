# Test

import wx

class MyFrame(wx.Frame):
    """
    Main Frame class.
    """

    def __init__(self):
        
        """
        Initialise the Frame.
        """
        
        

        #self.aclink = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.aclink.settimeout(0.01)
        #self.aclink.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.aclink.bind(('127.0.0.1', 7131))
        #self.aclink_addr = ('127.0.0.1', 7132)

        #wx.Frame.__init__(self, wx.Point(0, 0), wx.Size(720, 800))
        wx.Frame.__init__(self, None, pos=(150,150), size=(350,200))
        
class MyApp(wx.App):
    
    def __init__(self):
    
        wx.App.__init__(self)
        self.frame = MyFrame(None)
    

if __name__ == '__main__':
    
    frame = MyFrame()