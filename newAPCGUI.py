import wx

class mainWindow(wx.Frame):
    
    def __init__(self, *args, **kw):
        
        super(mainWindow, self).__init__(*args, **kw) # Runs __init__ of parent
        self._initialLayout()
        self.Show()
        
    def _initialLayout(self):
        
        self.SetTitle("Access Point Center - Manoeuvre rig - University of Bristol")
        
        self.panel1 = wx.Panel(self)
        
        self.buttonStart            = wx.Button(self.panel1, label="Start", size = (100,30))
        self.textHost               = wx.StaticText(self.panel1, label = "Host:", style = wx.ALIGN_RIGHT)
        self.controlTextHost        = wx.TextCtrl(self.panel1, size = (100,23))
        self.textMano               = wx.StaticText(self.panel1, label = "ManoSer:", style = wx.ALIGN_RIGHT)
        self.controlTextMano        = wx.TextCtrl(self.panel1, size = (100,23))
        self.buttonSetBaseTime      = wx.Button(self.panel1, label="Set base time", size = (100,30))
        self.buttonSyncTime         = wx.Button(self.panel1, label="Sync time", size = (100,30))
        self.controlTextExpNumber   = wx.TextCtrl(self.panel1, size = (50,23))
        self.buttonRecord           = wx.Button(self.panel1, label="Record", size = (100,30))
        
        self.row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.row1.Add(self.buttonStart,             proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.textHost,                proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.controlTextHost,         proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.textMano,                proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.controlTextMano,         proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonSetBaseTime,       proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonSyncTime,          proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.controlTextExpNumber,    proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row1.Add(self.buttonRecord,            proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.panel1.SetSizerAndFit(self.row1)
        
        self.panel2 = wx.Panel(self)
        
        self.radioButtonGND = wx.RadioButton(self.panel2, label = "GND:")
        self.radioButtonACM = wx.RadioButton(self.panel2, label = "ACM:")
        self.radioButtonCMP = wx.RadioButton(self.panel2, label = "CMP:")
        self.comboBoxGNDIP = wx.ComboBox(self.panel2, size = (100,23), value = "192.168.191.2", choices = ["192.168.191.2", "192.168.191.3", "192.168.191.4"])
        self.comboBoxACMIP = wx.ComboBox(self.panel2, size = (100,23), value = "192.168.191.4", choices = ["192.168.191.2", "192.168.191.3", "192.168.191.4"])
        self.comboBoxCMPIP = wx.ComboBox(self.panel2, size = (100,23), value = "192.168.191.3", choices = ["192.168.191.2", "192.168.191.3", "192.168.191.4"])
        self.guageACM = wx.Gauge(self.panel2, size = (100,23), range=100, style = wx.GA_HORIZONTAL)
        self.guageCMP = wx.Gauge(self.panel2, size = (100,23), range=100, style = wx.GA_HORIZONTAL)
        self.battACM = 50
        self.battCMP = 75
        self.guageACM.SetValue(self.battACM) # Use this to change the percentage to show
        self.guageCMP.SetValue(self.battCMP) # Use this to change the percentage to show
        self.textBattACM = wx.StaticText(self.panel2, label = str(self.battACM)+"%", style = wx.ALIGN_LEFT)
        self.textBattCMP = wx.StaticText(self.panel2, label = str(self.battCMP)+"%", style = wx.ALIGN_LEFT)
        
        self.column1 = wx.BoxSizer(wx.VERTICAL)
        self.row21 = wx.BoxSizer(wx.HORIZONTAL)
        self.row21.Add(self.radioButtonGND,  proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row21.Add(self.comboBoxGNDIP,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row22 = wx.BoxSizer(wx.HORIZONTAL)
        self.row22.Add(self.radioButtonACM,  proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row22.Add(self.comboBoxACMIP,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row22.Add(self.guageACM,        proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row22.Add(self.textBattACM,     proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row23 = wx.BoxSizer(wx.HORIZONTAL)
        self.row23.Add(self.radioButtonCMP,  proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row23.Add(self.comboBoxCMPIP,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row23.Add(self.guageCMP,        proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row23.Add(self.textBattCMP,     proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.column1.Add(self.row21, proportion = 1, flag = wx.ALIGN_LEFT|wx.ALL, border = 1)
        self.column1.Add(self.row22, proportion = 1, flag = wx.ALIGN_LEFT|wx.ALL, border = 1)
        self.column1.Add(self.row23, proportion = 1, flag = wx.ALIGN_LEFT|wx.ALL, border = 1)
        
        self.buttonActive = wx.Button(self.panel2, label="Active")
        
        self.column2 = wx.BoxSizer(wx.VERTICAL)
        self.column2.Add(self.buttonActive, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.textSimulinkTxPort         = wx.StaticText(self.panel2, label = "Simulink Tx port:", style = wx.ALIGN_RIGHT)
        self.textSimulinkRxPort         = wx.StaticText(self.panel2, label = "Simulink Rx port:", style = wx.ALIGN_RIGHT)
        self.textSimulinkExtraInputs    = wx.StaticText(self.panel2, label = "Simulink extra inputs:", style = wx.ALIGN_RIGHT)
        self.controlTextSimulinkTxPort         = wx.TextCtrl(self.panel2, size = (120,23), value = "9090")
        self.controlTextSimulinkRxPort         = wx.TextCtrl(self.panel2, size = (120,23), value = "8080")
        self.controlTextSimulinkExtraInputs    = wx.TextCtrl(self.panel2, size = (120,23), value = "p1 p2 p3 p4 p5 p6")
        
        self.column3 = wx.BoxSizer(wx.VERTICAL)
        self.row24 = wx.BoxSizer(wx.HORIZONTAL)
        self.row24.Add(self.textSimulinkTxPort, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row24.Add(self.controlTextSimulinkTxPort, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row25 = wx.BoxSizer(wx.HORIZONTAL)
        self.row25.Add(self.textSimulinkRxPort, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row25.Add(self.controlTextSimulinkRxPort, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row26 = wx.BoxSizer(wx.HORIZONTAL)
        self.row26.Add(self.textSimulinkExtraInputs, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row26.Add(self.controlTextSimulinkExtraInputs, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.column3.Add(self.row24, proportion = 1, flag = wx.ALIGN_RIGHT|wx.ALL, border = 1)
        self.column3.Add(self.row25, proportion = 1, flag = wx.ALIGN_RIGHT|wx.ALL, border = 1)
        self.column3.Add(self.row26, proportion = 1, flag = wx.ALIGN_RIGHT|wx.ALL, border = 1)
        
        
        self.row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.row2.Add(self.column1, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.EXPAND|wx.ALL, border = 5)
        self.row2.Add(self.column2, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.EXPAND|wx.ALL, border = 5)
        self.row2.Add(self.column3, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.EXPAND|wx.ALL, border = 5)
        self.panel2.SetSizerAndFit(self.row2)
        
        self.panel3 = wx.Panel(self)
        
        self.controlTextTest = wx.TextCtrl(self.panel3)
        
        self.row3 = wx.BoxSizer(wx.HORIZONTAL)
        self.row3.Add(self.controlTextTest, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel3.SetSizerAndFit(self.row3)
        
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.panel1, proportion = 0, flag = wx.EXPAND)
        self.panelSizer.Add(self.panel2, proportion = 1, flag = wx.EXPAND)
        self.panelSizer.Add(self.panel3, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(self.panelSizer)
        
        

if __name__ == '__main__':
    
    app = wx.App()
    GUI = mainWindow(None)
    app.MainLoop()