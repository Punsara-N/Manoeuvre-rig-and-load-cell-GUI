import wx


'''
frame = wx.Frame(None, title="Hello World")
frame.Show()
'''

class MainWindow(wx.Frame):
    
    def __init__(self, *args, **kw):
        super(MainWindow, self).__init__(*args, **kw)
        self.SetTitle("Hello World!")
        self.Show()
        
        self.panel1 = self._Panel((0,0),(200,200),(100, 100, 100))
        self.panel2 = self._Panel((200,0),(200,200),(250, 250, 250))
        
        self.panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panelSizer.Add(self.panel1,1,wx.ALIGN_CENTER)
        self.panelSizer.Add(self.panel2,1,wx.ALIGN_CENTER)
        self.SetSizer(self.panelSizer)
        
    def _Panel(self, pos, size, colour):
        self.panel = wx.Panel(self)
        self.panel.SetPosition(pos)
        self.panel.SetSize(size)
        self.panel.SetBackgroundColour(colour)
        
        self.textStatic = wx.StaticText(self.panel, label='Text:', pos=(10,10))
        self.textBox    = wx.TextCtrl(self.panel, pos=(10,40))
        
        space = 20
        self.rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.rowSizer.AddSpacer(space)
        self.rowSizer.Add(self.textStatic,1,wx.ALIGN_CENTER)
        #self.rowSizer.AddSpacer(space)
        self.rowSizer.Add(self.textBox,1,wx.ALIGN_CENTER)
        #self.rowSizer.AddSpacer(space)
        self.panel.SetSizer(self.rowSizer)


def main():
    app = wx.App()
    MainWindow(None)
    app.MainLoop()
    
if __name__ == '__main__':
    main()