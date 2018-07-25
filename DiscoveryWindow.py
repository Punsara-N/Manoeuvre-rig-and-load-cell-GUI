import wx

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
        self.Destroy()