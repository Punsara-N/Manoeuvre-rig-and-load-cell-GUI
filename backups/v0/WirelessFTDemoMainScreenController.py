'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 01-08-2017
-------------------------------------------------------------------------------------------------
'''

class WirelessFTDemoMainScreenController:
    
    import DiscoveryClient
    import WirelessFTDemoModel
    import WirelessFTDemoProfile
    import time
    import io
    
    m_saveProfile       = False     # Should profile changes be saved on the WNet?
    m_connected         = False     # Whether or not we are successfully connected to a WNet.
    m_readingRecords    = False     # Are we reading records?
    m_collectingData    = False     # Are we collecting data to file?
    m_threadActive      = False     # Is the CollectDataThread is currently active?
    
    m_drops          = 0 # The number of packet drop occurrences thus far, regardless of size.
    m_packets        = 0 # total number of packets received
    m_missedPackets  = 0 # The number of individual packets that have been missed.
    m_rxedPacketsTc  = 10000
    m_rxedPacketsAcc = 0
    m_LastSequence   = 0
    m_LastPacketTime = time.time()*1000
    m_timeAcc        = 0 # The number of individual packets that have been missed.
    m_timeTc         = 500
    m_OutOfOrders    = 0
    m_Duplicates     = 0
    
    m_model = WirelessFTDemoModel.WirelessFTDemoModel() # The application model.
    
    PREF_GAGE_OR_FT                 = 'ftOrGageData' # The preferred display startup (raw data or not).
    
    PREF_USER_ROOT_NODE_PATHNAME    = 'com.FTDemo.preference.Settings' # The preferences user root node pathname.
    
    PREF_DATA_COLLECTION_DIRECTORY  = 'latestCollectionDir' # The latest file-selection window for data collection, a preference keyword.
    
    PREF_LATEST_IP                  = 'latestIPConnectAttempt' # The latest IP setting, a preference keyword
    
    PREF_LAST_WINDOW_WIDTH          = 'latestWindowWidth' # The latest window width setting, a preference keyword
    
    PREF_LAST_WINDOW_HEIGHT         = 'latestWindowHeight' # The latest window height setting, a preference keyword
    
    PREF_LAST_X_POSITION            = 'latestXWindowPosition' # The latest x window position
    
    PREF_LAST_Y_POSITION            =  'latestYWIndowPosition' # The latest y window position
    
    PREF_FORCE_UNIT                 = 'forceUnitConversion' # The last force unit selected
    
    PREF_TORQUE_UNIT                = 'torqueUnitConversion' # The last torque unit selected
    
    PREF_DISPLACEMENT_UNIT          = 'displacementUnits' # The last displacement unit selected
    
    PREF_ROTATIONS_UNIT             = 'rotationsUnits' # The last rotations unit selected
    
    # Rotation/Displacement string prefixes (loop to use one for each sensor).
    PREF_DISPLACEMENT_X = 'displacementX'
    PREF_DISPLACEMENT_Y = 'displacementY'
    PREF_DISPLACEMENT_Z = 'displacementZ'
    
    PREF_ROTATIONS_X    = 'rotationsX'
    PREF_ROTATIONS_Y    = 'rotationsY'
    PREF_ROTATIONS_Z    = 'rotationsZ'
    
    # The last IP settings.
    PREF_BAND            = 'band'
    PREF_DHCP            = 'dhcp'
    PREF_SSID            = 'ssid'
    PREF_IP_ADDRESS      = 'ipAddress'
    PREF_DEFAULT_GATEWAY = 'defaultGateway'
    PREF_SUBNET_MASK     = 'subnetMask'
    
    PREFERRED_WINDOW_WIDTH = 912 # The preferred window width
    
    PREFERRED_WINDOW_HEIGHT = 500 # The preferred window height
    
    PREFERRED_GRAPH_WIDTH = 510 # The preferred graph width
    
    PREFERRED_GRAPH_HEIGHT = 494 # The preferred graph height
    
    UPPER_ANCHOR = 21 # Graph set upper anchor
    
    LOWER_ANCHOR = 261 # Graph set lower anchor
    
    BOX1_LEFT_ANCHOR = 232 # Graph set 1's left anchor
    
    BOX2_LEFT_ANCHOR = 741 # Graph set 2's left anchor
    
    BOX1_RIGHT_ANCHOR = 509 # Graph set 1's right anchor
    
    BOX2_RIGHT_ANCHOR = 0 # Graph set 2's right anchor
    
    UI_UPDATE_HZ = 30.0 # Display new data at this rate.
    
    ''' Processes new data from wireless FT system. '''
    class m_sampleChangeListener:
        
        def __init__(self):
            pass
    
    ''' Processes user request to change type of data coming from sensor. '''    
    class m_ftOrGageChangeListener:
        
        def __init__(self):
            pass
        
    ''' Sets the WNet profile prior to initialization. '''
    def setProfile(self, profile, save):
        self.m_profile     = profile
        self.m_saveProfile = save
        #m_applyRate.setText(m_profile.m_rate); // Put current rate into the Apply Rate text field.
        #m_vBoxPacketStats.setVisible(false);
        
    ''' Initializes the controller class. '''    
    class initialize:
        
        def __init__(self):
            pass
    
    ''' Opens window to extract .DAT files from a connected MicroSD and rewrite them locally as .CSV files. '''
    def openSDWindow(self):
        pass
    
    ''' Opens the window to download files to the WNet. '''
    def openFileUploadWindow(self):
        pass
    
    ''' Opens the calibration view window. '''
    def openCalibrationWindow(self):
        pass
    
    ''' Opens the About window. '''
    def openAboutWindow(self):
        pass
    
    ''' Opens the Auto-Cal window. '''
    def openAutoCalWindow(self):
        pass
    
    ''' Get conversion factors. '''
    def getConversionFactors(self, panel, transducer):
        cal    = self.m_model.readActiveCalibration() # Send CAL command to get calibration information.       
        serial = self.m_model.cal.getSerialNumber() # Get calibration serial number to label the graph with.      
        date   = self.m_model.cal.getCalibrationDate() # Get calibration date
        title  = 'Transducer ' + str(transducer + 1) + ' | ' + serial # Transducer is origin 1 to the user
        
        if '1970/01' in date:
            title = title + ' UNCALIBRATED'
            
        ############## panel.setTitle(title); // Label the graph with the Transducer number and the calibration serial number.
            
        forceUnits  = self.m_profile.getForceUnits().lower() # Get profile force  units
        torqueUnits = self.m_profile.getTorqueUnits().lower() # Get profile torque units
        
        if forceUnits == 'default': # If the force units are "default"
            forceUnits = self.m_model.cal.getForceUnits() # get the force units from the current calibration.
        
        if torqueUnits == 'default': # If the force units are "default",
            torqueUnits = self.m_model.cal.getTorqueUnits() # get the force units from the current calibration.
            
        conversions = [1, 1, 1, 1, 1, 1]
        
        try:
            conversions = self.m_model.cal.getForceTorqueConversionFactors(forceUnits, torqueUnits, transducer)
        except Exception as e:
            print 'Exception getting output F/T conversion factors, using factor of 1:'
            print e
            
        forceConv  = conversions[0] / self.m_model.cal.getCountsPerUnitForce () # force
        torqueConv = conversions[3] / self.m_model.cal.getCountsPerUnitTorque() # torque
        
        panel.setConversions     (forceConv,  torqueConv)
        panel.setForceTorqueUnits(forceUnits, torqueUnits)
    
    ''' Refreshes information about active calibrations. '''
    def refreshCalibrationInformation(self):
        try:
            userMode   = self.m_model.SetTechnicianMode() # Set technician mode
            #transducer = 0
            for transducer in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS):
                if self.m_model.m_sensorActive[transducer]: # If this transducer is active,
                    panel = self.panel    
                    self.m_model.setActiveSensor(transducer) # issue TRANS n command.
                    self.getConversionFactors(panel, transducer) # Issue CAL command.
                    
            self.m_model.RestoreWnetMode(userMode) # restore Wnet mode
        except Exception as e:
            print e
            self.disconnectButtonPressed()
            
    ''' Connects to WNet when the enter key is pressed in the host text field. '''
    def txtFieldSensorHostNameEnter(self):
        pass
    
    ''' Opens the Discovery Results window, which continuously searches for active Wireless F/Ts
    in range using the @RTADiscoveryProtocol package. The window contains a list of results to choose from. '''
    def discoverButtonPressed(self):
        DC = self.DiscoveryClient.DiscoveryClient()
        self.devices = DC.discoverRTADevicesLocalBroadcast()
        
        try:
            if len(self.devices) > 0:
                print '\nTotal number of devices found: %i' % len(self.devices)
                for i in range(0, len(self.devices)):
                    print self.devices[i].m_ipa, self.devices[i].m_ipaNetmask, self.devices[i].m_macstring, self.devices[i].m_strApplication, self.devices[i].m_strLocation
        except Exception as e:
            print e
            
    def m_ApplyRateChanged(self):
        self.m_btnApplyRatePressed()
        
    def m_btnApplyRatePressed(self, rate):
        try:
            packetRate = int(rate) # Get rate from screen
        except Exception as e:
            print e
            packetRate = self.MIN_UDP_RATE
            
        if packetRate > self.MAX_UDP_RATE:
            packetRate = self.MAX_UDP_RATE
            
        if packetRate < self.MIN_UDP_RATE:
            packetRate = self.MIN_UDP_RATE
            
        print 'Applying %d Hz rate...' % packetRate
        
        self.m_profile.setRate  (     packetRate) # Copy rate to profile
        
        try:
            self.m_model.applyRate(packetRate) # Copy rate to WNet unit
        except Exception as e: # If the WNet is not connected,
            print e
            pass # do not do anything rash.
            
        return packetRate
            
    ''' The possible LED color combinations. '''
    colors = ['BLACK', 
              '#ff1400', # brighter red   than Color.RED
              '#14ff00', # brighter green than Color.GREEN
              '#ff7f00'] # orange
    SATRED = '#cc0000' # Saturation red
    
    ''' Called when the Show Packet Statistics CheckBox changes. '''
    def ShowPacketStatsChanged(self):
        # This is done in GUI.py already
        pass
    
    ''' Connects to the WNet. '''
    def connectButtonPressed(self, ip, profile_name = 'DefaultProfile.xml'):
        
        print '\nConnecting...\n'
        
        self.profile_name = profile_name
        self.m_profile = self.WirelessFTDemoProfile.WirelessFTDemoProfile()
        self.m_profile.WirelessFTDemoProfile(self.profile_name) # Loading profile.
        self.m_saveProfile = False # Should these changes be saved to the WNet itself at connect-time?
        self.m_controller = None # Probably not needed
        self.m_bufferedWriter = None
        
        # PROFILE SETTINGS
        print '\nProfile settings:'
        print '-----------------\n'
        print 'Active Calibration:', self.m_profile.getActiveCalibration(0)
        print 'Calibration:', self.m_profile.getCalibrationCommand(0)
        print 'Displacement Units:', self.m_profile.getDisplacementUnits(0)
        print 'Displacement Values:', self.m_profile.getDisplacementValues(0)
        print 'Filter:', self.m_profile.getFilterCommand(0)
        print 'Filter Type:', self.m_profile.getFilterType(0)
        print 'Filter Value:', self.m_profile.getFilterValue(0)
        print 'Force Units:', self.m_profile.getForceUnits()
        print 'Rate:', self.m_profile.getRateCommand()
        print 'Rotation Units:', self.m_profile.getRotationUnits(0)
        print 'Rotation Values:', self.m_profile.getRotationValues(0)
        print 'SD:', self.m_profile.getSDCommand()
        print 'Torque Units:', self.m_profile.getTorqueUnits()
        print 'Transducer:', self.m_profile.getTransducerCommand(0)
        print 'Transformation Matrix:', self.m_profile.getTransformationMatrix(0)
        print  'XPWR:', self.m_profile.getXPWRCommand(0)
        
        if not self.m_connected: # and len(self.devices)>0:
            try:
                
                self.m_model.connect(ip, self.m_profile, self.m_saveProfile, self.m_controller)

                print '\nConnected.\n'                
                
                self.m_readingRecords = True
                self.CollectData(self)
                
                self.setupPanels() ############## Setup panels.
                self.refreshCalibrationInformation()
                
                ftData = True # So that I will get forces/moments instead of gage values.
                self.setOnlineMode(True, ftData) # Switch to online UI mode and set data type.
                self.changeGageFT(ftData)
                
                self.m_connected = True
                
                self.connectingFailed = False # Used to pop-up a dialog box saying connection failed.
                
                ######### Begin animation.
                
            except Exception as e:
                print e
                self.connectingFailed = True
                
        else:
            self.disconnectButtonPressed()
    
    ''' Changes active UI controls based on whether or not we've connected with a WNet. '''
    def setOnlineMode(self, connected, ftData):
        pass
    
    ''' Dynamically creates panels to maximize space when displayed on the main screen. '''
    def setupPanels(self):
        sensors = 0
        for m_xpwr in self.m_profile.m_xpwr:
            if m_xpwr == 'ON':
                sensors += 1
        print 'Number of sensors:', sensors
        
        ########### Create graphs for each Transducer and add them to the screen.
        self.panel = self.CreatePanel()
        self.panel.setSensorIndex(0)
    
    ''' Create a panel, and handle its Bias and Un-bias buttons. '''
    def CreatePanel(self):
        import WirelessFTSensorPanel
        panel = WirelessFTSensorPanel.WirelessFTSensorPanel(self.m_profile)
        return panel
    
    ''' Close the UDP stream and TCP connection to the current device, then clears the graphs from the GUI. '''    
    def disconnectButtonPressed(self):
        
        print '\nDisconnecting...\n'
        
        self.m_readingRecords = False
        
        if self.m_threadActive:
            try:
                self.time.sleep(1)
            except Exception as e:
                print e
                
        self.stopCollectingData()
                
        self.m_model.disconnect() # Close TCP/UDP connections to the sensor.
        
        try:
            self.setOnlineMode(False, False) # Switch to offline UI. // This function really should be called from a different thread
        except Exception as e:
            print e
            
        self.m_connected = False
        
        print '\nDisconnected.\n'
        
    ''' Called when user presses button to choose a data collection file. '''
    def chooseDataCollectionFilePressed(self):
        pass
    
    ''' Called when button to collect data is pressed. '''
    def collectDataButtonPressed(self, name):
        import datetime
        if self.m_collectingData:
            self.stopCollectingData()
        else:
            try:
                filename = name # Get filename from text box
                extIndex = filename.rfind('.')
                
                if extIndex < 0: # Find last . (if any)
                    extension = '.csv'
                else:
                    extension = filename[extIndex:]
                    filename = filename[:extIndex]
                
                currentDateTimeString = str(datetime.datetime.today()) # E.g.: '2017-07-28 17:26:16.786000'
                currentDateString = currentDateTimeString.split(' ')[0] # E.g.: '2017-07-28'
                currentTimeString = currentDateTimeString.split(' ')[1] # E.g.: '17:26:16.786000'
                currentYear       = currentDateString.split('-')[0] # E.g.: '2017'
                currentMonth      = currentDateString.split('-')[1] # E.g.: '07'
                currentDay        = currentDateString.split('-')[2] # E.g.: '28'
                currentHour       = currentTimeString.split(':')[0] # E.g.: '17'
                currentMinute     = currentTimeString.split(':')[1] # E.g.: '26'
                currentSecond     = currentTimeString.split(':')[2].split('.')[0] # E.g.: '16'
                currentMilliSecond= currentTimeString.split(':')[2].split('.')[1][:3] # E.g.: '786'
                
                filename = filename + '_' + currentYear + '_' + currentMonth + '_' + currentDay + '_' + currentHour + '_' + currentMinute + '_' + currentSecond + '_' + currentMilliSecond + extension
                                
                print 'Saving data to file:', filename
                
                self.startCollectingData(filename)
                
            except Exception as e:
                print e
                try:
                    message = 'Data collection failed.'
                    print message
                except Exception as e:
                    print e
                    
        if self.m_collectingData:
            self.m_btnCollectData = 'Stop'
            pass
        else:
            self.m_btnCollectData = 'Collect Data'
            pass
        
    ''' Begins writing data to a file by setting the collect data flag and inserting the header into a new .csv or .txt file. '''
    def startCollectingData(self, filename):
        if self.m_collectingData:
            print 'Data collection already in progress.'
        else:
            
            self.m_bufferedWriter = self.io.BufferedWriter(self.io.FileIO(filename, 'w'))
            
            # Column headers:
            self.m_bufferedWriter.write('Time, Mask, Bat, Sts1, Sts2, Seq #')
            channelNames = ['FX', 'FY', 'FZ', 'TX', 'TY', 'TZ']
            gageNames = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5']
            
            for transducer in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS):
                if self.m_model.m_sensorActive[transducer]:
                    for axis in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES):
                        self.m_bufferedWriter.write(',T' + str(transducer + 1) + (channelNames[axis] if self.panel.m_forceTorqueButton else gageNames[axis]))
                        
            self.m_bufferedWriter.write('\n')
            
            self.m_collectingData = True
      
    class CollectData:
        
        import time
        
        # Separate from the UDP receive timeout, 
        # this is the longest time the Demo is
        # allowed to run with no new data.
        ###THRESHOLD = 60000/1000 # seconds
        THRESHOLD = 10 # seconds
        
        warningShown = False # Did we fail to retrieve the last sample buffer?
        reconnecting = False # Are we trying to re-establish communication?
        
        def __init__(self, main):
            self.main = main
            self.CollectDataThread()
            
        # Continuously reads samples from the WNet and (optionally) writes them to a .txt or .csv file.
        def CollectDataThread(self):
                
            import threading
            
            th = threading.Thread(target=self.run)
            th.start()
        
        # Begin reading records.
        # If the time between records
        # exceeds the 1-minute timeout threshold, attempt to
        # handle a disconnect scenario.
        # If the file-write flag is set, also record each of
        # these records to the user-specified .csv or .txt file.
        def run(self):
            self.main.m_threadActive   = True
            lastSuccess = self.time.time()
            
            while(self.main.m_readingRecords):
                try:
                    #sample = self.main.m_model.m_sensor                    
                    #self.main.m_model.m_sensor.readStreamingSamples() # Get all packets from next UDP data block
                    #samples = [sample]
                    samples = self.main.m_model.m_sensor.readStreamingSamples() # Get all packets from next UDP data block
                    
                    self.warningShown = False # Response recieved, reset the message flag.
                    for s in samples: # For each sample block in the UDP data block,                        
                        self.main.CalculateDataBlockStatistices(s) # calculate statistics.
                        ######m_sampleProperty.set(s) # Put the data where the listener can plot it.
                        if self.main.m_collectingData:
                            self.main.WriteDataBlockToFile(s)
                            
                        ######
                        #self.main.WriteDataBlockToFile(s)
                        #print self.main.m_bufferedWriter
                        ######
                    try:        
                        self.main.m_lastSample = samples[0]
                    except:
                        print 'No samples read.'
                            
                    if self.reconnecting:
                        self.reconnecting = False
                    lastSuccess = self.time.time()
                except Exception as e:
                    print e
                    self.reconnecting = True
                    currentTime = self.time.time()
                    if ((currentTime - lastSuccess) > self.THRESHOLD):
                        try:
                            self.main.disconnectButtonPressed() # This function really should be called from the FX application thread
                        except Exception as e:
                            print e
                    else:
                        if not self.warningShown:
                            print 'Connection lost, attempting to re-establish UDP ...'
                            self.warningShown = True
            self.main.m_threadActive = False
                        
                        
    def CalculateDataBlockStatistices(self, s):
        thisSequence = s.getSequence()                              # Get the new sequence number
        if thisSequence > self.m_LastSequence:                      # If this packet is in order,
            self.m_packets  += 1                                    # Count the packet
            missed      = thisSequence - self.m_LastSequence - 1    # Calculate number of missed packets (should be 0)
            self.m_missedPackets += missed                          # Calculate total number of missed packets
            if missed>0:                                            # If any packets were missed,
                self.m_drops += 1
                for i in range(0, missed):
                    self.m_rxedPacketsAcc += 1.0 - (self.m_rxedPacketsAcc / self.m_rxedPacketsTc) # single-pole IIR filter
                self.m_rxedPacketsAcc += 0.0 - (self.m_rxedPacketsAcc / self.m_rxedPacketsTc)     # single-pole IIR filter
            currentTime  = self.time.time()*1000                   # Calculate packet rate
            deltaTime    = currentTime - self.m_LastPacketTime
            self.m_LastPacketTime  = currentTime
            self.m_timeAcc        += deltaTime - (self.m_timeAcc / self.m_timeTc) # single-pole IIR filter
        elif thisSequence < self.m_LastSequence:                    # If this packet is out-of-order,
            self.m_OutOfOrders += 1                                 # count it.
        else:                                                       # If the packet was a duplicate,
            self.m_Duplicates += 1                                  # count it.
        self.m_LastSequence = thisSequence                          # Save sequence number for next time.
    
    def WriteDataBlockToFile(self, s):
        
        self.m_bufferedWriter.write('%d, %2x, %d, %8x, %8x, %d' %(s.getTimeStamp(), s.getSensorMask(), s.getBatteryLevel(), s.getStatusCode1(), s.getStatusCode2(), s.getSequence()))
        
        for transducer in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS): # For each Transducer,
            if self.m_model.m_sensorActive[transducer]: # If this Transducer is active,
                # Note: 's.getFtOrGageData()[transducer]' is a row vector, need to convert to a column for matrix multiplication.
                getFtOrGageData = []
                for v in s.getFtOrGageData()[transducer]:
                    getFtOrGageData.append([v])
                data = self.matrixMult(self.m_profile.getTransformationMatrix(transducer), getFtOrGageData)
                for axis in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES): # For each channel,
                    value = data[axis][0] # get the data value.
                    self.m_bufferedWriter.write(', ' + str(value)) # Save converted value
        self.m_bufferedWriter.write('\n')
    
    ''' Multiplies the matrices representing transformations and raw gage data, respectively. '''    
    def matrixMult(self, A, B):
        # Creating size of results matrix.
        results = []
        numOfRowsInMatrixA = len(A)
        numOfColoumnsInMatrixB = len(B[0])
        for ii in range(0, numOfRowsInMatrixA): # This will create the right number of rows.
            results.append([])
            for jj in range(0, numOfColoumnsInMatrixB): # This will create the right number of columns.
                results[ii].append(0)
    
        # Iterate through rows of A.
        for i in range(len(A)):
           # Iterate through columns of B
           for j in range(len(B[0])):
               # Iterate through rows of B
               for k in range(len(B)):
                   results[i][j] += A[i][k] * B[k][j]
                  
        return results
        
    ''' Closes the file to which data is being collected and stops writing data. '''
    def stopCollectingData(self):
        self.m_collectingData = False
        self.m_LastPacketTime = self.time.time()*1000
        self.m_packets        = 0
        self.m_drops          = 0
        self.m_missedPackets  = 0
        self.m_rxedPacketsAcc = 0
        self.m_OutOfOrders    = 0
        self.m_Duplicates     = 0
        
        try:
            self.m_bufferedWriter.close() # Close buffer
        except Exception as e:
            print 'Exception closing data file:'
            print e

    ''' Change data between Gage and FT displays. '''
    # forceTorqueButton true if forceTorque button is selected
    def changeGageFT(self, forceTorqueButton):
        try:
            self.m_model.selectGageOrFTData(forceTorqueButton)
            self.panel.setDataDisplay(forceTorqueButton)
        except Exception as e:
            print e
            self.disconnectButtonPressed()
        
        # Change the preferred setting.
        #prefs = m_prefsRoot.node(PREF_USER_ROOT_NODE_PATHNAME);
        #prefs.putBoolean(PREF_GAGE_OR_FT, forceTorqueButton);
        
    ''' Updates error log on main screen. Intended to be used with Platform.runLater to make it thread safe. '''
    def UpdateErrorLog(self):
        pass
    
    ''' Disconnects from the WNet automatically when the application is closed. '''
    def OnCloseRequest(self):
        if self.m_connected:
            self.disconnectButtonPressed()
    
    def __init__(self):
        self.MIN_UDP_RATE =    5
        self.MAX_UDP_RATE = 4000
    
    
    
def main():
    
    import time
    
    print("\nStarting...")

    mainScreen = WirelessFTDemoMainScreenController()
    #mainScreen.discoverButtonPressed()
    mainScreen.connectButtonPressed('192.168.0.10')
    time.sleep(0.01)
    mainScreen.disconnectButtonPressed()
    
    print("\nCode is finished.")
        

if __name__ == '__main__':
    main()