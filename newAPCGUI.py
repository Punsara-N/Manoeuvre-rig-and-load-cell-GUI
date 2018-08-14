import wx
import time
import datetime
import threading
from LEDIndicatorGUI import LED
import myLog
import ntpserver

class mainWindow(wx.Frame):
    
    def __init__(self, *args, **kw):
        
        super(mainWindow, self).__init__(*args, **kw) # Runs __init__ of parent
        self._initialLayout()
        self._startLog()
        self._bindEvents()
        
        self.flag = 0
        
        self.Show()
        
    def _initialLayout(self):
        
        self.SetTitle("Access Point Center - Manoeuvre rig - University of Bristol")
        
        self.menuBar = wx.MenuBar()
        self.menuFile = wx.Menu()
        self.menuItemReset = self.menuFile.Append(wx.ID_ANY, "Reset")
        self.menuFile.AppendSeparator()
        self.menuItemExit = self.menuFile.Append(wx.ID_ANY, "Exit", "Closes the window")
        self.menuBar.Append(self.menuFile, title="&File")
        self.SetMenuBar(self.menuBar)
        
        self.CreateStatusBar()
        
        self.panel1 = wx.Panel(self)
        
        self.buttonStart            = wx.Button(self.panel1, label="Start", size = (100,30))
        self.textHost               = wx.StaticText(self.panel1, label = "Host:", style = wx.ALIGN_RIGHT)
        self.controlTextHost        = wx.TextCtrl(self.panel1, size = (100,23), value = "192.168.191.5")
        self.textMano               = wx.StaticText(self.panel1, label = "ManoSer:", style = wx.ALIGN_RIGHT)
        self.controlTextMano        = wx.TextCtrl(self.panel1, size = (100,23), value = "COM6")
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
        self.battACM = 0
        self.battCMP = 0
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
        
        self.buttonSendRemoteAT = wx.Button(self.panel3, label="Send RemoteAT", size = (100,30))
        self.comboBoxRemoteAT = wx.ComboBox(self.panel3, size = (50,23), value = "MY", choices = ["MY", "1", "2", "3"])
        self.controlTextRemoteAT = wx.TextCtrl(self.panel3, size = (120,23))
        self.controlTextRemoteATOption = wx.TextCtrl(self.panel3, size = (30,23), value = "02")
        self.buttonSendCommand = wx.Button(self.panel3, label="Send Command", size = (100,30))
        self.controlTextSendCommand = wx.TextCtrl(self.panel3, size = (120,23))
        self.controlTextSendCommandOption1 = wx.TextCtrl(self.panel3, size = (30,23), value = "01")
        self.controlTextSendCommandOption2 = wx.TextCtrl(self.panel3, size = (30,23), value = "01")
        
        self.column = wx.BoxSizer(wx.VERTICAL)
        self.row3 = wx.BoxSizer(wx.HORIZONTAL)
        self.row3.Add(self.buttonSendRemoteAT,          proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row3.Add(self.comboBoxRemoteAT,            proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row3.Add(self.controlTextRemoteAT,         proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row3.Add(self.controlTextRemoteATOption,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row4 = wx.BoxSizer(wx.HORIZONTAL)
        self.row4.Add(self.buttonSendCommand,               proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row4.Add(self.controlTextSendCommand,          proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row4.Add(self.controlTextSendCommandOption1,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.row4.Add(self.controlTextSendCommandOption2,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.column.Add(self.row3, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column.Add(self.row4, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel3.SetSizerAndFit(self.column)
        
        self.panel4 = wx.Panel(self)
        
        self.buttonSendServoCommand = wx.Button(self.panel4, label="Send Command", size = (100,30))
        self.comboBoxCommand = wx.ComboBox(self.panel4, size = (70,23), value = "Reset", choices = ["Reset", "1", "2", "3"])
        self.textStartTime = wx.StaticText(self.panel4, label = "Start time:", style = wx.ALIGN_RIGHT)
        self.controlTextSendStartTime = wx.TextCtrl(self.panel4, size = (50,23), value = "500")
        self.textTimeDelta = wx.StaticText(self.panel4, label = "Time Delta:", style = wx.ALIGN_RIGHT)
        self.controlTextTimeDelta = wx.TextCtrl(self.panel4, size = (50,23), value = "500")
        self.textNoOfCycles = wx.StaticText(self.panel4, label = "No. of cycles:", style = wx.ALIGN_RIGHT)
        self.controlTextNoOfCycles = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.textDa = wx.StaticText(self.panel4, label = "Da=", style = wx.ALIGN_RIGHT)
        self.textDe = wx.StaticText(self.panel4, label = "De=", style = wx.ALIGN_RIGHT)
        self.textDr = wx.StaticText(self.panel4, label = "Dr=", style = wx.ALIGN_RIGHT)
        self.textCa = wx.StaticText(self.panel4, label = "Ca=", style = wx.ALIGN_RIGHT)
        self.textCe = wx.StaticText(self.panel4, label = "Ce=", style = wx.ALIGN_RIGHT)
        self.textCr = wx.StaticText(self.panel4, label = "Cr=", style = wx.ALIGN_RIGHT)
        self.controlTextDa = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.controlTextDe = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.controlTextDr = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.controlTextCa = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.controlTextCe = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.controlTextCr = wx.TextCtrl(self.panel4, size = (50,23), value = "0.0")
        self.checkBoxCH1 = wx.CheckBox(self.panel4, label = "CH1")
        self.checkBoxCH2 = wx.CheckBox(self.panel4, label = "CH2")
        self.checkBoxCH3 = wx.CheckBox(self.panel4, label = "CH3")
        self.checkBoxCH4 = wx.CheckBox(self.panel4, label = "CH4")
        self.checkBoxCH5 = wx.CheckBox(self.panel4, label = "CH5")
        self.checkBoxCH6 = wx.CheckBox(self.panel4, label = "CH6")
        self.textMaxValue1 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.textMaxValue2 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.textMaxValue3 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.textMaxValue4 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.textMaxValue5 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.textMaxValue6 = wx.StaticText(self.panel4, label = "Max value", style = wx.ALIGN_RIGHT)
        self.controlTextMaxValue1 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.controlTextMaxValue2 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.controlTextMaxValue3 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.controlTextMaxValue4 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.controlTextMaxValue5 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.controlTextMaxValue6 = wx.TextCtrl(self.panel4, size = (50,23), value = "5.0")
        self.textMinFreq  = wx.StaticText(self.panel4, label = "Min freq", style = wx.ALIGN_RIGHT)
        self.textMaxFreq  = wx.StaticText(self.panel4, label = "Max freq", style = wx.ALIGN_RIGHT)
        self.textMinValue1 = wx.StaticText(self.panel4, label = "Min value", style = wx.ALIGN_RIGHT)
        self.textMinValue2 = wx.StaticText(self.panel4, label = "Min value", style = wx.ALIGN_RIGHT)
        self.textMinValue3 = wx.StaticText(self.panel4, label = "Min value", style = wx.ALIGN_RIGHT)
        self.textMinValue4 = wx.StaticText(self.panel4, label = "Min value", style = wx.ALIGN_RIGHT)
        self.controlTextMinFreq = wx.TextCtrl(self.panel4, size = (50,23), value = "1.0")
        self.controlTextMaxFreq = wx.TextCtrl(self.panel4, size = (50,23), value = "1.0")
        self.controlTextMinValue1 = wx.TextCtrl(self.panel4, size = (50,23), value = "100")
        self.controlTextMinValue2 = wx.TextCtrl(self.panel4, size = (50,23), value = "100")
        self.controlTextMinValue3 = wx.TextCtrl(self.panel4, size = (50,23), value = "100")
        self.controlTextMinValue4 = wx.TextCtrl(self.panel4, size = (50,23), value = "100")
        self.textSign1 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.textSign2 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.textSign3 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.textSign4 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.textSign5 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.textSign6 = wx.StaticText(self.panel4, label = "Sign", style = wx.ALIGN_RIGHT)
        self.controlTextSign1 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.controlTextSign2 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.controlTextSign3 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.controlTextSign4 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.controlTextSign5 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.controlTextSign6 = wx.TextCtrl(self.panel4, size = (50,23), value = "1")
        self.buttonEmergency = wx.Button(self.panel4, label="EMERGENCY STOP", size = (100,30))
        self.buttonEmergency.SetBackgroundColour('red') 
        self.buttonEmergency.SetForegroundColour('white')
        font = wx.Font(pointSize=18, family=wx.DEFAULT, style=wx.ITALIC, weight=wx.BOLD)
        self.buttonEmergency.SetFont(font)
        
        self.row5 = wx.BoxSizer(wx.HORIZONTAL)
        self.row5.Add(self.buttonSendServoCommand,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.bigColumn = wx.BoxSizer(wx.VERTICAL)
        self.smallRow = wx.BoxSizer(wx.HORIZONTAL)
        self.smallRow.Add(self.comboBoxCommand,             proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.textStartTime,               proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.controlTextSendStartTime,    proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.textTimeDelta,               proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.controlTextTimeDelta,        proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.textNoOfCycles,              proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.controlTextNoOfCycles,       proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow2 = wx.BoxSizer(wx.HORIZONTAL)
        self.smallColumn1 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn1.Add(self.textDa, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn1.Add(self.textDe, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn1.Add(self.textDr, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn1.Add(self.textCa, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn1.Add(self.textCe, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn1.Add(self.textCr, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 7)
        self.smallColumn2 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn2.Add(self.controlTextDa,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn2.Add(self.controlTextDe,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn2.Add(self.controlTextDr,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn2.Add(self.controlTextCa,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn2.Add(self.controlTextCe,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn2.Add(self.controlTextCr,           proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn3 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn3.Add(self.checkBoxCH1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn3.Add(self.checkBoxCH2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn3.Add(self.checkBoxCH3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn3.Add(self.checkBoxCH4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn3.Add(self.checkBoxCH5,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn3.Add(self.checkBoxCH6,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 2)
        self.smallColumn4 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn4.Add(self.textMaxValue1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn4.Add(self.textMaxValue2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn4.Add(self.textMaxValue3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn4.Add(self.textMaxValue4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn4.Add(self.textMaxValue5,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn4.Add(self.textMaxValue6,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn5 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn5.Add(self.controlTextMaxValue1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn5.Add(self.controlTextMaxValue2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn5.Add(self.controlTextMaxValue3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn5.Add(self.controlTextMaxValue4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn5.Add(self.controlTextMaxValue5,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn5.Add(self.controlTextMaxValue6,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn6 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn6.Add(self.textMinFreq,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn6.Add(self.textMaxFreq,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn6.Add(self.textMinValue1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn6.Add(self.textMinValue2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn6.Add(self.textMinValue3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn6.Add(self.textMinValue4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn7 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn7.Add(self.controlTextMinFreq,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn7.Add(self.controlTextMaxFreq,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn7.Add(self.controlTextMinValue1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn7.Add(self.controlTextMinValue2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn7.Add(self.controlTextMinValue3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn7.Add(self.controlTextMinValue4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn8 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn8.Add(self.textSign1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn8.Add(self.textSign2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn8.Add(self.textSign3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn8.Add(self.textSign4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn8.Add(self.textSign5,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn8.Add(self.textSign6,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP, border = 7)
        self.smallColumn9 = wx.BoxSizer(wx.VERTICAL)
        self.smallColumn9.Add(self.controlTextSign1,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn9.Add(self.controlTextSign2,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn9.Add(self.controlTextSign3,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn9.Add(self.controlTextSign4,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn9.Add(self.controlTextSign5,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallColumn9.Add(self.controlTextSign6,             proportion = 1, flag = wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, border = 5)
        self.smallRow2.Add(self.smallColumn1, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn2, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn3, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn4, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn5, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn6, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn7, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn8, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.smallRow2.Add(self.smallColumn9, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.bigColumn.Add(self.smallRow,  proportion = 0, flag = wx.ALL, border = 2)
        self.bigColumn.Add(self.smallRow2, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 2)
        self.row5.Add(self.bigColumn, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 2)
        self.row5.Add(self.buttonEmergency,   proportion = 1, flag = wx.EXPAND|wx.ALL, border = 2)
        self.panel4.SetSizerAndFit(self.row5)
        
        self.panel5 = wx.Panel(self)
        
        self.buttonResetRigPosition = wx.Button(self.panel5, label="Reset rig position", size = (150,30))
        
        self.row6 = wx.BoxSizer(wx.HORIZONTAL)
        self.row6.Add(self.buttonResetRigPosition, proportion = 0, flag = wx.ALL, border = 2)
        self.panel5.SetSizerAndFit(self.row6)
        
        self.panel6 = wx.Panel(self)
        
        self.textData = wx.StaticText(self.panel6, label = "...", size=(100,100))
        self.boxTitle = wx.StaticBox(self.panel6, -1, "Data")
        self.panel6.SetDoubleBuffered(True)
        
        self.row7 = wx.StaticBoxSizer(self.boxTitle, wx.HORIZONTAL)
        self.row7.Add(self.textData, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel6.SetSizerAndFit(self.row7)
        
        self.panel7 = wx.Panel(self)
        
        self.controlTextLog = wx.TextCtrl(self.panel7, size=(100,150), style=wx.TE_RICH2|wx.TE_MULTILINE|wx.TE_READONLY)
        
        self.row8 = wx.BoxSizer(wx.HORIZONTAL)
        self.row8.Add(self.controlTextLog, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel7.SetSizerAndFit(self.row8)
        
        self.panel8 = wx.Panel(self)
        
        self.buttonClear   = wx.Button(self.panel8, label="Clear", size = (100,30))
        self.buttonSaveLog = wx.Button(self.panel8, label="Save log", size = (100,30))
        
        self.row9 = wx.BoxSizer(wx.HORIZONTAL)
        self.row9.Add(self.buttonClear, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row9.Add(self.buttonSaveLog, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel8.SetSizerAndFit(self.row9)
        
        self.panelSizerV1 = wx.BoxSizer(wx.VERTICAL)
        self.panelSizerV1.Add(self.panel1, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel2, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel3, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel4, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel5, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel6, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel7, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV1.Add(self.panel8, proportion = 0, flag = wx.EXPAND)
        
        self.panel9 = wx.Panel(self)
        
        self.textLoadCellProfile = wx.StaticText(self.panel9, label = "Load cell profile:", style = wx.ALIGN_LEFT)
        self.controlTextLoadCellProfile = wx.TextCtrl(self.panel9, size = (150,23), value = "DefaultProfile.xml")
        self.buttonDiscover = wx.Button(self.panel9, label="Discover", size = (100,30))
        self.buttonConnect = wx.Button(self.panel9, label="Connect", size = (100,30))
        self.textIPAddress = wx.StaticText(self.panel9, label = "IP Address:", style = wx.ALIGN_LEFT)
        self.controlTextIPAddress = wx.TextCtrl(self.panel9, size = (150,23), value = "192.168.191.6")
        self.textRate = wx.StaticText(self.panel9, label = "Rate (Hz):", style = wx.ALIGN_LEFT)
        self.controlTextRate = wx.TextCtrl(self.panel9, size = (50,23), value = "244")
        self.buttonApplyRate = wx.Button(self.panel9, label="Apply rate", size = (100,30))
        self.textDataType = wx.StaticText(self.panel9, label = "Data type:", style = wx.ALIGN_LEFT)
        self.buttonFT = wx.Button(self.panel9, label="FT", size = (100,30))
        self.buttonGuage = wx.Button(self.panel9, label="Gage", size = (100,30))
        self.textSaveFile = wx.StaticText(self.panel9, label = "Save file:", style = wx.ALIGN_LEFT)
        self.controlSaveFile = wx.TextCtrl(self.panel9, size = (150,23), value = "")
        self.buttonCollectData = wx.Button(self.panel9, label="Collect data", size = (100,30))
        
        self.panelLED1 = LED(self)
        self.panelLED2 = LED(self)
        self.panelLED3 = LED(self)
        self.panelLED4 = LED(self)
        self.panelLED5 = LED(self)
        self.panelLED6 = LED(self)
        self.panelLED7 = LED(self)
        self.panelLED8 = LED(self)
        self.panelLED9 = LED(self)
        
        self.column4 = wx.BoxSizer(wx.VERTICAL)
        self.row10 = wx.BoxSizer(wx.HORIZONTAL)
        self.row10.Add(self.textLoadCellProfile, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row10.Add(self.controlTextLoadCellProfile, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row11 = wx.BoxSizer(wx.HORIZONTAL)
        self.row11.Add(self.buttonDiscover, proportion = 1, flag = wx.ALL, border = 5)
        self.row11.Add(self.buttonConnect, proportion = 1, flag = wx.ALL, border = 5)
        self.row12 = wx.BoxSizer(wx.HORIZONTAL)
        self.row12.Add(self.textIPAddress, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row12.Add(self.controlTextIPAddress, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row13 = wx.BoxSizer(wx.HORIZONTAL)
        self.row13.Add(self.textRate, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row131 = wx.BoxSizer(wx.HORIZONTAL)
        self.row131.Add(self.controlTextRate, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row131.Add(self.buttonApplyRate, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row13.Add(self.row131, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row14 = wx.BoxSizer(wx.HORIZONTAL)
        self.row14.Add(self.textDataType, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row141 = wx.BoxSizer(wx.HORIZONTAL)
        self.row141.Add(self.buttonFT, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row141.Add(self.buttonGuage, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row14.Add(self.row141, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row15 = wx.BoxSizer(wx.HORIZONTAL)
        self.row15.Add(self.textSaveFile, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row15.Add(self.controlSaveFile, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row16 = wx.BoxSizer(wx.HORIZONTAL)
        self.row16.Add(self.buttonCollectData, proportion = 1, flag = wx.ALL, border = 5)
        self.column4.Add(self.row10, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row11, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row12, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row13, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row14, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row15, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row16, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel9.SetSizerAndFit(self.column4)
        
        self.panel10 = wx.Panel(self)
        
        self.textBattery        = wx.StaticText(self.panel10, label = "Battery", style = wx.ALIGN_LEFT)
        self.textBatterySizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textBatterySizer.Add(self.textBattery, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textExternalPower  = wx.StaticText(self.panel10, label = "External power", style = wx.ALIGN_LEFT)
        self.textExternalPowerSizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textExternalPowerSizer.Add(self.textExternalPower, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textWLAN           = wx.StaticText(self.panel10, label = "WLAN", style = wx.ALIGN_LEFT)
        self.textWLANSizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textWLANSizer.Add(self.textWLAN, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer1    = wx.StaticText(self.panel10, label = "Transducer 1", style = wx.ALIGN_LEFT)
        self.textTransducer1Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer1Sizer.Add(self.textTransducer1, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer2    = wx.StaticText(self.panel10, label = "Transducer 2", style = wx.ALIGN_LEFT)
        self.textTransducer2Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer2Sizer.Add(self.textTransducer2, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer3    = wx.StaticText(self.panel10, label = "Transducer 3", style = wx.ALIGN_LEFT)
        self.textTransducer3Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer3Sizer.Add(self.textTransducer3, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer4    = wx.StaticText(self.panel10, label = "Transducer 4", style = wx.ALIGN_LEFT)
        self.textTransducer4Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer4Sizer.Add(self.textTransducer4, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer5    = wx.StaticText(self.panel10, label = "Transducer 5", style = wx.ALIGN_LEFT)
        self.textTransducer5Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer5Sizer.Add(self.textTransducer5, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.textTransducer6    = wx.StaticText(self.panel10, label = "Transducer 6", style = wx.ALIGN_LEFT)
        self.textTransducer6Sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.textTransducer6Sizer.Add(self.textTransducer6, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        
        self.column5 = wx.BoxSizer(wx.VERTICAL)
        self.column5.Add(self.textBatterySizer,          proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textExternalPowerSizer,    proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textWLANSizer,             proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer1Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer2Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer3Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer4Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer5Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column5.Add(self.textTransducer6Sizer,      proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel10.SetSizerAndFit(self.column5)
        
        self.panelSizerV2 = wx.BoxSizer(wx.VERTICAL)
        self.panelSizerV2.Add(self.panelLED1, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED2, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED3, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED4, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED5, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED6, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED7, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED8, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV2.Add(self.panelLED9, proportion = 1, flag = wx.EXPAND)
        
        self.panel12 = wx.Panel(self)
        
        self.boxTitle = wx.StaticBox(self.panel12, -1, "Measurement \n(load cell axes)")
        self.textX = wx.StaticText(self.panel12, label = "X =", style = wx.ALIGN_RIGHT)
        self.textY = wx.StaticText(self.panel12, label = "Y =", style = wx.ALIGN_RIGHT)
        self.textZ = wx.StaticText(self.panel12, label = "Z =", style = wx.ALIGN_RIGHT)
        self.textL = wx.StaticText(self.panel12, label = "L =", style = wx.ALIGN_RIGHT)
        self.textM = wx.StaticText(self.panel12, label = "M =", style = wx.ALIGN_RIGHT)
        self.textN = wx.StaticText(self.panel12, label = "N =", style = wx.ALIGN_RIGHT)
        self.textXReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textYReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textZReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textLReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textMReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textNReading = wx.StaticText(self.panel12, label = "0", style = wx.ALIGN_RIGHT)
        self.textXUnit = wx.StaticText(self.panel12, label = "N", style = wx.ALIGN_LEFT)
        self.textYUnit = wx.StaticText(self.panel12, label = "N", style = wx.ALIGN_LEFT)
        self.textZUnit = wx.StaticText(self.panel12, label = "N", style = wx.ALIGN_LEFT)
        self.textLUnit = wx.StaticText(self.panel12, label = "Nm", style = wx.ALIGN_LEFT)
        self.textMUnit = wx.StaticText(self.panel12, label = "Nm", style = wx.ALIGN_LEFT)
        self.textNUnit = wx.StaticText(self.panel12, label = "Nm", style = wx.ALIGN_LEFT)
        self.buttonShowLoadsGraph = wx.Button(self.panel12, label="Show graph", size = (100,30))
        self.buttonBias = wx.Button(self.panel12, label="Bias", size = (100,30))
        self.buttonUnbias = wx.Button(self.panel12, label="Unbias", size = (100,30))
        
        self.column6 = wx.BoxSizer(wx.VERTICAL)
        self.column6.Add(self.textX, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.textY, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.textZ, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.textL, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.textM, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.textN, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7 = wx.BoxSizer(wx.VERTICAL)
        self.column7.Add(self.textXReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7.Add(self.textYReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7.Add(self.textZReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7.Add(self.textLReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7.Add(self.textMReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column7.Add(self.textNReading, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8 = wx.BoxSizer(wx.VERTICAL)
        self.column8.Add(self.textXUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textYUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textZUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textLUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textMUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textNUnit, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row18 = wx.StaticBoxSizer(self.boxTitle, wx.HORIZONTAL)
        self.row18.Add(self.column6, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row18.Add(self.column7, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row18.Add(self.column8, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row19 = wx.BoxSizer(wx.HORIZONTAL)
        self.row19.Add(self.buttonBias, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row19.Add(self.buttonUnbias, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9 = wx.BoxSizer(wx.VERTICAL)
        self.column9.Add(self.row18, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9.Add(self.buttonShowLoadsGraph, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9.Add(self.row19, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel12.SetSizerAndFit(self.column9)
        
        self.row17 = wx.BoxSizer(wx.HORIZONTAL)
        self.row17.Add(self.panelSizerV2, proportion = 2, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row17.Add(self.panel10, proportion = 4, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row17.Add(self.panel12, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        
        self.panel11 = wx.Panel(self)
        self.panel11.SetDoubleBuffered(True)
        
        text = "Packets: \nPacket rate (Hz): \nClock offset (ms): \nDrop events: \nPackets dropped: \nDrop rate (%): \nOut-of-orders: \nDuplicates:"
        self.textLoadCellPacketStats = wx.StaticText(self.panel11, label = text, style = wx.ALIGN_LEFT)
        self.buttonStartNTPServer = wx.Button(self.panel11, label="Start NTP server", size = (100,30))
        self.buttonStopNTPServer = wx.Button(self.panel11, label="Stop NTP server", size = (100,30))
        self.textSycRequestReceived = wx.StaticText(self.panel11, label = "No. sync requests received:", style = wx.ALIGN_LEFT)
        self.textNoSycRequestReceived = wx.StaticText(self.panel11, label = "0", style = wx.ALIGN_LEFT)
        self.buttonProfile = wx.Button(self.panel11, label="Profile", size = (100,30))
        
        self.column6 = wx.BoxSizer(wx.VERTICAL)
        self.column6.Add(self.textLoadCellPacketStats, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 15)
        self.row19 = wx.BoxSizer(wx.HORIZONTAL)
        self.row19.Add(self.buttonStartNTPServer, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row19.Add(self.buttonStopNTPServer, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column6.Add(self.row19, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row20 = wx.BoxSizer(wx.HORIZONTAL)
        self.row20.Add(self.textSycRequestReceived, proportion = 2, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 0)
        self.row20.Add(self.textNoSycRequestReceived, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 0)
        self.column6.Add(self.row20, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 5)
        self.column6.Add(self.buttonProfile, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel11.SetSizerAndFit(self.column6)
        
        self.panelSizerV3 = wx.BoxSizer(wx.VERTICAL)
        self.panelSizerV3.Add(self.panel9, proportion = 0, flag = wx.EXPAND)
        self.panelSizerV3.Add(self.row17, proportion = 1, flag = wx.EXPAND)
        self.panelSizerV3.Add(self.panel11, proportion = 1, flag = wx.EXPAND)
        
        self.panelSizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.panelSizerH.Add(self.panelSizerV1, proportion = 0, flag = wx.EXPAND)
        self.panelSizerH.Add(self.panelSizerV3, proportion = 1, flag = wx.EXPAND)
        self.SetSizerAndFit(self.panelSizerH)
        
    def _bindEvents(self):
        
        self.Bind(wx.EVT_BUTTON, self._test, self.buttonResetRigPosition)
        self.Bind(wx.EVT_MENU, self._onExit, self.menuItemExit)
        self.panelLED1.Bind(wx.EVT_SIZE, self._refresh)
        self.Bind(wx.EVT_BUTTON, self.myLog.save, self.buttonSaveLog)
        self.Bind(wx.EVT_BUTTON, self.clearLog, self.buttonClear)
        self.Bind(wx.EVT_BUTTON, self.startNTPServer, self.buttonStartNTPServer)
        self.Bind(wx.EVT_BUTTON, self.stopNTPServer, self.buttonStopNTPServer)
        
        
    def startNTPServer(self, event):
        
        try:
            self.NTPServer = ntpserver.NTPServer()
        except Exception as error:
            print error
        
        
    def stopNTPServer(self, event):
        
        try:
            self.NTPServer.stopServer()
        except Exception as error:
            print error
        
        
    def clearLog(self, event):
        
        self.controlTextLog.Clear()
        self.myLog.clear()
        
    
    def _refresh(self, event):
        
        self.Refresh()
        
        
    def _onExit(self, event):
        
        self.SetStatusText("Exiting...")
        print "Exiting..."
        self.myLog.close()
        self.Close(True)
        
        
    def _startLog(self):
        
        self.myLog = myLog.myLog(self)
        
        
    def _test(self, event):
        
        if self.flag == 0:
            self.flag = 1
            try:
                dataThread = threading.Thread(target=self._test2)
                dataThread.daemon = True
                dataThread.start()
            except Exception, errtxt:
                print errtxt
        else:
            self.flag = 0
            
        print str(self.flag)
        
        
    def _test2(self):
        
        while True:
            if self.flag == 1:
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
                self.textData.SetLabel(st + '\n' + st + '\n' + st)
                self.panelLED1.colour = wx.Colour(255,0,0)
                self.panelLED1.Refresh()
                #time.sleep(0.0001)
            else:
                self.panelLED1.colour = wx.Colour(0,0,0)
                self.panelLED1.Refresh()
                break
        return
                
        

if __name__ == '__main__':
    
    app = wx.App()
    GUI = mainWindow(None)
    app.MainLoop()