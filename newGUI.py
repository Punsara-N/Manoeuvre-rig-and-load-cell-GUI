import wx

class MainWindow(wx.Frame):
    
    def __init__(self, *args, **kw):
        
        super(MainWindow, self).__init__(*args, **kw)
        self.SetTitle("Hello World!")

        self.panel1 = self._Panel((100, 100, 100))
        self.panel2 = self._Panel((250, 250, 250))
        self.panel3 = self._Panel((175, 175, 175))
        
        self.panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panelSizer.Add(self.panel1, proportion = 2, flag = wx.EXPAND)
        self.panelSizer.Add(self.panel2, proportion = 3, flag = wx.EXPAND|wx.ALL, border = 30)
        self.panelSizer.Add(self.panel3, proportion = 2, flag = wx.EXPAND)
        self.SetSizerAndFit(self.panelSizer)
        
        self.Show()
        
    def _Panel(self, colour):
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(colour)
        
        textStatic = wx.StaticText(panel, label='Text:', pos=(10,10))
        textBox    = wx.TextCtrl(panel, pos=(10,40))
        button     = wx.Button(panel, label='An example button')
        
        rowSizer = wx.BoxSizer(wx.VERTICAL)
        rowSizer.Add(textStatic, proportion = 1, flag = wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, border = 20)
        rowSizer.Add(textBox,    proportion = 2, flag = wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, border = 20)
        rowSizer.Add(button,     proportion = 1, flag = wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, border = 20)
        panel.SetSizerAndFit(rowSizer)
        
        return panel


def main():
    app = wx.App()
    MainWindow(None)
    app.MainLoop()
    
if __name__ == '__main__':
    main()