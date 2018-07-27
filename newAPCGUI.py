import wx

class mainWindow(wx.Frame):
    
    def __init__(self, *args, **kw):
        
        super(mainWindow, self).__init__(*args, **kw) # Runs __init__ of parent
        self._initialLayout()
        self.Show()
        
    def _initialLayout(self):
        
        self.SetTitle("Access Point Center - Manoeuvre rig - University of Bristol")
        
        self.panel1 = wx.Panel(self)
        
        self.buttonStart            = wx.Button(self.panel1, label="Start")
        self.textHost               = wx.StaticText(self.panel1, label = "Host:", style = wx.ALIGN_RIGHT)
        self.controlTextHost        = wx.TextCtrl(self.panel1, size = (100,23))
        self.textMano               = wx.StaticText(self.panel1, label = "ManoSer:", style = wx.ALIGN_RIGHT)
        self.controlTextMano        = wx.TextCtrl(self.panel1, size = (100,23))
        self.buttonSetBaseTime      = wx.Button(self.panel1, label="Set base time")
        self.buttonSyncTime         = wx.Button(self.panel1, label="Sync time")
        self.controlTextExpNumber   = wx.TextCtrl(self.panel1, size = (50,23))
        self.buttonRecord           = wx.Button(self.panel1, label="Record")
        
        self.row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.row1.Add(self.buttonStart,             proportion = 2, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.textHost,                proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL)
        self.row1.Add(self.controlTextHost,         proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.textMano,                proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL)
        self.row1.Add(self.controlTextMano,         proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonSetBaseTime,       proportion = 2, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonSyncTime,          proportion = 2, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.controlTextExpNumber,    proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonRecord,            proportion = 2, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.panel1.SetSizerAndFit(self.row1)
        
        self.panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panelSizer.Add(self.panel1, proportion = 0, flag = wx.EXPAND*0)
        self.SetSizerAndFit(self.panelSizer)
        

if __name__ == '__main__':
    
    app = wx.App()
    GUI = mainWindow(None)
    app.MainLoop()