import wx

class configFrame(wx.Frame):
    
    from WirelessFTDemoProfile import WirelessFTDemoProfile
    from WirelessFTDemoModel import WirelessFTDemoModel
    
    def __init__(self, *args, **kwargs):
        super(configFrame, self).__init__(*args[:-1], **kwargs)
        
        ''' Constants. '''
        self.MIN_UPD_RATE = 5
        self.MAX_UPD_RATE = 4000
        self.MAX_OVERSAMPLING = 32 # The largest valid value for oversampling.
        self.MAX_TAPS = 32 # The maximum amount of averaging samples allowed per transducer.
        self.MAX_TIME_CONSTANT = 32767 # The maximum IIR time constant allowed per transducer.
        self.m_forceLabels  = ["Default", "lbf",    "klbf",   "N",   "kN",   "g",     "kg"  ] # Force  ComboBox entries
        self.m_torqueLabels = ["Default", "lbf-in", "lbf-ft", "N-m", "N-mm", "kg-cm", "kN-m"] # Torque ComboBox entries
        self.FIRST_PAGE = 0
        self.MODEL_PAGE = 1
        self.NTP_PAGE   = 2
        self.FCU_PAGE   = 3
        self.TOOL_PAGE  = 4
        self.MAX_PAGE   = 5 # The largest page index possible.
        
        ''' Fields. '''
        self.m_pageIndex = 0 # The current wizard/window page index.
        self.m_wizardProfile = self.WirelessFTDemoProfile() # This dummy profile represents the state of the Wizard's UI and is used to write the XML for the new profile when the Finish button is pressed.
        self.m_filCalTransducer = None # The active transducer and calibrations for which settings are being changed.
        self.m_ToolTransformTransducer = None # The active transducer for which transformation settings are being changed.
    
        self.basicGUI()
        
    def basicGUI(self):
        
        ''' Window title. '''
        self.SetTitle('Profile configuration (This window is under construction. Please use the JAVA demo to create/edit profiles)')
        
        ''' Panel. '''
        panel = wx.Panel(self)
        #self.text = wx.StaticText(panel, label='This window is under construction. Please use the JAVA demo to create/edit profiles.', pos=(50,25))        
        #self.listbox = wx.ListBox(panel, pos=(50,50), size=(700,100), choices=['Waiting...'])
        buttonOk = wx.Button(panel, label='Ok', pos=(275,700), size=(100,30))
        #buttonOk.Bind(wx.EVT_BUTTON, self.Ok)
        buttonCancel = wx.Button(panel, label='Cancel', pos=(200+225,700), size=(100,30))
        buttonCancel.Bind(wx.EVT_BUTTON, self.Cancel)
        
        # Number of transducers that can be connected to transmitter.
        position = [10,50]
        wx.StaticText(panel, label='Transducer ports on device:', pos=(0+position[0], 0+position[1]))
        self.m_wnet3Toggle = wx.ToggleButton(panel, label="3", pos=(0  +position[0], 0+position[1]), size=(100, 30))
        self.m_wnet6Toggle = wx.ToggleButton(panel, label="6", pos=(100+position[0], 0+position[1]), size=(100, 30))
               
        # Active transducers
        position = [10,100]
        self.m_t1Toggle = wx.ToggleButton(panel, label="Transducer 1", pos=(0  +position[0], 0+position[1]), size=(100, 30))
        self.m_t2Toggle = wx.ToggleButton(panel, label="Transducer 2", pos=(100+position[0], 0+position[1]), size=(100, 30))
        self.m_t3Toggle = wx.ToggleButton(panel, label="Transducer 3", pos=(200+position[0], 0+position[1]), size=(100, 30))
        self.m_t4Toggle = wx.ToggleButton(panel, label="Transducer 4", pos=(300+position[0], 0+position[1]), size=(100, 30))
        self.m_t5Toggle = wx.ToggleButton(panel, label="Transducer 5", pos=(400+position[0], 0+position[1]), size=(100, 30))
        self.m_t6Toggle = wx.ToggleButton(panel, label="Transducer 6", pos=(500+position[0], 0+position[1]), size=(100, 30))
        self.m_transducers = [self.m_t1Toggle, self.m_t2Toggle, self.m_t3Toggle, self.m_t4Toggle, self.m_t5Toggle, self.m_t6Toggle]
        
        # Rate text box
        position = [10,150]
        wx.StaticText(panel, label='Packet rate (5 - 4000):', pos=(0+position[0], 0+position[1]))
        self.m_txtRate = wx.TextCtrl(panel, value='', pos=(150+position[0], 0+position[1]), size=(150,20))
        wx.StaticText(panel, label='packets/second', pos=(310+position[0], 0+position[1]))
        
        # Oversampling text box
        position = [10,200]
        wx.StaticText(panel, label='Oversampling rate:', pos=(0+position[0], 0+position[1]))
        self.m_txtOversamp = wx.TextCtrl(panel, value='', pos=(150+position[0], 0+position[1]), size=(150,20))
        wx.StaticText(panel, label='times', pos=(310+position[0], 0+position[1]))
        
        # SD card check box
        position = [10,250]
        self.m_chkSD = wx.CheckBox(panel, label="Also save transducer data to MicroSD card", pos=(0+position[0], 0+position[1]))
        
        # Notes
        position= [10,300]
        wx.StaticText(panel, label='Notes:', pos=(0+position[0], 0+position[1]))
        self.m_Notes = wx.TextCtrl(panel, value='', pos=(150+position[0], 0+position[1]), size=(400,150), style = wx.TE_MULTILINE)
        
        # Force and torque combo boxes
        position = [10,600]
        self.cmbForce = wx.ComboBox(panel, value="", pos=(0+position[0], 0+position[1]), size=(150,20), choices=self.m_forceLabels)
        self.cmbTorque = wx.ComboBox(panel, value="", pos=(200+position[0], 0+position[1]), size=(150,20), choices=self.m_torqueLabels)
        
        self.Show()
        
    def Cancel(self, event):
        self.Close()
        self.Destroy()
        
    ''' Sets the profile for this controller to modify. '''
    def setProfile(self):
        pass # SEE JAVA CODE
    
    ''' Copy the settings from the XML file to the working variables. '''
    def setupWizard(self):
        
        # Set active transducers.
        for transducer in range(0, self.WirelessFTDemoModel.MAX_SENSORS):
            xpwr = self.m_wizardProfile.m_xpwr[transducer]
            if 'ON' in xpwr:
                self.m_transducers[transducer].SetValue(True)
            else:
                self.m_transducers[transducer].SetValue(False)
                
        # Apply general settings from the XML file to the working copes.
        self.m_wizardProfile.getForceUnits() ################
        self.m_wizardProfile.getTorqueUnits()################
                
        self.m_txtRate.SetValue(self.m_wizardProfile.m_rate)
        self.m_txtOversamp.SetValue(self.m_wizardProfile.m_oversampling)
        self.m_chkSD.SetValue(self.m_wizardProfile.m_sd=='ON')
        self.m_Notes.SetValue(self.m_wizardProfile.m_Notes)
        
        if self.m_wizardProfile.m_Wnet == 6:
            self.m_wnet3Toggle.SetValue(False)
            self.m_wnet6Toggle.SetValue(True)
        else:
            self.m_wnet3Toggle.SetValue(True)
            self.m_wnet6Toggle.SetValue(False)
        