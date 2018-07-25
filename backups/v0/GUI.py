'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 01-07-2017
-------------------------------------------------------------------------------------------------
'''

""" User interface. """

import wx
#from wx.lib.pubsub import pub
from WirelessFTDemoMainScreenController import WirelessFTDemoMainScreenController
from ConfigParser import SafeConfigParser
import os
from GraphPanel import DataGen
from GraphPanel import GraphPanel

class mainFrame(wx.Frame):
    
    from LEDController import LED
    import time
    
    def __init__(self, *args, **kwargs):
        
        super(mainFrame, self).__init__(*args, **kwargs)
        self.screenController = WirelessFTDemoMainScreenController()
        self.basicGUI()
        #pub.subscribe(self.myListener, "panelListener")
        
        
    def basicGUI(self):
        
        config = SafeConfigParser()
        config.read('config.ini')
        
        ''' Window title. '''
        self.SetTitle('Load Cell Interface, University of Bristol')
        
        ''' Buttons on menu bar. '''
        fileButton = wx.Menu()
        exitItem = fileButton.Append(wx.ID_EXIT, '&Exit', 'Exit the window.')
        self.Bind(wx.EVT_MENU, self.Quit, exitItem)
        
        editButton = wx.Menu()
        
        ''' The menu bar. '''
        menuBar = wx.MenuBar()
        menuBar.Append(fileButton, '&File')
        menuBar.Append(editButton, '&Edit')
        self.SetMenuBar(menuBar)
        
        ''' Panel 1. '''
        panel1 = wx.Panel(self, pos=(0,0), size=(280, 800))
        
        # Profile text box.
        self.textProfile = wx.StaticText(panel1, label='Profile:', pos=(10,10))
        configProfile = config.get('main', 'profile')
        self.textBoxProfile = wx.TextCtrl(panel1, value=configProfile, pos=(110,10), size=(150,20))
        
        # Discovery button.
        buttonDiscover = wx.Button(panel1, label='Discover', pos=(10,40), size=(100,30))
        buttonDiscover.Bind(wx.EVT_BUTTON, self.openDiscoveryWindow)
        
        # Connect button.
        self.buttonConnect = wx.Button(panel1, label='Connect', pos=(160,40), size=(100,30))
        self.buttonConnect.Bind(wx.EVT_BUTTON, self.buttonConnectDisconnectPressed)
        
        # IPA text box.
        self.textIpa = wx.StaticText(panel1, label='IP Address:', pos=(10,80))
        configIpa = config.get('main', 'ipa')
        self.textBoxIpa = wx.TextCtrl(panel1, value=configIpa, pos=(110,80), size=(150,20))
        
        # Rate changing.
        self.textRate = wx.StaticText(panel1, label='Rate (Hz):', pos=(10,110))
        configRate = config.get('main', 'rate')
        self.textBoxRate = wx.TextCtrl(panel1, value=configRate, pos=(110,110), size=(50,20))
        self.buttonApplyRate = wx.Button(panel1, label='Apply Rate', pos=(170,110), size=(90,20))
        self.buttonApplyRate.Bind(wx.EVT_BUTTON, self.buttonApplyRatePressed)
        
        # Data type changing.
        self.textDataType = wx.StaticText(panel1, label='Data Type:', pos=(10,140))
        self.buttonDataTypeFT = wx.Button(panel1, label='FT', pos=(110,140), size=(70,20))
        self.buttonDataTypeFT.Bind(wx.EVT_BUTTON, self.DataTypeFT)
        self.buttonDataTypeGage = wx.Button(panel1, label='Gage', pos=(190,140), size=(70,20))
        self.buttonDataTypeGage.Bind(wx.EVT_BUTTON, self.DataTypeGage)
        
        # Save file.
        self.textSaveFile = wx.StaticText(panel1, label='Save File:', pos=(10,170))
        configSaveFile = config.get('main', 'saveFile')
        self.textBoxSaveFile = wx.TextCtrl(panel1, value=configSaveFile, pos=(110,170), size=(150,20))
        self.buttonSaveFile = wx.Button(panel1, label='Collect Data', pos=(110,200), size=(150,20))
        self.buttonSaveFile.Bind(wx.EVT_BUTTON, self.SaveFile)
        self.buttonSaveFile.Disable()
        
        # LEDs.
#        self.LEDBattery = self.LED(self, 20, 230)
#        self.LEDBattery.LEDColour('BLACK')
#        self.textLEDBattery = wx.StaticText(panel1, label='Battery', pos=(50,235))
#        
#        self.LEDExternalPower = self.LED2(self, 20, 260)
#        self.LEDExternalPower.LEDColour('BLACK')
#        self.textExternalPower = wx.StaticText(panel1, label='External Power', pos=(50,265))
#        
#        self.LEDWLAN = self.LED2(self, 20, 290)
#        self.LEDWLAN.LEDColour('BLACK')
#        self.textWLAN = wx.StaticText(panel1, label='WLAN', pos=(50,295))
#        
#        self.LEDTransducer1 = self.LED2(self, 20, 320)
#        self.LEDTransducer1.LEDColour('BLACK')
#        self.textTransducer1 = wx.StaticText(panel1, label='Transducer 1', pos=(50,325))
#        
#        self.LEDTransducer2 = self.LED2(self, 20, 350)
#        self.LEDTransducer2.LEDColour('BLACK')
#        self.textTransducer2 = wx.StaticText(panel1, label='Transducer 2', pos=(50,355))
#        
#        self.LEDTransducer3 = self.LED2(self, 20, 380)
#        self.LEDTransducer3.LEDColour('BLACK')
#        self.textTransducer3 = wx.StaticText(panel1, label='Transducer 3', pos=(50,385))
#        
#        self.LEDTransducer4 = self.LED2(self, 20, 410)
#        self.LEDTransducer4.LEDColour('BLACK')
#        self.textTransducer4 = wx.StaticText(panel1, label='Transducer 4', pos=(50,415))
#        
#        self.LEDTransducer5 = self.LED2(self, 20, 440)
#        self.LEDTransducer5.LEDColour('BLACK')
#        self.textTransducer5 = wx.StaticText(panel1, label='Transducer 5', pos=(50,445))
#        
#        self.LEDTransducer6 = self.LED2(self, 20, 470)
#        self.LEDTransducer6.LEDColour('BLACK')
#        self.textTransducer6 = wx.StaticText(panel1, label='Transducer 6', pos=(50,475))
        
        self.colourLEDBattery    = 'BLACK'
        self.colourExternalPower = 'BLACK'
        self.colourWLAN          = 'BLACK'
        self.colourTransducer1   = 'BLACK'
        self.colourTransducer2   = 'BLACK'
        self.colourTransducer3   = 'BLACK'
        self.colourTransducer4   = 'BLACK'
        self.colourTransducer5   = 'BLACK'
        self.colourTransducer6   = 'BLACK'
        
        self.Buffer = None
        panel1.Bind(wx.EVT_PAINT, self.OnPaint) # Paints LEDs.
        panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack) # Prevents flickering.
        
        self.textLEDBattery = wx.StaticText(panel1, label='Battery', pos=(50,235))
        self.textExternalPower = wx.StaticText(panel1, label='External Power', pos=(50,265))
        self.textWLAN = wx.StaticText(panel1, label='WLAN', pos=(50,295))
        self.textTransducer1 = wx.StaticText(panel1, label='Transducer 1', pos=(50,325))
        self.textTransducer2 = wx.StaticText(panel1, label='Transducer 2', pos=(50,355))
        self.textTransducer3 = wx.StaticText(panel1, label='Transducer 3', pos=(50,385))
        self.textTransducer4 = wx.StaticText(panel1, label='Transducer 4', pos=(50,415))
        self.textTransducer5 = wx.StaticText(panel1, label='Transducer 5', pos=(50,445))
        self.textTransducer6 = wx.StaticText(panel1, label='Transducer 6', pos=(50,475))
        
        self.m_transLabels = [self.textTransducer1,
                              self.textTransducer2,
                              self.textTransducer3,
                              self.textTransducer4,
                              self.textTransducer5,
                              self.textTransducer6] # Used to update text if transducer becomes saturated.
        
        # Show packet statistics check box.
        self.checkBoxStatistics = wx.CheckBox(panel1, -1 ,'Show Packet Statistics', (20, 520))
        self.checkBoxStatistics.Bind(wx.EVT_CHECKBOX, self.ShowPacketStatsChanged)
        
        # Packet statistics.
        self.textStatsHeadings = wx.StaticText(panel1, label='Packets: \nPacket rate (Hz): \nClock Offset (ms): \nDrop Events: \nPackets Dropped: \nDrop Rate(%): \nOut-of-orders: \nDuplicates:', pos=(20,550))
        self.textStatsHeadings.Hide()
        self.textStats = wx.StaticText(panel1, label='  \n  \n  \n  \n  \n  \n  \n ', pos=(120,550))
        self.textStats.Hide()
        
        ''' Panel 2. '''
        panel2 = wx.Panel(self, pos=(280,600), size=(770, 200))
        
        # Forces and moments value display.
        self.textForcesHeading = wx.StaticText(panel2, label=' ', pos=(120, 20))
        self.textMomentsHeading = wx.StaticText(panel2, label=' ', pos=(220, 20))
        self.textForcesValues = wx.StaticText(panel2, label=' ', pos=(100, 50))
        self.textMomentsValues = wx.StaticText(panel2, label=' ', pos=(200, 50))
        self.textAxesX = wx.StaticText(panel2, label='X', pos=(90, 50))
        self.textAxesY = wx.StaticText(panel2, label='Y', pos=(90, 82))
        self.textAxesZ = wx.StaticText(panel2, label='Z', pos=(90, 114))
        self.textAxesX.Hide()
        self.textAxesY.Hide()
        self.textAxesZ.Hide()
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.textForcesHeading.SetFont(font)
        self.textMomentsHeading.SetFont(font)
        self.textForcesValues.SetFont(font)
        self.textMomentsValues.SetFont(font)
        self.textAxesX.SetFont(font)
        self.textAxesY.SetFont(font)
        self.textAxesZ.SetFont(font)
        self.textAxesX.SetForegroundColour('RED')
        self.textAxesY.SetForegroundColour('GREEN')
        self.textAxesZ.SetForegroundColour('BLUE')
        
        # Quit button.
        buttonQuit = wx.Button(panel2, label='Quit', pos=(650,110), size=(100,30))
        buttonQuit.Bind(wx.EVT_BUTTON, self.Quit)
        
        ''' Panel 3. '''
        panel3 = wx.Panel(self, pos=(280,0), size=(770, 600))
        
        
        self.panel1 = panel1
        self.panel2 = panel2
        self.panel3 = panel3
        self.Show()
        
        #self.panel1.Bind(wx.EVT_PAINT, self.drawLED) # Draws the LEDs
        #self.panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack) # To avoid flickering
        
        
        
    ''' //////////////////// Used for drawing LEDs. \\\\\\\\\\\\\\\\\\\\ '''
    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker
        
    def InitBuffer(self):
        width  = 280 # Create a bitmap buffer the same size as panel1.
        height = 800
        
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == width and self.Buffer.GetHeight() == height:
            return False

        self.Buffer=wx.EmptyBitmap(width, height) # Create a bitmap buffer the same size as panel1.
        dc=wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        dc.SetBackground(wx.Brush(self.panel1.GetBackgroundColour()))
        dc.Clear()
        self.Drawcircle(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def Drawcircle(self,dc):
        
        # LEDBattery
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourLEDBattery, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+235, 10)
        
        # ExternalPower
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourExternalPower, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+265, 10)
        
        # WLAN
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourWLAN, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+295, 10)
        
        # Transducer1
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer1, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+325, 10)
        
        # Transducer2
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer2, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+355, 10)
        
        # Transducer3
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer3, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+385, 10)
        
        # Transducer4
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer4, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+415, 10)
        
        # Transducer5
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer5, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+445, 10)
        
        # Transducer6
        dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        dc.SetBrush(wx.Brush(self.colourTransducer6, wx.SOLID)) # Fill.
        dc.DrawCircle(30, 5+475, 10)
        
    def OnPaint(self, event):
        if self.InitBuffer():
            self.panel1.Refresh() # buffer changed paint in next event, this paint event may be old
            return
            
        dc = wx.PaintDC(self.panel1)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawcircle(dc)
        
    ''' \\\\\\\\\\\\\\\\\\\\ End of methods used for drawing LEDs. //////////////////// '''
  
        

    def openDiscoveryWindow(self, event):
        
        discoveryFrame(None, self, size = (800,250), style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
        
    def buttonConnectDisconnectPressed(self, event):
        
        if self.screenController.m_connected == False:
            self.connect()
            if self.screenController.m_connected == True:
                self.buttonConnect.SetLabel('Disconnect')
                self.buttonSaveFile.Enable()
        elif self.screenController.m_connected == True:
            self.disconnect()
            if self.screenController.m_connected == False:
                self.buttonConnect.SetLabel('Connect')
                self.buttonSaveFile.Disable()
    
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
            self.PanelUpdateThread(self)
            
            # Plot graphs (panel 3).
            self.GraphPanel = GraphPanel(self, self.panel3)
            
            self.screenController.m_LastPacketTime = self.time.time()*1000
            self.screenController.m_packets = 0
            self.screenController.m_drops = 0 
            self.screenController.m_missedPackets = 0
            self.screenController.m_rxedPacketsAcc = 0
            self.screenController.m_OutOfOrders = 0
            self.screenController.m_Duplicates = 0
    
    def disconnect(self):
        self.screenController.disconnectButtonPressed()
        self.buttonConnect.SetLabel('Connect')
        self.buttonSaveFile.Disable()
        
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
            setPacketRate = self.screenController.m_btnApplyRatePressed(packetRate)
        except Exception as e:
            print e

        self.textBoxRate.SetValue(str(setPacketRate)) # Copy rate back to screen.
    
    def DataTypeFT(self, event):
        print 'Changing data type to FT.'
        self.screenController.changeGageFT(True)
    
    def DataTypeGage(self, event):
        print 'Changing data type to gage.'
        self.screenController.changeGageFT(False)
        
    def SaveFile(self, event):
        filename = self.textBoxSaveFile.GetValue()
        self.screenController.collectDataButtonPressed(filename)
        
        self.buttonSaveFile.SetLabel(self.screenController.m_btnCollectData)
    
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
            config.set('main', 'saveFile', self.textBoxSaveFile.GetValue())
            
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
            
    class PanelUpdateThread:
        
        def __init__(self, main):
            self.main = main
            
            self.timer = wx.Timer(self.main.panel1)
            self.main.panel1.Bind(wx.EVT_TIMER, self.PanelUpdate, self.timer)
            #self.timer.Start(1000/self.main.screenController.UI_UPDATE_HZ) # Updates at 30 Hz
            self.timer.Start(100)
            
            #self.main.panel1.SetDoubleBuffered(False) ######## This should fix flickering
            
            self.status = True
            
            #self.startThread()
        
        def startThread(self):
            import threading
            self.th = threading.Thread(target=self.PanelUpdate)
            self.th.start()
        
        def PanelUpdate(self, event):
            
            #while True:
            if self.main.screenController.m_readingRecords:
                
                try:
                    status1 = self.main.screenController.m_lastSample.getStatusCode1()
                    status2 = self.main.screenController.m_lastSample.getStatusCode2()
                except:
                    print 'No packets received. Try reconnecting or restarting wireless transmitter.'
                    self.timer.Stop()
                    return
                
                # Updating LEDs.
#                self.main.LEDTransducer1  .LEDColour(self.main.screenController.colors[status1       & 0x3])
#                self.main.LEDTransducer2  .LEDColour(self.main.screenController.colors[status1 >>  2 & 0x3])
#                self.main.LEDTransducer3  .LEDColour(self.main.screenController.colors[status1 >>  4 & 0x3])
#                self.main.LEDWLAN         .LEDColour(self.main.screenController.colors[status1 >>  6 & 0x3])
#                self.main.LEDExternalPower.LEDColour(self.main.screenController.colors[status1 >>  8 & 0x3])
#                self.main.LEDBattery      .LEDColour(self.main.screenController.colors[status1 >> 10 & 0x3])
#                
#                self.main.LEDTransducer4  .LEDColour(self.main.screenController.colors[status2       & 0x3])
#                self.main.LEDTransducer5  .LEDColour(self.main.screenController.colors[status2 >>  2 & 0x3])
#                self.main.LEDTransducer6  .LEDColour(self.main.screenController.colors[status2 >>  4 & 0x3])
                self.colourTransducer1   = self.main.screenController.colors[status1       & 0x3]
                self.colourTransducer2   = self.main.screenController.colors[status1 >>  2 & 0x3]
                self.colourTransducer3   = self.main.screenController.colors[status1 >>  4 & 0x3]
                self.colourWLAN          = self.main.screenController.colors[status1 >>  6 & 0x3]
                self.colourExternalPower = self.main.screenController.colors[status1 >>  8 & 0x3]
                self.colourLEDBattery    = self.main.screenController.colors[status1 >> 10 & 0x3]
                self.colourTransducer4   = self.main.screenController.colors[status2       & 0x3]
                self.colourTransducer5   = self.main.screenController.colors[status2 >>  2 & 0x3]
                self.colourTransducer6   = self.main.screenController.colors[status2 >>  4 & 0x3]
                self.panel1.Refresh()
                
                
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
                
                label='%10d \n%10.0f \n%10d \n%10d \n%10d \n%10.2f \n%10d \n%10d' % (self.main.screenController.m_packets, 
                                                                                     packetRate, 
                                                                                     self.main.screenController.m_lastSample.getLatency(), 
                                                                                     self.main.screenController.m_drops, 
                                                                                     self.main.screenController.m_missedPackets,
                                                                                     avgMissed,
                                                                                     self.main.screenController.m_OutOfOrders,
                                                                                     self.main.screenController.m_Duplicates)
                                                                                     
                self.main.textStats.SetLabel(label)
                
                # Forces and moments values.
                self.main.screenController.panel.setSensorData(self.main.screenController.m_lastSample)
                stringForces,stringMoments = self.main.screenController.panel.updatePlot()
                
                self.main.textForcesHeading.SetLabel(self.main.screenController.panel.FUnitsHeading)
                self.main.textMomentsHeading.SetLabel(self.main.screenController.panel.TUnitsHeading)
                
                self.main.textForcesValues.SetLabel(stringForces)
                self.main.textMomentsValues.SetLabel(stringMoments)
                
                self.main.textAxesX.Show()
                self.main.textAxesY.Show()
                self.main.textAxesZ.Show()
                        
                self.main.Refresh()    
                    
            else:
                self.timer.Stop()
                self.main.Refresh()
                self.panelReset()
                return 
            
        def panelReset(self):
            # Setting displays to default
#            self.main.LEDTransducer1  .LEDColour('BLACK')
#            self.main.LEDTransducer2  .LEDColour('BLACK')
#            self.main.LEDTransducer3  .LEDColour('BLACK')
#            self.main.LEDWLAN         .LEDColour('BLACK')
#            self.main.LEDExternalPower.LEDColour('BLACK')
#            self.main.LEDBattery      .LEDColour('BLACK')
#            self.main.LEDTransducer4  .LEDColour('BLACK')
#            self.main.LEDTransducer5  .LEDColour('BLACK')
#            self.main.LEDTransducer6  .LEDColour('BLACK')
            self.main.textStats.SetLabel(' ')
            self.main.textForcesHeading.SetLabel(' ')
            self.main.textMomentsHeading.SetLabel(' ')
            self.main.textForcesValues.SetLabel(' ')
            self.main.textMomentsValues.SetLabel(' ')
            self.main.textAxesX.Hide()
            self.main.textAxesY.Hide()
            self.main.textAxesZ.Hide()
    
    def Quit(self, event):
        self.disconnect()
        self.SaveSettings()
        self.Close()
        
#    def myListener(self, message): # Listener function
#        print message
#        self.textbox1.SetValue(message)


        
class discoveryFrame(wx.Frame):
    
    import DiscoveryClient
    
    def __init__(self, *args, **kwargs):
        
        super(discoveryFrame, self).__init__(*args[:-1], **kwargs)
        self.ipa = '0.0.0.0'
        self.screen = args[1]
        self.basicGUI()
        
    def basicGUI(self):
        
        ''' Window title. '''
        self.SetTitle('Device discovery')
        
        ''' Panel. '''
        panel = wx.Panel(self)
        self.text = wx.StaticText(panel, label='Searching...', pos=(50,25))        
        self.listbox = wx.ListBox(panel, pos=(50,50), size=(700,100), choices=['Waiting...'])
        buttonOk = wx.Button(panel, label='Ok', pos=(50+225,170), size=(100,30))
        buttonOk.Bind(wx.EVT_BUTTON, self.Ok)
        buttonCancel = wx.Button(panel, label='Cancel', pos=(200+225,170), size=(100,30))
        buttonCancel.Bind(wx.EVT_BUTTON, self.Cancel)
        self.Show()
        self.searchThread()
        
    def searchThread(self):
        import threading
        self.th = threading.Thread(target=self.search)
        self.th.start()
        
    def search(self):
        self.screen.screenController.discoverButtonPressed()
        devices = self.screen.screenController.devices
        devicesString = []
        try:
            if len(devices) > 0:
                for i in range(0, len(devices)):
                    #print devices[i].m_ipa, devices[i].m_ipaNetmask, devices[i].m_macstring, devices[i].m_strApplication, devices[i].m_strLocation
                    devicesString.append('%s %s %s %s %s' %(devices[i].m_ipa, devices[i].m_ipaNetmask, devices[i].m_macstring, devices[i].m_strApplication, devices[i].m_strLocation))
        except Exception as e:
            print e
            pass
        self.devicesList = devices
        self.text.SetLabel('Searching... Done.')
        self.listbox.Set(devicesString)
        
    def Ok(self, event):
        try:
            selectedIndex = self.listbox.GetSelection()
            self.ipa = self.devicesList[selectedIndex].m_ipa
            #pub.sendMessage("panelListener", message=self.ipa)
            self.screen.textBoxIpa.SetValue(self.ipa)
        except Exception as e:
            print e
        self.Close()
        
    def Cancel(self, event):
        self.Close()
    
    
        
def main():

    app = wx.App(False)
    mainWindow = mainFrame(None, size = (1050,800), style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
    app.MainLoop()
    
    print 'Done'

if __name__ == '__main__':
    main()