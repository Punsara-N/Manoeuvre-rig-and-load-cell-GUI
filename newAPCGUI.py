import wx
import time
import datetime
import threading
from LEDIndicatorGUI import LED
import myLog
import ntpserver
from ConfigParser import SafeConfigParser
import string
import struct
import Queue
from math import atan2,sqrt,sin,cos
import json
from wx.lib.newevent import NewEvent
import wx.lib.agw.pygauge as PG
import os
import logging
from WirelessFTDemoMainScreenController import WirelessFTDemoMainScreenController
from ProfileConfigWindow import configFrame
from DiscoveryWindow import discoveryFrame
from GraphPanel import GraphPanel

# New Event Declarations
LogEvent, EVT_LOG = NewEvent()
RxStaEvent, EVT_STAT = NewEvent()
ACM_StaEvent, EVT_ACM_STAT = NewEvent()
CMP_StaEvent, EVT_CMP_STAT = NewEvent()
GND_StaEvent, EVT_GND_STAT = NewEvent()
ACM_DatEvent, EVT_ACM_DAT = NewEvent()
CMP_DatEvent, EVT_CMP_DAT = NewEvent()
GND_DatEvent, EVT_GND_DAT = NewEvent()
EXP_DatEvent, EVT_EXP_DAT = NewEvent()

ALPHA_ONLY = 1
DIGIT_ONLY = 2
HEX_ONLY = 3

def _(ori_string):
    return ori_string

class MyValidator(wx.PyValidator):
    
    def __init__(self, flag=None, pyVar=None):
        
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.hexs = string.digits + 'abcdefABCDEF'


    def Clone(self):
        return MyValidator(self.flag)


    def Validate(self, win):
        
        tc = self.GetWindow()
        val = tc.GetValue()

        if self.flag == ALPHA_ONLY:
            return all([i in string.letters for i in val])

        elif self.flag == DIGIT_ONLY:
            return all([i in string.digits for i in val])

        elif self.flag == HEX_ONLY:
            return all([i in self.hexs for i in val])

        return True


    def OnChar(self, event):
        
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == HEX_ONLY and chr(key) in self.hexs:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in '-':
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in '.':
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return
    
    
class RedirectText(object):
    
    def __init__(self, parent):
        self.parent = parent


    def write(self, string):
        wx.PostEvent(self.parent, LogEvent(log=string))


class mainWindow(wx.Frame):
    
    def __init__(self, process=[None,None], gui2msgcQueue=None, msgc2guiQueue=None, gui2drawerQueue=None):
        
        super(mainWindow, self).__init__(None) # Runs __init__ of parent
        
        self.T0 = 0
        self.T0_loadcell = 0
        self.T0epoch = 0
        
        self.msg_process = process[0]
        self.graph_process = process[1]
        self.gui2msgcQueue = gui2msgcQueue
        self.msgc2guiQueue = msgc2guiQueue
        self.gui2drawerQueue = gui2drawerQueue
        self.screenController = WirelessFTDemoMainScreenController(self)
        
        self.parser = SafeConfigParser()
        self.parser.read('config.ini')
        
        self._initialLayout()
        self._startLog()
        self._bindEvents()
        
        self.flag = 0
        self.biasFlag = False
        
        self.OnInputType(None)
        
        self.Show(True)
        
        # Set some program flags
        self.keepgoing = True
        self.msg_thread = threading.Thread(target=self.processMsgTask)
        self.msg_thread.daemon = True
        self.msg_thread.start()
        
        
    def _initialLayout(self):
        
        self.SetTitle("Access Point Center - Manoeuvre rig - University of Bristol")
        
        self.menuBar = wx.MenuBar()
        self.menuFile = wx.Menu()
        self.menuItemEmergencyStop = self.menuFile.Append(wx.ID_ANY, "&Emergency Stop\tCTRL+E", "Emergency Stop")
        self.menuItemEmergencyReset = self.menuFile.Append(wx.ID_ANY, "Emergency &Cancel", "Emergency Canceled")
        self.menuFile.AppendSeparator()
        self.menuItemExit = self.menuFile.Append(wx.ID_ANY, "&Close\tCTRL+Q", "Close this frame")
        self.menuBar.Append(self.menuFile, "&File")
        self.SetMenuBar(self.menuBar)
        
        self.CreateStatusBar()
        
        self.panel1 = wx.Panel(self)
        
        self.buttonStart            = wx.Button(self.panel1, label="Start", size = (100,30))
        self.textHost               = wx.StaticText(self.panel1, label = "Host:", style = wx.ALIGN_RIGHT)
        self.controlTextHost        = wx.TextCtrl(self.panel1, size = (100,23), value = self.parser.get('host','AP')) # value = "192.168.191.5"
        self.textMano               = wx.StaticText(self.panel1, label = "ManoSer:", style = wx.ALIGN_RIGHT)
        self.controlTextMano        = wx.TextCtrl(self.panel1, size = (100,23), value = self.parser.get('host','COM')) # value = "COM6"
        self.buttonSetBaseTime      = wx.Button(self.panel1, label="Set base time", size = (100,30))
        self.buttonSetBaseTime.Enable(False)
        self.buttonSyncTime         = wx.ToggleButton(self.panel1, label="Sync time", size = (100,30))
        self.buttonSyncTime.SetValue(True)
        self.buttonSyncTime.Enable(False)
        self.controlTextExpNumber   = wx.TextCtrl(self.panel1, size = (50,23), value = self.parser.get('rec','prefix'), validator = MyValidator(DIGIT_ONLY))
        self.buttonRecord           = wx.ToggleButton(self.panel1, label="Record", size = (100,30))
        self.buttonRecord.Enable(False)
        
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
        
        AT_CMD = ['MY', 'MK', 'GW', 'SH', 'SL', 'DL', 'C0', 'ID', 'AH', 'MA', 'PL', 'BD', 'AI', 'WR', 'FR',]
        HOST_LIST = ["192.168.191.2", "192.168.191.3", "192.168.191.4"]
        
        self.target = 'GND'
        self.radioButtonGND = wx.RadioButton(self.panel2, label = "GND:")
        self.radioButtonACM = wx.RadioButton(self.panel2, label = "ACM:")
        self.radioButtonCMP = wx.RadioButton(self.panel2, label = "CMP:")
        self.comboBoxGNDIP = wx.ComboBox(self.panel2, size = (100,23), value = self.parser.get('host','GND'), choices = HOST_LIST)
        self.comboBoxACMIP = wx.ComboBox(self.panel2, size = (100,23), value = self.parser.get('host','ACM'), choices = HOST_LIST)
        self.comboBoxCMPIP = wx.ComboBox(self.panel2, size = (100,23), value = self.parser.get('host','CMP'), choices = HOST_LIST)
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
        self.buttonActive.Enable(False)
        
        self.column2 = wx.BoxSizer(wx.VERTICAL)
        self.column2.Add(self.buttonActive, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        
        self.textSimulinkTxPort         = wx.StaticText(self.panel2, label = "Simulink Tx port:", style = wx.ALIGN_RIGHT)
        self.textSimulinkRxPort         = wx.StaticText(self.panel2, label = "Simulink Rx port:", style = wx.ALIGN_RIGHT)
        self.textSimulinkExtraInputs    = wx.StaticText(self.panel2, label = "Simulink extra inputs:", style = wx.ALIGN_RIGHT)
        self.controlTextSimulinkTxPort         = wx.TextCtrl(self.panel2, size = (120,23), value = self.parser.get('simulink','tx'), validator = MyValidator(DIGIT_ONLY))
        self.controlTextSimulinkRxPort         = wx.TextCtrl(self.panel2, size = (120,23), value = self.parser.get('simulink','rx'), validator = MyValidator(DIGIT_ONLY))
        self.controlTextSimulinkExtraInputs    = wx.TextCtrl(self.panel2, size = (120,23), value = self.parser.get('simulink','extra'))
        
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
        self.buttonSendRemoteAT.Enable(False)
        self.comboBoxRemoteAT = wx.ComboBox(self.panel3, size = (50,23), value = "MY", choices = AT_CMD)
        self.comboBoxRemoteAT.SetToolTip(wx.ToolTip('''AT Command in TWO characters :
MY - IP Network Address
MK - IP Address Mask
GW - Gateway IP address
SH - Serial Number High
SL - Serial Number Low
DL - Destination Address Low
C0 - source IP port
ID - SSID
AH - Network Type
MA - IP Addressing Mode. 0=DHCP;1=Static
PL - Power Level
BD - baudrate
AI - Association Indication
WR - write to flash
FR - Software Reset
'''))
        self.controlTextRemoteAT = wx.TextCtrl(self.panel3, value = "", size = (120,23), validator = MyValidator(HEX_ONLY))
        self.controlTextRemoteAT.SetToolTip(wx.ToolTip('Hexadecimal Parameter for remote AT Command to set.\nIf blanked, just get the parameter.'))
        self.controlTextRemoteATOption = wx.TextCtrl(self.panel3, size = (30,23), value = "02", validator = MyValidator(HEX_ONLY))
        self.controlTextRemoteATOption.SetToolTip(wx.ToolTip('''Bitfield of supported transmission options \nSupported values include the following: \n0x00 - Disable retries and route repair \n0x02 - Apply changes. '''))
        self.buttonSendCommand = wx.Button(self.panel3, label="Send Command", size = (100,30))
        self.buttonSendCommand.Enable(False)
        self.controlTextSendCommand = wx.TextCtrl(self.panel3, value = "", size = (120,23))
        self.controlTextSendCommand.SetToolTip(wx.ToolTip('Text to be sent\nIf in continoous mode, the sent text will be prefixed with "P" and 5-digital index number.'))
        self.controlTextSendCommandOption1 = wx.TextCtrl(self.panel3, size = (30,23), value = "01", validator = MyValidator(HEX_ONLY))
        self.controlTextSendCommandOption1.SetToolTip(wx.ToolTip( '''Sets maximum number of hops a broadcast transmission can occur. \nIf set to 0, the broadcast radius will be set to the maximum hops value.'''))
        self.controlTextSendCommandOption2 = wx.TextCtrl(self.panel3, size = (30,23), value = "01", validator = MyValidator(HEX_ONLY))
        self.controlTextSendCommandOption2.SetToolTip(wx.ToolTip(
            '''Bitfield of supported transmission options. Supported values include the following:
0x01 - Disable retries and route repair
0x20 - Enable APS encryption (if EE=1)
0x40 - Use the extended transmission timeout
Enabling APS encryption presumes the source and destination have been authenticated.  I also decreases the maximum number of RF payload bytes by 4 (below the value reported by NP).
The extended transmission timeout is needed when addressing sleeping end devices.It also increases the retry interval between retries to compensate for end device polling.See Chapter 4, Transmission Timeouts, Extended Timeout for a description.
Unused bits must be set to 0.  '''))
        
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
        
        self.buttonSendServoCommand = wx.Button(self.panel4, label="Servo Command", size = (100,30))
        self.buttonSendServoCommand.Enable(False)
        self.comboBoxInputType = wx.Choice(self.panel4, size = (110,23), choices = ['Reset','Step','Doublet','3-2-1-1','Ramp', 'pitch rate','open loop','LinFreq Sweep','ExpFreq Sweep'])
        self.comboBoxInputType.SetSelection(0)
        self.textStartTime = wx.StaticText(self.panel4, label = "Start time:", style = wx.ALIGN_RIGHT)
        self.controlTextStartTime = wx.TextCtrl(self.panel4, size = (50,23), value = "500", validator = MyValidator(DIGIT_ONLY))
        self.controlTextStartTime.SetToolTip(wx.ToolTip('milliseconds'))
        self.textTimeDelta = wx.StaticText(self.panel4, label = "Time Delta:", style = wx.ALIGN_RIGHT)
        self.controlTextTimeDelta = wx.TextCtrl(self.panel4, size = (50,23), value = "500", validator = MyValidator(DIGIT_ONLY))
        self.controlTextTimeDelta.SetToolTip(wx.ToolTip('milliseconds'))
        self.textNoOfCycles = wx.StaticText(self.panel4, label = "No. of cycles:", style = wx.ALIGN_RIGHT)
        self.controlTextNoOfCycles = wx.TextCtrl(self.panel4, size = (50,23), value = "1", validator = MyValidator(DIGIT_ONLY))
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
        self.buttonEmergency.Enable(False)
        
        # To match Matthew's variables
        self.menu1 = self.menuBar
        self.menu_ES = self.menuItemEmergencyStop
        self.menu_ER = self.menuItemEmergencyReset
        self.menu_close = self.menuItemExit
        
        self.btnStart       = self.buttonStart
        self.txtHost        = self.controlTextHost
        self.txtCOM         = self.controlTextMano
        self.btnBaseTime    = self.buttonSetBaseTime
        self.btnGNDsynct    = self.buttonSyncTime 
        self.txtRecName     = self.controlTextExpNumber
        self.btnALLrec      = self.buttonRecord
        self.rbGND          = self.radioButtonGND
        self.rbACM          = self.radioButtonACM
        self.rbCMP          = self.radioButtonCMP
        self.txtGNDhost     = self.comboBoxGNDIP
        self.txtACMhost     = self.comboBoxACMIP
        self.txtCMPhost     = self.comboBoxCMPIP
        self.btnAct         = self.buttonActive
        self.txtMatlabRx    = self.controlTextSimulinkTxPort
        self.txtMatlabTx    = self.controlTextSimulinkRxPort
        self.txtMatlabExtra = self.controlTextSimulinkExtraInputs
        self.btnRmtAT       = self.buttonSendRemoteAT
        self.txtRmtATcmd    = self.comboBoxRemoteAT
        self.txtRmtATpar    = self.controlTextRemoteAT
        self.txtRmtATopt    = self.controlTextRemoteATOption
        self.btnTX          = self.buttonSendCommand
        self.txtTX          = self.controlTextSendCommand
        self.txtTXrad       = self.controlTextSendCommandOption1
        self.txtTXopt       = self.controlTextSendCommandOption2
        self.btnTM          = self.buttonSendServoCommand
        self.InputType      = self.comboBoxInputType
        self.StartTime      = self.controlTextStartTime
        self.TimeDelta      = self.controlTextTimeDelta
        self.NofCycles      = self.controlTextNoOfCycles
        self.btnES          = self.buttonEmergency
        
        self.Srv2Move1 = self.checkBoxCH1
        self.ServoRef1 = self.controlTextDa
        self.MaxValue1 = self.controlTextMaxValue1
        self.MinValue1 = self.controlTextMinFreq
        self.Sign1     = self.controlTextSign1
        self.Srv2Move2 = self.checkBoxCH2
        self.ServoRef2 = self.controlTextDe
        self.MaxValue2 = self.controlTextMaxValue2
        self.MinValue2 = self.controlTextMaxFreq
        self.Sign2     = self.controlTextSign2
        self.Srv2Move3 = self.checkBoxCH3
        self.ServoRef3 = self.controlTextDr
        self.MaxValue3 = self.controlTextMaxValue3
        self.MinValue3 = self.controlTextMinValue1
        self.Sign3     = self.controlTextSign3
        self.Srv2Move4 = self.checkBoxCH4
        self.ServoRef4 = self.controlTextCa
        self.MaxValue4 = self.controlTextMaxValue4
        self.MinValue4 = self.controlTextMinValue2
        self.Sign4     = self.controlTextSign4
        self.Srv2Move5 = self.checkBoxCH5
        self.ServoRef5 = self.controlTextCe
        self.MaxValue5 = self.controlTextMaxValue5
        self.MinValue5 = self.controlTextMinValue3
        self.Sign5     = self.controlTextSign5
        self.Srv2Move6 = self.checkBoxCH6
        self.ServoRef6 = self.controlTextCr
        self.MaxValue6 = self.controlTextMaxValue6
        self.MinValue6 = self.controlTextMinValue4
        self.Sign6     = self.controlTextSign6
        
        
        self.row5 = wx.BoxSizer(wx.HORIZONTAL)
        self.row5.Add(self.buttonSendServoCommand,   proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.bigColumn = wx.BoxSizer(wx.VERTICAL)
        self.smallRow = wx.BoxSizer(wx.HORIZONTAL)
        self.smallRow.Add(self.comboBoxInputType,             proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.textStartTime,               proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
        self.smallRow.Add(self.controlTextStartTime,    proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 2)
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
        self.buttonResetRigPosition.Enable(False)
        self.btnResetRig = self.buttonResetRigPosition
        
        self.row6 = wx.BoxSizer(wx.HORIZONTAL)
        self.row6.Add(self.buttonResetRigPosition, proportion = 0, flag = wx.ALL, border = 2)
        self.panel5.SetSizerAndFit(self.row6)
        
        self.panel6 = wx.Panel(self)
        
        '''
        self.textData = wx.StaticText(self.panel6, label = "...", size=(100,100))
        '''
        # RX statistics
        self.txtRXSta = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        # Ground board statistics
        self.txtGNDSta = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        self.txtGNDDat = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        # Aircraft model statistics
        self.txtACMSta = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        self.txtACMDat = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        # Compensator statistics
        self.txtCMPSta = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        self.txtCMPDat = wx.StaticText(self.panel6, wx.ID_ANY, "...")
        # Experiment data (?)
        self.txtExpDat = wx.StaticText(self.panel6, wx.ID_ANY, "...", size=(100,32))
        self.panel6.SetDoubleBuffered(True)
        
        self.boxTitle = wx.StaticBox(self.panel6, -1, "Data")
        self.row7 = wx.StaticBoxSizer(self.boxTitle, wx.VERTICAL)
        self.row7.Add(self.txtRXSta, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtGNDSta, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtGNDDat, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtACMSta, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtACMDat, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtCMPSta, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtCMPDat, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row7.Add(self.txtExpDat, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel6.SetSizerAndFit(self.row7)
        
        self.panel7 = wx.Panel(self)
        
        self.controlTextLog = wx.TextCtrl(self.panel7, size=(100,150), style=wx.TE_RICH2|wx.TE_MULTILINE|wx.TE_READONLY)
        self.log_txt = self.controlTextLog
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        self.log_handle = logging.StreamHandler(RedirectText(self))
        self.log_handle.setFormatter(logging.Formatter('%(asctime)s:%(message)s'))
        self.log.addHandler(self.log_handle)
        
        self.row8 = wx.BoxSizer(wx.HORIZONTAL)
        self.row8.Add(self.controlTextLog, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.panel7.SetSizerAndFit(self.row8)
        
        self.panel8 = wx.Panel(self)
        
        self.buttonClear   = wx.Button(self.panel8, label="Clear", size = (100,30))
        self.buttonSaveLog = wx.Button(self.panel8, label="Save log", size = (100,30))
        self.btnClr = self.buttonClear
        self.btnSaveLog = self.buttonSaveLog
        
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
        self.controlTextLoadCellProfile = wx.TextCtrl(self.panel9, size = (150,23), value = self.parser.get('main', 'profile'))
        self.buttonDiscover = wx.Button(self.panel9, label="Discover", size = (100,30))
        self.buttonConnect = wx.Button(self.panel9, label="Connect", size = (100,30))
        self.textIPAddress = wx.StaticText(self.panel9, label = "IP Address:", style = wx.ALIGN_LEFT)
        self.controlTextIPAddress = wx.TextCtrl(self.panel9, size = (150,23), value = self.parser.get('main', 'ipa'))
        self.textRate = wx.StaticText(self.panel9, label = "Rate (Hz):", style = wx.ALIGN_LEFT)
        self.textOversample = wx.StaticText(self.panel9, label = "Oversample rate:", style = wx.ALIGN_LEFT)
        self.controlTextRate = wx.TextCtrl(self.panel9, size = (50,23), value = self.parser.get('main', 'rate'))
        self.controlTextOversample = wx.TextCtrl(self.panel9, size = (50,23), value = self.parser.get('main', 'oversample'))
        self.buttonApplyRate = wx.Button(self.panel9, label="Apply rate", size = (100,30))
        self.textDataType = wx.StaticText(self.panel9, label = "Data type:", style = wx.ALIGN_LEFT)
        self.buttonFT = wx.Button(self.panel9, label="Force / Torque", size = (100,30))
        self.buttonGuage = wx.Button(self.panel9, label="Gage", size = (100,30))
        #self.textSaveFile = wx.StaticText(self.panel9, label = "Save file:", style = wx.ALIGN_LEFT)
        #self.controlTextSaveFile = wx.TextCtrl(self.panel9, size = (150,23), value = self.parser.get('main', 'savefile'))
        #self.buttonCollectData = wx.Button(self.panel9, label="Collect data", size = (100,30))
        
        self.textBoxProfile = self.controlTextLoadCellProfile
        self.textBoxIpa = self.controlTextIPAddress
        self.textBoxRate = self.controlTextRate
        self.textBoxOversample = self.controlTextOversample
        #self.textBoxSaveFile = self.controlTextSaveFile
        self.buttonDataTypeFT = self.buttonFT
        self.buttonDataTypeGage = self.buttonGuage
        #self.buttonSaveFile = self.buttonCollectData
        #self.buttonSaveFile.Disable()
        
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
        self.columnForRateAndOversample1 = wx.BoxSizer(wx.VERTICAL)
        self.columnForRateAndOversample1.Add(self.textRate, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.TOP, border = 10)
        self.columnForRateAndOversample1.Add(self.textOversample, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.TOP, border = 10)
        self.columnForRateAndOversample2 = wx.BoxSizer(wx.VERTICAL)
        self.columnForRateAndOversample2.Add(self.controlTextRate, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.columnForRateAndOversample2.Add(self.controlTextOversample, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row13.Add(self.columnForRateAndOversample1, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row13.Add(self.columnForRateAndOversample2, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row13.Add(self.buttonApplyRate, proportion = 2, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row14 = wx.BoxSizer(wx.HORIZONTAL)
        self.row14.Add(self.textDataType, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row141 = wx.BoxSizer(wx.HORIZONTAL)
        self.row141.Add(self.buttonFT, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        self.row141.Add(self.buttonGuage, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        self.row14.Add(self.row141, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        #self.row15 = wx.BoxSizer(wx.HORIZONTAL)
        #self.row15.Add(self.textSaveFile, proportion = 0, flag = wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 5)
        #self.row15.Add(self.controlTextSaveFile, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 5)
        #self.row16 = wx.BoxSizer(wx.HORIZONTAL)
        #self.row16.Add(self.buttonCollectData, proportion = 1, flag = wx.ALL, border = 5)
        self.column4.Add(self.row10, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row11, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row12, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row13, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column4.Add(self.row14, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        #self.column4.Add(self.row15, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        #self.column4.Add(self.row16, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel9.SetSizerAndFit(self.column4)
        
        self.panel10 = wx.Panel(self)
        self.panel10.SetDoubleBuffered(True)
        
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
        
        self.m_transLabels = [self.textTransducer1,
                              self.textTransducer2,
                              self.textTransducer3,
                              self.textTransducer4,
                              self.textTransducer5,
                              self.textTransducer6] # Used to update text if transducer becomes saturated.
        
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
        self.panel12.SetDoubleBuffered(True)
        
        self.boxTitle = wx.StaticBox(self.panel12, -1, "Measurement \n(load cell axes)")
        self.textX = wx.StaticText(self.panel12, label = "X =", style = wx.ALIGN_RIGHT)
        self.textY = wx.StaticText(self.panel12, label = "Y =", style = wx.ALIGN_RIGHT)
        self.textZ = wx.StaticText(self.panel12, label = "Z =", style = wx.ALIGN_RIGHT)
        self.textL = wx.StaticText(self.panel12, label = "L =", style = wx.ALIGN_RIGHT)
        self.textM = wx.StaticText(self.panel12, label = "M =", style = wx.ALIGN_RIGHT)
        self.textN = wx.StaticText(self.panel12, label = "N =", style = wx.ALIGN_RIGHT)
        self.textXReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textYReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textZReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textLReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textMReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textNReading = wx.StaticText(self.panel12, size=(50,23), label = " ", style = wx.ALIGN_RIGHT)
        self.textXUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.textYUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.textZUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.textLUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.textMUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.textNUnit = wx.StaticText(self.panel12, size=(100,23), label = " ", style = wx.ALIGN_LEFT)
        self.buttonShowLoadsGraph = wx.Button(self.panel12, label="Show graph", size = (100,30))
        self.buttonBias = wx.Button(self.panel12, label="Bias", size = (100,30))
        #self.buttonUnbias = wx.Button(self.panel12, label="Unbias", size = (100,30))
        self.buttonShowLoadsGraph.Disable()
        self.buttonBias.Disable()
        
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
        self.column8.Add(self.textXUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textYUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textZUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textLUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textMUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.column8.Add(self.textNUnit, proportion = 1, flag = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border = 5)
        self.row18 = wx.StaticBoxSizer(self.boxTitle, wx.HORIZONTAL)
        self.row18.Add(self.column6, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row18.Add(self.column7, proportion = 2, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row18.Add(self.column8, proportion = 3, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row19 = wx.BoxSizer(wx.HORIZONTAL)
        self.row19.Add(self.buttonBias, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        #self.row19.Add(self.buttonUnbias, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9 = wx.BoxSizer(wx.VERTICAL)
        self.column9.Add(self.row18, proportion = 6, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9.Add(self.buttonShowLoadsGraph, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.column9.Add(self.row19, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 0)
        self.panel12.SetSizerAndFit(self.column9)
        
        self.row17 = wx.BoxSizer(wx.HORIZONTAL)
        self.row17.Add(self.panelSizerV2, proportion = 2, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row17.Add(self.panel10, proportion = 4, flag = wx.EXPAND|wx.ALL, border = 0)
        self.row17.Add(self.panel12, proportion = 8, flag = wx.EXPAND|wx.ALL, border = 0)
        
        self.panel11 = wx.Panel(self)
        self.panel11.SetDoubleBuffered(True)
        
        text = "Packets: \nPacket rate (Hz): \nClock offset + delay (ms): \nDrop events: \nPackets dropped: \nDrop rate (%): \nOut-of-orders: \nDuplicates: \nTime (s):"
        self.textLoadCellPacketStats = wx.StaticText(self.panel11, label = text, style = wx.ALIGN_LEFT)
        data = " ...\n ...\n ...\n ...\n ...\n ...\n ...\n ...\n ..."
        self.textStats = wx.StaticText(self.panel11, label = data, style = wx.ALIGN_LEFT)
        self.buttonStartNTPServer = wx.Button(self.panel11, label="Start NTP server", size = (100,30))
        self.buttonStopNTPServer = wx.Button(self.panel11, label="Stop NTP server", size = (100,30))
        self.textSycRequestReceived = wx.StaticText(self.panel11, label = "No. sync requests received:", style = wx.ALIGN_LEFT)
        self.textNoSycRequestReceived = wx.StaticText(self.panel11, label = "0", style = wx.ALIGN_LEFT)
        self.buttonProfile = wx.Button(self.panel11, label="Profile", size = (100,30))
        
        self.rowStats = wx.BoxSizer(wx.HORIZONTAL)
        self.rowStats.Add(self.textLoadCellPacketStats, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        self.rowStats.Add(self.textStats, proportion = 0, flag = wx.EXPAND|wx.ALL, border = 0)
        
        self.column6 = wx.BoxSizer(wx.VERTICAL)
        self.column6.Add(self.rowStats, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 15)
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
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MENU, self.OnClose, self.menuItemExit)
        self.Bind(EVT_LOG, self.OnLog)
        self.Bind(wx.EVT_BUTTON, self.OnStart, self.btnStart)
        self.Bind(wx.EVT_BUTTON, self.OnRmtAT, self.btnRmtAT)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnSyncGND, self.btnGNDsynct)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnRecALL, self.btnALLrec)
        self.Bind(wx.EVT_BUTTON, self.OnSetBaseTime, self.btnBaseTime)
        self.Bind(wx.EVT_BUTTON, self.OnTX, self.btnTX)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChooseACM, self.rbACM)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChooseCMP, self.rbCMP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChooseGND, self.rbGND)
        self.Bind(wx.EVT_BUTTON, self.OnClr, self.btnClr)
        self.Bind(wx.EVT_BUTTON, self.OnSaveLog, self.btnSaveLog)
        self.Bind(EVT_STAT, self.OnRXSta)
        self.Bind(EVT_ACM_STAT, self.OnACMSta)
        self.Bind(EVT_CMP_STAT, self.OnCMPSta)
        self.Bind(EVT_GND_STAT, self.OnGNDSta)
        self.Bind(EVT_ACM_DAT, self.OnACMDat)
        self.Bind(EVT_CMP_DAT, self.OnCMPDat)
        self.Bind(EVT_GND_DAT, self.OnGNDDat)
        self.Bind(EVT_EXP_DAT, self.OnExpDat)
        self.Bind(wx.EVT_BUTTON, self.OnTestMotor, self.btnTM)
        self.Bind(wx.EVT_BUTTON, self.OnES, self.btnES)
        self.Bind(wx.EVT_MENU, self.OnES, self.menu_ES)
        self.Bind(wx.EVT_MENU, self.OnER, self.menu_ER)
        self.Bind(wx.EVT_BUTTON, self.OnRstRig, self.btnResetRig)
        self.Bind(wx.EVT_CHOICE, self.OnInputType, self.InputType)
        self.Bind(wx.EVT_BUTTON, self.OnActAll, self.btnAct)
        
        self.Bind(wx.EVT_BUTTON, self.openDiscoveryWindow, self.buttonDiscover)
        self.Bind(wx.EVT_BUTTON, self.buttonConnectDisconnectPressed, self.buttonConnect)
        self.Bind(wx.EVT_BUTTON, self.buttonApplyRatePressed, self.buttonApplyRate)
        self.Bind(wx.EVT_BUTTON, self.DataTypeFT, self.buttonDataTypeFT)
        self.Bind(wx.EVT_BUTTON, self.DataTypeGage, self.buttonDataTypeGage)
        #self.Bind(wx.EVT_BUTTON, self.SaveFile, self.buttonSaveFile)
        self.Bind(wx.EVT_BUTTON, self.openConfigWindow, self.buttonProfile)
        self.Bind(wx.EVT_BUTTON, self.biasUnbiasButtonPressed, self.buttonBias)
        self.Bind(wx.EVT_BUTTON, self.openLoadsGraph, self.buttonShowLoadsGraph)
        
        #self.Bind(wx.EVT_BUTTON, self._test, self.buttonResetRigPosition)
        #self.Bind(wx.EVT_MENU, self._onExit, self.menuItemExit)
        self.panelLED1.Bind(wx.EVT_SIZE, self._refresh)
        #self.Bind(wx.EVT_BUTTON, self.myLog.save, self.buttonSaveLog)
        #self.Bind(wx.EVT_BUTTON, self.clearLog, self.buttonClear)
        self.Bind(wx.EVT_BUTTON, self.startNTPServer, self.buttonStartNTPServer)
        self.Bind(wx.EVT_BUTTON, self.stopNTPServer, self.buttonStopNTPServer)
        
        
    def OnClose(self, event):
        """
        Stop the task queue, terminate processes and close the window.
        """
        busy = wx.BusyInfo("Waiting for processes to terminate...", self) 
        # Stop processing tasks and terminate the processes
        self.processTerm()
        self.keepgoing = False
        self.msg_thread.join()
        
        # Disconnecting loadcell if it's connected
        if self.screenController.m_connected == True:
            self.disconnect()
            if self.screenController.m_connected == False:
                self.buttonConnect.SetLabel('Connect')
                
        self.saveConfig()
        
        print 'Active threads remaining:'
        for thread in threading.enumerate():
            print(thread.name)

        self.Destroy()
        
        
    def OnLog(self, event) :
        self.log_txt.AppendText(event.log)
        
    
    def saveConfig(self):
        parser = self.parser
        parser.set('host','AP', self.txtHost.GetValue())
        parser.set('host','COM', self.txtCOM.GetValue())
        parser.set('host','GND', self.txtGNDhost.GetValue())
        parser.set('host','ACM', self.txtACMhost.GetValue())
        parser.set('host','CMP', self.txtCMPhost.GetValue())
        parser.set('rec','prefix', self.txtRecName.GetValue())
        parser.set('simulink','tx', self.txtMatlabRx.GetValue())
        parser.set('simulink','rx', self.txtMatlabTx.GetValue())
        parser.set('simulink','extra', self.txtMatlabExtra.GetValue())
        parser.set('main', 'profile', self.textBoxProfile.GetValue())
        parser.set('main', 'ipa', self.textBoxIpa.GetValue())
        parser.set('main', 'rate', self.textBoxRate.GetValue())
        cfg = open('config.ini', 'w')
        parser.write(cfg)
        cfg.close()
        
        
    def processMsgTask(self):
        """
        Start the execution of tasks by the processes.
        """
        while self.keepgoing:
            try:
                output = self.msgc2guiQueue.get(block=True,timeout=0.2)
                if output['ID'] == 'ExpData':
                    wx.PostEvent(self, EXP_DatEvent(states=output['states']))
                    #self.gui2drawerQueue.put_nowait(output)
                elif output['ID'] == 'info':
                    self.log.info(':'.join(['MSGC:',output['content']]))
                elif output['ID'] == 'Statistics':
                    arrv_cnt = output['arrv_cnt']
                    arrv_bcnt = output['arrv_bcnt']
                    elapsed = output['elapsed']
                    wx.PostEvent(self, RxStaEvent(txt=
                    'C{:0>5d}/T{:<.2f} {:03.0f}Pps/{:05.0f}bps'.format(
                        arrv_cnt, elapsed, arrv_cnt / elapsed,
                        arrv_bcnt * 10 / elapsed)))
                elif output['ID'] == 'ACM_STA':
                    wx.PostEvent(self, ACM_StaEvent(txt=output['info'],
                        batpct=output['batpct']))
                elif output['ID'] == 'ACM_DAT':
                    wx.PostEvent(self, ACM_DatEvent(txt=output['info']))
                elif output['ID'] == 'CMP_STA':
                    wx.PostEvent(self, CMP_StaEvent(txt=output['info'],
                        batpct=output['batpct']))
                elif output['ID'] == 'CMP_DAT':
                    wx.PostEvent(self, CMP_DatEvent(txt=output['info']))
                elif output['ID'] == 'GND_STA':
                    wx.PostEvent(self, GND_StaEvent(txt=output['info']))
                elif output['ID'] == 'GND_DAT':
                    wx.PostEvent(self, GND_DatEvent(txt=output['info']))
                elif output['ID'] == 'T0':
                    self.T0 = int(output['info'])
                    print 'T0: ' + str(self.T0)
                elif output['ID'] == 'T0_loadcell':
                    self.T0_loadcell = int(output['info'])
                    print 'T0_loadcell: ' + str(self.T0_loadcell)
                elif output['ID'] == 'T0epoch':
                    self.T0epoch = int(output['info']) # Epoch in microseconds (milliseconds accuracy)
                    print 'T0epoch: ' + str(self.T0epoch)
            except Queue.Empty:
                pass
            

    def processTerm(self):
        """
        Stop the execution of tasks by the processes.
        """
        # Terminate message center processes
        while self.msg_process.is_alive():
            self.gui2msgcQueue.put_nowait({'ID': 'STOP'})
            self.msg_process.terminate()
            self.msg_process.join()
            print 'msg_process terminated'

        try:
            if self.graph_process != None:
                if self.graph_process.is_alive():
                    self.graph_process.terminate()
                    self.graph_process.join()
        except Exception as error:
            print error
            
        
    def OnStart(self, event):
        self.gui2msgcQueue.put({'ID': 'START',
            'xbee_hosts': [self.txtHost.GetValue(), self.txtGNDhost.GetValue(),
                self.txtACMhost.GetValue(), self.txtCMPhost.GetValue()],
            'xbee_port': 0x2000, 'mano_port': self.txtCOM.GetValue(),
            'matlab_ports': [int(self.txtMatlabRx.GetValue()),
                int(self.txtMatlabTx.GetValue()),
                self.txtMatlabExtra.GetValue()],
                })

        self.btnStart.Enable(False)
        self.txtHost.Enable(False)
        self.txtCOM.Enable(False)
        self.txtGNDhost.Enable(False)
        self.txtACMhost.Enable(False)
        self.txtCMPhost.Enable(False)
        self.txtMatlabRx.Enable(False)
        self.txtMatlabTx.Enable(False)
        self.txtMatlabExtra.Enable(False)
        self.btnALLrec.Enable(True)
        self.btnBaseTime.Enable(True)
        self.btnGNDsynct.Enable(True)
        self.btnRmtAT.Enable(True)
        self.btnTX.Enable(True)
        self.btnTM.Enable(True)
        self.btnES.Enable(True)
        self.btnResetRig.Enable(True)
        self.btnAct.Enable(True)
        
        
    def OnRecALL(self, event) :
        if event.IsChecked():
            self.SaveFile(None)
            filename = time.strftime(
                    'FIWT_Exp{:03d}_%Y%m%d%H%M%S.dat'.format(
                        int(self.txtRecName.GetValue()[:3])))
            self.gui2msgcQueue.put({'ID': 'REC_START',
                'filename': filename})
        else:
            self.SaveFile(None)
            self.gui2msgcQueue.put({'ID': 'REC_STOP'})

    def OnSetBaseTime(self, event) :
        self.gui2msgcQueue.put({'ID': 'SET_BASE_TIME'})

    def OnRmtAT(self, event):
        options = self.txtRmtATopt.GetValue().encode()[:2].decode('hex')[0]
        command = self.txtRmtATcmd.GetValue().encode()[:2]
        parameter = self.txtRmtATpar.GetValue().encode()
        self.gui2msgcQueue.put({'ID': 'AT', 'target':self.target,
            'options':options, 'command':command, 'parameter':parameter})

    def OnChooseACM(self, event):
        self.target = 'ACM'
        self.log.info('Target {}'.format(self.target))

    def OnChooseCMP(self, event):
        self.target = 'CMP'
        self.log.info('Target {}'.format(self.target))

    def OnChooseGND(self, event):
        self.target = 'GND'
        self.log.info('Target {}'.format(self.target))

    def OnSyncGND(self, event) :
        self.gui2msgcQueue.put({'ID': 'NTP', 'enable':event.IsChecked()})

    def OnTX(self, event):
        data = self.txtTX.GetValue().encode()
        self.gui2msgcQueue.put({'ID': 'CMD', 'target':self.target, 'command':data})

    def OnRXSta(self, event) :
        self.txtRXSta.SetLabel(event.txt)

    def OnACMSta(self, event) :
        self.txtACMSta.SetLabel(event.txt)
        self.battACM = event.batpct
        self.guageACM.SetValue(self.battACM)
        self.textBattACM.SetLabel(str(self.battACM)+"%")
        if event.batpct < 30:
            self.textBattACM.SetForegroundColour('red')
        elif event.batpct < 40:
            self.textBattACM.SetForegroundColour('yellow')
        else:
            self.textBattACM.SetForegroundColour('green')

    def OnCMPSta(self, event) :
        self.txtCMPSta.SetLabel(event.txt)
        self.battCMP = event.batpct
        self.guageCMP.SetValue(self.battCMP)
        self.textBattCMP.SetLabel(str(self.battCMP)+"%")
        if event.batpct < 30:
            self.textBattCMP.SetForegroundColour('red')
        elif event.batpct < 40:
            self.textBattCMP.SetForegroundColour('yellow')
        else:
            self.textBattCMP.SetForegroundColour('green')

    def OnGNDSta(self, event) :
        self.txtGNDSta.SetLabel(event.txt)

    def OnACMDat(self, event) :
        self.txtACMDat.SetLabel(event.txt)

    def OnCMPDat(self, event) :
        self.txtCMPDat.SetLabel(event.txt)

    def OnGNDDat(self, event) :
        self.txtGNDDat.SetLabel(event.txt)

    def OnExpDat(self, event) :
        states = event.states
        txt = ('ACRoll{7:.2f} ACRollRate{1:.2f} '
        'RigRoll{13:07.2f} RigRollRate{14:07.2f} '
        'RigPitch{15:07.2f} RigPitchRate{16:07.2f}\n').format(*states)

        Ax = states[4]
        Ay = states[5]
        Az = states[6]
        roll_s = atan2(-Ay, -Az)*57.3
        pitch_s = atan2(Ax,sqrt(Ay*Ay+Az*Az))*57.3
        txt2 = 'AoA{:-5.1f}/AoS{:-5.1f} Pitch{:-5.1f}/Roll{:-5.1f} PitchS{:-5.1f}/RollS{:-5.1f}'.format(states[51],states[52], states[54],states[53], pitch_s,roll_s)

        self.txtExpDat.SetLabel(txt+txt2)
        msgs = {'data': {
                    'VC': states[39],
                    'VG': states[40],
                    'heading': states[13],
                    'NAV':{ 'SLG': states[15]*10,
                        'CTE': states[17]*10 },
                    'roll': states[53],
                    'pitch': states[54],
                    'AoS': states[52],
                    'AoA': states[51],
                    'Ma': states[52],
                    'GLoad':-states[6],
                    'ASL': states[15],
                    'AGL': states[17],
                    'T': states[0],
                    'mode': 'FIWT',
                    } }
        self.aclink.sendto(json.dumps(msgs), self.aclink_addr)
        
        
    def OnSaveLog(self, event):
        dlg = wx.FileDialog(
            self, message="Save log as ...", defaultDir=os.getcwd(),
            defaultFile="log.txt", wildcard="Text file(*.txt)|*.txt",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.log_txt.SaveFile(dlg.GetPath())


    def OnClr(self, event):
        self.log_txt.Clear()
        self.txtRXSta.SetLabel('...')
        self.txtACMSta.SetLabel('...')
        self.txtCMPSta.SetLabel('...')
        self.txtGNDSta.SetLabel('...')
        self.txtACMDat.SetLabel('...')
        self.txtCMPDat.SetLabel('...')
        self.txtGNDDat.SetLabel('...')

        self.battACM = 0
        self.guageACM.SetValue(self.battACM)
        self.textBattACM.SetLabel(str(self.battACM)+"%")
        self.textBattACM.SetForegroundColour('black')
        self.battCMP = 0
        self.guageCMP.SetValue(self.battCMP)
        self.textBattCMP.SetLabel(str(self.battCMP)+"%")
        self.textBattCMP.SetForegroundColour('black')
        self.txtGNDinfo.SetLabel('...')

        self.gui2msgcQueue.put({'ID': 'CLEAR'})


    def OnRstRig(self, event):
        self.gui2msgcQueue.put({'ID': 'RESET_RIG'})


    def OnES(self, event):
        self.gui2msgcQueue.put({'ID': 'EMERGENCY_STOP'})


    def OnER(self, event):
        self.gui2msgcQueue.put({'ID': 'EMERGENCY_CANCELED'})


    def OnInputType(self, event):
        InputType = self.InputType.GetSelection()+1
        if InputType == 1:
            self.StartTime.Enable(False)
            self.TimeDelta.Enable(False)
            self.NofCycles.Enable(False)
            self.ServoRef1.Enable(True)
            self.Srv2Move1.Enable(False)
            self.MaxValue1.Enable(False)
            self.MinValue1.Enable(False)
            self.Sign1.Enable(False)
            self.ServoRef2.Enable(True)
            self.Srv2Move2.Enable(False)
            self.MaxValue2.Enable(False)
            self.MinValue2.Enable(False)
            self.Sign2.Enable(False)
            self.ServoRef3.Enable(True)
            self.Srv2Move3.Enable(False)
            self.MaxValue3.Enable(False)
            self.MinValue3.Enable(False)
            self.Sign3.Enable(False)
            self.ServoRef4.Enable(True)
            self.Srv2Move4.Enable(False)
            self.MaxValue4.Enable(False)
            self.MinValue4.Enable(False)
            self.Sign4.Enable(False)
            self.ServoRef5.Enable(True)
            self.Srv2Move5.Enable(False)
            self.MaxValue5.Enable(False)
            self.MinValue5.Enable(False)
            self.Sign5.Enable(False)
            self.ServoRef6.Enable(True)
            self.Srv2Move6.Enable(False)
            self.MaxValue6.Enable(False)
            self.MinValue6.Enable(False)
            self.Sign6.Enable(False)
        else:
            self.StartTime.Enable(True)
            self.TimeDelta.Enable(True)
            self.NofCycles.Enable(True)
            self.ServoRef1.Enable(False)
            self.Srv2Move1.Enable(True)
            self.MaxValue1.Enable(True)
            self.MinValue1.Enable(False)
            self.Sign1.Enable(True)
            self.ServoRef2.Enable(False)
            self.Srv2Move2.Enable(True)
            self.MaxValue2.Enable(True)
            self.MinValue2.Enable(False)
            self.Sign2.Enable(True)
            self.ServoRef3.Enable(False)
            self.Srv2Move3.Enable(True)
            self.MaxValue3.Enable(True)
            self.MinValue3.Enable(False)
            self.Sign3.Enable(True)
            self.ServoRef4.Enable(False)
            self.Srv2Move4.Enable(True)
            self.MaxValue4.Enable(True)
            self.MinValue4.Enable(False)
            self.Sign4.Enable(True)
            self.ServoRef5.Enable(False)
            self.Srv2Move5.Enable(True)
            self.MaxValue5.Enable(True)
            self.MinValue5.Enable(False)
            self.Sign5.Enable(True)
            self.ServoRef6.Enable(False)
            self.Srv2Move6.Enable(True)
            self.MaxValue6.Enable(True)
            self.MinValue6.Enable(False)
            self.Sign6.Enable(True)
            if InputType in [8,9]:
                self.MinValue1.Enable(True)
                self.MinValue2.Enable(True)


    def OnActAll(self, event):
        for t in ['GND','ACM','CMP']:
            self.gui2msgcQueue.put({'ID': 'A5', 'target':t,
                'data':'active'})
        
        
    def OnTestMotor(self, event):
        InputType = self.InputType.GetSelection()+1
        if self.target == 'CMP' :
            Id = 0xA6
        else:
            Id = 0xA5
        if InputType == 1:
            cmd = {'ID': 'CMD',
                   'da': float(self.ServoRef1.GetValue()),
                   'de': float(self.ServoRef2.GetValue()),
                   'dr': float(self.ServoRef3.GetValue()),
                   'da_cmp': float(self.ServoRef4.GetValue()),
                   'de_cmp': float(self.ServoRef5.GetValue()),
                   'dr_cmp': float(self.ServoRef6.GetValue()) }
            self.gui2msgcQueue.put(cmd)
        else :
            Srv2Move = (1 if self.Srv2Move1.GetValue() else 0) \
                     | (2 if self.Srv2Move2.GetValue() else 0) \
                     | (4 if self.Srv2Move3.GetValue() else 0) \
                     | (8 if self.Srv2Move4.GetValue() else 0) \
                     | (16 if self.Srv2Move5.GetValue() else 0) \
                     | (32 if self.Srv2Move6.GetValue() else 0)
            others = [ int(float(self.MaxValue1.GetValue())*4096/180.0/4.0),
                       int(float(self.MaxValue2.GetValue())*4096/180.0/4.0),
                       int(float(self.MaxValue3.GetValue())*4096/180.0/4.0),
                       int(float(self.MaxValue4.GetValue())*4096/180.0/4.0),
                       int(float(self.MaxValue5.GetValue())*4096/180.0/4.0),
                       int(float(self.MaxValue6.GetValue())*4096/180.0/4.0),
                       float(self.MinValue1.GetValue()),
                       float(self.MinValue2.GetValue()),
                       float(self.MinValue3.GetValue()),
                       float(self.MinValue4.GetValue()),
                       float(self.MinValue5.GetValue()),
                       float(self.MinValue6.GetValue()),
                       int(self.Sign1.GetValue()),
                       int(self.Sign2.GetValue()),
                       int(self.Sign3.GetValue()),
                       int(self.Sign4.GetValue()),
                       int(self.Sign5.GetValue()),
                       int(self.Sign6.GetValue()),
                     ]
            starttime = int(int(self.StartTime.GetValue())*1000/1024.0)
            if InputType == 5:
                deltatime = int(int(self.TimeDelta.GetValue())*1000/(1024.0*8))
            elif InputType in [8,9]:
                deltatime = int(int(self.TimeDelta.GetValue())*1000/(1024.0*4))
                others[6] = int(others[6]*25)
                others[7] = int(others[7]*25)
            else:
                deltatime = int(int(self.TimeDelta.GetValue())*1000/1024.0)
            nofcyc = int(self.NofCycles.GetValue())
            data = struct.pack('>Bf2B2HB6B6B6B', Id, 0.0, InputType, Srv2Move,
                    starttime, deltatime, nofcyc, *others)
            self.gui2msgcQueue.put({'ID': 'A5', 'target':self.target,
                'data':data})
        
        
    def startNTPServer(self, event):
        
        try:
            serverIP = self.controlTextHost.GetValue()
            self.NTPServer = ntpserver.NTPServer(self, serverIP)
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
        self.txtRXSta.SetLabel('')
        self.txtACMSta.SetLabel('')
        self.txtCMPSta.SetLabel('')
        self.txtGNDSta.SetLabel('')
        self.txtACMDat.SetLabel('')
        self.txtCMPDat.SetLabel('')
        self.txtGNDDat.SetLabel('')

        self.ggACMbat.SetValue(0)
        self.ggACMbat.Refresh()
        self.ggCMPbat.SetValue(0)
        self.ggCMPbat.Refresh()
        self.txtGNDinfo.SetLabel('')

        self.gui2msgcQueue.put({'ID': 'CLEAR'})
        
    
    def _refresh(self, event):
        
        self.Refresh()
        
        
    def _onExit(self, event):
        
        self.SetStatusText("Exiting...")
        print "Exiting..."
        self.myLog.close()
        self.Close(True)
        
        
    def _startLog(self):
        
        self.myLog = myLog.myLog(self)
        
    
    '''
    Load cell funtions
    '''
    def openDiscoveryWindow(self, event):
        
        discoveryFrame(None, self, size = (800,250), style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
        
    def openConfigWindow(self, event):
        
        configFrame(None, self, size = (800,800), style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
    
    def openLoadsGraph(self, event):
        
        self.loadsGraph = GraphPanel(self)
    
    def buttonConnectDisconnectPressed(self, event):
        
        if self.screenController.m_connected == False:
            self.connect()
            if self.screenController.m_connected == True:
                self.buttonConnect.SetLabel('Disconnect')
                #self.buttonSaveFile.Enable()
                self.buttonShowLoadsGraph.Enable()
                self.buttonBias.Enable()
        elif self.screenController.m_connected == True:
            self.disconnect()
            if self.screenController.m_connected == False:
                self.buttonConnect.SetLabel('Connect')
                #self.buttonSaveFile.Disable()
                self.buttonShowLoadsGraph.Disable()
                self.buttonBias.Disable()
    
    def connect(self):
        
        ipa = self.textBoxIpa.GetValue() # Getting IP from text box.
        profile = self.textBoxProfile.GetValue() # Getting profile name from text box.
        print 'Connecting to:', ipa
        
        if profile == '':
            self.screenController.connectButtonPressed(ipa)
        else:
            self.screenController.connectButtonPressed(ipa, profile)
        
        if self.screenController.connectingFailed:
            title = 'Connect timed out'
            message = 'Could not connect to IP address: ' + self.textBoxIpa.GetValue() + '. If DHCP is on, the device\'s IP address may have changed; consider using the \"Discover\" button.'
            wx.MessageBox(message, title, wx.OK | wx.ICON_INFORMATION)
        else: # Connection successful.
            self.textBoxProfile.SetValue(self.screenController.profile_name)
            self.textBoxRate.SetValue(self.screenController.m_profile.m_rate)
            
            # Starting panels 1 and 2.
            self.PanelUpdateThread = PanelUpdateThread(self)
            
            # Plot graphs (panel 3).
            #self.GraphPanel = GraphPanel(self, self.panel3)

            self.screenController.m_LastPacketTime = time.time()*1000
            self.screenController.m_packets = 0
            self.screenController.m_drops = 0 
            self.screenController.m_missedPackets = 0
            self.screenController.m_rxedPacketsAcc = 0
            self.screenController.m_OutOfOrders = 0
            self.screenController.m_Duplicates = 0
            
    
    def disconnect(self):
        self.screenController.disconnectButtonPressed()
        self.buttonConnect.SetLabel('Connect')
        #self.buttonSaveFile.Disable()
        self.buttonShowLoadsGraph.Disable()
        self.buttonBias.Disable()
        
        # Stoping graph, recreating panel3
        try:
            self.GraphPanel.redraw_timer.Stop()
            self.panel3.Destroy()
            self.panel3 = wx.Panel(self, pos=(280,0), size=(770, 600))
        except Exception as e:
            print e

    
    def buttonApplyRatePressed(self, event):
        try:
            packetRate = int(self.textBoxRate.GetValue())
            oversampleRate = int(self.textBoxOversample.GetValue())
            setPacketRate = self.screenController.m_btnApplyRatePressed(packetRate, oversampleRate)
        except Exception as e:
            print e

        self.textBoxRate.SetValue(str(setPacketRate)) # Copy rate back to screen.
    
    def DataTypeFT(self, event):
        print 'Changing data type to FT.'
        self.screenController.changeGageFT(True)
    
    def DataTypeGage(self, event):
        print 'Changing data type to gage.'
        self.screenController.changeGageFT(False)
        
    def SaveFile(self, event): # Integrating with main record button
        filename = self.controlTextExpNumber.GetValue() # self.textBoxSaveFile.GetValue()
        self.screenController.collectDataButtonPressed(filename)
        
        #self.buttonSaveFile.SetLabel(self.screenController.m_btnCollectData)
    
    def SaveSettings(self):
        try: # Delete config file if it exists.
            os.remove('config.ini')
        except OSError:
            pass
        
        try:
            config = SafeConfigParser()
            config.read('config.ini')
            config.add_section('main')
            config.set('main', 'profile', self.textBoxProfile.GetValue())
            config.set('main', 'ipa', self.textBoxIpa.GetValue())
            config.set('main', 'rate', self.textBoxRate.GetValue())
            #config.set('main', 'saveFile', self.textBoxSaveFile.GetValue())
            
            with open('config.ini', 'w') as f:
                config.write(f)
            
            print 'Console settings saved.'
            
        except Exception as e:
            print 'Failed to save console settings.'
            print e
        
    def ShowPacketStatsChanged(self, event):
        value = self.checkBoxStatistics.GetValue()
        print 'Show packet stats checkbox:', value
        if value:
            self.textStatsHeadings.Show()
            self.textStats.Show()
        else:
            self.textStatsHeadings.Hide()
            self.textStats.Hide()
            
            
    def biasUnbiasButtonPressed(self, event):
        try:
            if not self.biasFlag:    # If un-baised
                self.screenController.m_model.biasSensor(0) # 0 means first transducer
                self.buttonBias.SetLabel('Un-bias')
                self.biasFlag = True
            else:
                self.screenController.m_model.unbiasSensor(0) # 0 means first transducer
                self.buttonBias.SetLabel('Bias')
                self.biasFlag = False
        except Exception as e:
            print e
            self.mainFrame.disconnect()
            
class PanelUpdateThread:
        
    def __init__(self, main):
        self.main = main
        
        #self.timer = wx.Timer(self.main.panel1)
        self.timer = wx.Timer(self.main)
        #self.main.panel1.Bind(wx.EVT_TIMER, self.PanelUpdate, self.timer)
        self.main.Bind(wx.EVT_TIMER, self.PanelUpdate, self.timer)
        self.timer.Start(1000/self.main.screenController.UI_UPDATE_HZ) # Updates at 30 Hz
        #self.timer.Start(100)
        
        self.status = True
    
    def startThread(self):
        self.th = threading.Thread(target=self.PanelUpdate)
        self.th.start()
    
    def PanelUpdate(self, event):
        
        #while True:
        if self.main.screenController.m_readingRecords:
            
            try:
                status1 = self.main.screenController.m_lastSample.getStatusCode1()
                status2 = self.main.screenController.m_lastSample.getStatusCode2()
            except Exception as error:
                print error
                print 'No packets received. Try reconnecting or restarting wireless transmitter.'
                self.timer.Stop()
                return
            
            # Updating LEDs.
            self.colourTransducer1   = self.main.screenController.colors[status1       & 0x3]
            self.colourTransducer2   = self.main.screenController.colors[status1 >>  2 & 0x3]
            self.colourTransducer3   = self.main.screenController.colors[status1 >>  4 & 0x3]
            self.colourWLAN          = self.main.screenController.colors[status1 >>  6 & 0x3]
            self.colourExternalPower = self.main.screenController.colors[status1 >>  8 & 0x3]
            self.colourLEDBattery    = self.main.screenController.colors[status1 >> 10 & 0x3]
            self.colourTransducer4   = self.main.screenController.colors[status2       & 0x3]
            self.colourTransducer5   = self.main.screenController.colors[status2 >>  2 & 0x3]
            self.colourTransducer6   = self.main.screenController.colors[status2 >>  4 & 0x3]
            #self.main.panel1.Refresh()
            
            try:
                self.main.panelLED1.colour = self.colourLEDBattery
                self.main.panelLED1.Refresh()
                self.main.panelLED2.colour = self.colourExternalPower
                self.main.panelLED2.Refresh()
                self.main.panelLED3.colour = self.colourWLAN
                self.main.panelLED3.Refresh()
                self.main.panelLED4.colour = self.colourTransducer1
                self.main.panelLED4.Refresh()
                self.main.panelLED5.colour = self.colourTransducer2
                self.main.panelLED5.Refresh()
                self.main.panelLED6.colour = self.colourTransducer3
                self.main.panelLED6.Refresh()
                self.main.panelLED7.colour = self.colourTransducer4
                self.main.panelLED7.Refresh()
                self.main.panelLED8.colour = self.colourTransducer5
                self.main.panelLED8.Refresh()
                self.main.panelLED9.colour = self.colourTransducer6
                self.main.panelLED9.Refresh()
            except Exception as error:
                print error
            
            # Update saturation flags.
            for transducer in range(0, self.main.screenController.m_model.MAX_SENSORS):
                status = status1 if (transducer<3) else status2
                saturated = (status >> (24 + transducer % 3) & 0x1) == 1
                if saturated:                                   # If the Transducer is saturated,
                    color = self.main.screenController.SATRED   # Set color  to Saturation red
                    suffix = ' SAT'                             # Set suffix to SAT
                else:                                           # If the Transducer is not saturated,
                    color = 'BLACK'                             # Set color  to black
                    suffix = '    '                             # Set suffix to blank
                self.main.m_transLabels[transducer].SetForegroundColour(color)
                self.main.m_transLabels[transducer].SetLabel('Transducer ' + str(transducer + 1) + suffix)
                
            ######################### Update graph.
                
            avgMissed  =  100.0 * self.main.screenController.m_rxedPacketsAcc / self.main.screenController.m_rxedPacketsTc # Update statistics.
            packetRate = 1000.0 * self.main.screenController.m_timeTc         / self.main.screenController.m_timeAcc
                
            #print 'Packets: %10d' % self.main.screenController.m_packets
            #print 'Packet rate (Hz): %10.0f' % packetRate
            #print 'Latency (ms): %10d' % self.main.screenController.m_lastSample.getLatency()
            #print 'Drop events: %10d' % self.main.screenController.m_drops
            #print 'Dropped packets: %10d' % self.main.screenController.m_missedPackets
            #print 'Drop rate (percentage): %10.2f' % avgMissed
            #print 'Out-of-order packets: %10d' % self.main.screenController.m_OutOfOrders
            #print 'Duplicate packets: %10d \n' % self.main.screenController.m_Duplicates
            
            try:
                label='%10d \n%10.0f \n%10.3f \n%10d \n%10d \n%10.2f \n%10d \n%10d \n%10.6f' % (self.main.screenController.m_packets, 
                                                                                                 packetRate, 
                                                                                                 self.main.screenController.m_lastSample.getLatency(), 
                                                                                                 self.main.screenController.m_drops, 
                                                                                                 self.main.screenController.m_missedPackets,
                                                                                                 avgMissed,
                                                                                                 self.main.screenController.m_OutOfOrders,
                                                                                                 self.main.screenController.m_Duplicates,
                                                                                                 self.main.screenController.m_lastSample.loadcellTimeStamp)
                                                                                     
                self.main.textStats.SetLabel(label)
            except Exception as error:
                print error
            
            # Forces and moments values.
            self.main.screenController.panel.setSensorData(self.main.screenController.m_lastSample)
            stringForces,stringMoments = self.main.screenController.panel.updatePlot()
            
            X = float(stringForces.split('\n\n')[0].strip())
            Y = float(stringForces.split('\n\n')[1].strip())
            Z = float(stringForces.split('\n\n')[2].strip())
            L = float(stringMoments.split('\n\n')[0].strip())
            M = float(stringMoments.split('\n\n')[1].strip())
            N = float(stringMoments.split('\n\n')[2].strip())
            forceUnits = self.main.screenController.panel.FUnitsHeading
            momentUnits = self.main.screenController.panel.TUnitsHeading
            
            self.main.textXReading.SetLabel(str(X))
            self.main.textYReading.SetLabel(str(Y))
            self.main.textZReading.SetLabel(str(Z))
            self.main.textLReading.SetLabel(str(L))
            self.main.textMReading.SetLabel(str(M))
            self.main.textNReading.SetLabel(str(N))
            self.main.textXUnit.SetLabel(forceUnits)
            self.main.textYUnit.SetLabel(forceUnits)
            self.main.textZUnit.SetLabel(forceUnits)
            self.main.textLUnit.SetLabel(momentUnits)
            self.main.textMUnit.SetLabel(momentUnits)
            self.main.textNUnit.SetLabel(momentUnits)
                    
            #self.main.Refresh()    
                
        else:
            self.timer.Stop()
            self.main.Refresh()
            self.panelReset()
            return 
        
    def panelReset(self):
        # Setting displays to default
        self.panelLED1.colour = 'BLACK'
        self.panelLED1.Refresh()
        self.panelLED2.colour = 'BLACK'
        self.panelLED2.Refresh()
        self.panelLED3.colour = 'BLACK'
        self.panelLED3.Refresh()
        self.panelLED4.colour = 'BLACK'
        self.panelLED4.Refresh()
        self.panelLED5.colour = 'BLACK'
        self.panelLED5.Refresh()
        self.panelLED6.colour = 'BLACK'
        self.panelLED6.Refresh()
        self.panelLED7.colour = 'BLACK'
        self.panelLED7.Refresh()
        self.panelLED8.colour = 'BLACK'
        self.panelLED8.Refresh()
        self.panelLED9.colour = 'BLACK'
        self.panelLED9.Refresh()
        self.main.textStats.SetLabel(" ")
        self.main.textXReading.SetLabel(" ")
        self.main.textYReading.SetLabel(" ")
        self.main.textZReading.SetLabel(" ")
        self.main.textLReading.SetLabel(" ")
        self.main.textMReading.SetLabel(" ")
        self.main.textNReading.SetLabel(" ")
        self.main.textXUnit.SetLabel(" ")
        self.main.textYUnit.SetLabel(" ")
        self.main.textZUnit.SetLabel(" ")
        self.main.textLUnit.SetLabel(" ")
        self.main.textMUnit.SetLabel(" ")
        self.main.textNUnit.SetLabel(" ")
        
        
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
    GUI = mainWindow()
    app.MainLoop()