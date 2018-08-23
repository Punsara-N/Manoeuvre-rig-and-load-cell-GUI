'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 21-06-2017
-------------------------------------------------------------------------------------------------
'''

''' Represents the connected WNet and its state. '''
class WirelessFTDemoModel:
    
    import logging
    import IPSettings
    import WirelessFTSensor
    import Calibration
    
    Cal1Serial          = ''
    Cal1PartNumber      = ''
    Cal1Date            = ''
    Cal1Force           = ''
    Cal1Torque          = ''
    
    Cal2Serial          = ''
    Cal2PartNumber      = ''
    Cal2Date            = ''
    Cal2Force           = ''
    Cal2Torque          = ''
    
    Cal3Serial          = ''
    Cal3PartNumber      = ''
    Cal3Date            = ''
    Cal3Force           = ''
    Cal3Torque          = ''
    
    ActiveCalibration   = 0
    ActiveTransducer    = 0
    Matrix              = [[]]
    
    PREF_USER_ROOT_NODE_PATHNAME = "com.FTDemo.preference.Settings"  # The preferences user root node pathname.
    PREF_LATEST_IP               = "latestIPConnectAttempt"          # The latest IP setting, a preference keyword.
    
    m_udpRate        = -1  # The current UDP packet transfer rate.
    MAX_SENSORS      =  6  # The maximum number of Transducers in a WNet. 
    MAX_CALIBRATIONS =  3  # The maximum number of calibrations each sensor may have.
    NUM_AXES         =  6  # The number of gages on a sensor.
    m_sensorActive = [False, False, False, False, False, False] # Keeps track of active sensors. 
    m_sensor = None
    m_flagFileUploadComplete = False # Indicates that a file upload is complete (typically firmware upgrades).
    
    logging.basicConfig(filename='wirelessft.log') # An error log for the application.
    
    def __init__(self):
        
        #import WirelessFTDemoMainScreenController
        #import WirelessFTDemoProfile
        #import Calibration
        #import WirelessFTSensor
        
        #self.m_sensor = WirelessFTSensor.WirelessFTSensor() # Used to communicate with the WNet over Telnet/UDP.
        #m_controller = WirelessFTDemoMainScreenController()
        #self.profile = WirelessFTDemoProfile.WirelessFTDemoProfile()
        self.m_flagReadStreaming = False # Indicates that we are reading streaming data. 
        self.m_sensorAddressOrHostName = '' # The WNet's IP Address.
        self.m_fileUploadProgress = 0 # The progress of the file/firmware upload.
    
    '''
    Gets the percentage progress of the latest file upload.
    @return The percentage 0-100 of the file upload process.
    '''
    def fileUploadProgress(self):
        return self.m_fileUploadProgress
    
    '''    
    Sets the UDP Transfer rate for this model.
    @param rate How many ADC reads are between each sent packet.
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''
    def applyRate(self,rate,oversample=1): 
        self.m_sensor.sendTelnetCommand("RATE " + str(rate) + " " + str(oversample), True)
    
    '''    
    Gets whether or not F/T records will also be written to the MicroSD card.
    @return True if the MicroSD is recording, false otherwise.
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''
    def getSDRecording(self):
        if 'ON' in self.sendCommandAndWaitForResponse("SDREC").upper():
            return True
        else:
            return False
            
    '''
    Set Technician Mode
    @return previous user mode
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def SetTechnicianMode(self):
        response = self.sendCommandAndWaitForResponse("TECHNICIAN ?").upper() # See what terminal mode we are in.
        userMode = 'USER' in response
        if userMode:                                            # If we are in user mode,
            self.sendCommandAndWaitForResponse('TECHNICIAN')    # set technician mode.
        return userMode
        
    '''
    Restore WNet Mode
    @param userMode  true = user, false = technician
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def RestoreWnetMode(self, userMode):
        if userMode:                                    # If we were in user mode,
            self.sendCommandAndWaitForResponse("USER")  # restore user mode.

    def connect(self, ipAddress, profile, save, m_controller):
        
        self.m_sensorAddressOrHostName      = ipAddress
        self.m_sensor                       = self.WirelessFTSensor.WirelessFTSensor()
        self.m_sensor.WirelessFTSensor(self.m_sensorAddressOrHostName)
        self.m_flagReadStreaming            = True
    
        ''' Ensure the active transducers match the xpwr commands sent. '''
        for transducer in range(0, self.MAX_SENSORS):
            power = profile.m_xpwr[transducer].upper()
            self.m_sensorActive[transducer] = 'ON' in power
    
        self.sendCommandAndWaitForResponse(profile.getRateCommand())    # Send RATE command.
        self.sendCommandAndWaitForResponse('T OFF')                     # Ensure packet transmit is off.
        userMode = self.SetTechnicianMode()                             # Set technician mode.
        
        if profile.m_ntpUse and len(profile.m_ntpServer) > 0:           # If NTP is selected, and there is an NTP server specified,
            self.setNtpParameters(profile)                              # set the NTP parameters.
        else:
            self.setTimeAndDate()                                       # Set time/date from the system clock.
            
        self.sendStartupCommands(profile)                               # Send startup commands from the WNet profile.       
        self.RestoreWnetMode(userMode)                                  # restore Wnet mode
        self.sendCommandAndWaitForResponse('T ON')                      # WNet has been prepared, ensure packet transmit is on.
        
        if save:                                                        # If the "Save profile settings to my Wireless F/T" box is checked,
            self.sendCommandAndWaitForResponse('SAVEALL')               # save changes.
            
        '''
        Initialize the connection for the data collection thread
        and retrieve the mask that identifies active sensors.
        '''
        assert self.m_sensor != None, "CollectDataThread can't run because sensor is null."

        
        try:
            self.m_sensor.startStreamingData()
            pass
        except Exception as e:
            logging.critical(e)
            
    '''
    Sets the time and date within the WNet to
    match the time of the Java Virtual Machine.
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def setTimeAndDate(self):
        
        import time
        import datetime
        
        self.sendCommandAndWaitForResponse("NTP ENA 0") # Turn off NTP.
        
        millis = int(round(time.time() * 1000)) + 28 # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0), add fudge factor
        date = datetime.datetime.fromtimestamp(millis/1000.0)
        ''' Need date and time in this format: "yyyy/MM/dd HH:mm:ss.SSS" as a string. '''
        dateFormat = '%Y/%m/%d %H:%M:%S.%f'
        dateString = date.strftime(dateFormat)[:-3]
        dateAndTime = dateString.split(' ')
        
        self.sendCommandAndWaitForResponse("NET DATE " + dateAndTime[0])
        self.sendCommandAndWaitForResponse("NET TIME " + dateAndTime[1])
        
    '''
    Sets the NTP parameters within the WNet.
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException 
    '''
    def setNtpParameters(self, profile):
        if profile.m_ntpDst:
            ntpDsp = 'ON'
        else:
            ntpDsp = 'OFF'
    
        self.sendCommandAndWaitForResponse('NTP SERVER ' + profile.m_ntpServer)
        self.sendCommandAndWaitForResponse('NTP ZONE '   + '{:2d}{:2d}'.format(profile.m_ntpOffsetHours, profile.m_ntpOffsetMinutes))
        self.sendCommandAndWaitForResponse('NTP DST '    + ntpDsp)
        self.sendCommandAndWaitForResponse('NTP ENA 1')
    
    '''
    Gets the active calibrations from the WNet.
    @return the active calibrations from the WNet
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def getActiveCalibrations(self):
        response = ''
        lines = ['']
        calibs = [0, 0, 0, 0, 0, 0]
        transducer = 0
        calibration = 0
        
        response = self.sendCommandAndWaitForResponse("CALIB")
        lines    = response.split("\r\n") # Split response into individual lines.
        
        for i in range(0, len(lines)):
            line = lines[i]
            fields = line.strip().split() # Split this line into individual tokens.
            if len(fields) >= 2:
                try:
                    transducer  = int(fields[0]) - 1 # Transducer  is origin 1 to the user
                    calibration = int(fields[1]) - 1 # Calibration is origin 1 to the user
                except:
                    transducer  = -1
                    calibration = -1
            if transducer >= 0 and transducer < self.MAX_SENSORS and calibration >= 0 and calibration < self.MAX_CALIBRATIONS:
                calibs[transducer] = calibration
        return calibs
        
    '''
    Gets the powered Transducers from the WNet.
    @return the powered Transducers from the WNet
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def getPoweredTransducers(self):
        response = ''
        lines = ['']
        transducers = [False, False, False, False, False, False]
        transducer = 0
        stateIn = ''
        
        response = self.sendCommandAndWaitForResponse("XPWR");
        lines    = response.split("\r\n") # Split response into individual lines.
        
        for i in range(0, len(lines)):
            line = lines[i]
            fields = line.strip().split() # Split this line into individual tokens.
            if len(fields) >= 2: # If there are at least two tokens in this line,
                try:
                    transducer = int(fields[0]) - 1 # Transducer is origin 1 to the user
                except:
                    transducer = -1
                stateIn = fields[1]
                if transducer >= 0 and transducer < self.MAX_SENSORS and stateIn == "ON":
                    transducers[transducer] = True
        return transducers
        
    def getOperand(self, operand, buf, cmd):
        i = 0
        buf = buf.upper()
        cmd = cmd.upper()
        i   = buf.index(cmd)
        if i >= 0: # If found
            operand = buf[(i + len(cmd)):]
            operand = operand.strip()
        return operand
        
    '''
    Gets the Component Versions from the WNet.
    @return the Component Versions from the WNet
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException
    '''
    def getComponentVersions(self):
        response = ''
        lines = ['']
        versions = ["", "", "", ""]
        
        response = self.sendCommandAndWaitForResponse("VERSIONS")
        lines    = response.split() # Split response into individual lines.
        
        for i in range(0, len(lines)):
            line = lines[i]
            versions[0] = self.getOperand(versions[0], line, 'Firmware')
            versions[1] = self.getOperand(versions[1], line, 'WLAN Module')
            versions[2] = self.getOperand(versions[2], line, 'CPLD 0')
            versions[3] = self.getOperand(versions[3], line, 'CPLD 1')
        return versions
        
    '''
    Sends all of the commands from the given profile so that the WNet is in the same
    state as the profile itself.
    @param profile The WNet profile to read commands from.
    @throws wirelessftsensor.WirelessFTSensor.CommSeveredException 
    '''
    def sendStartupCommands(self, profile):
        self.sendCommandAndWaitForResponse(profile.getSDCommand()) # Send SDREC [ON | OFF]
        
        ''' Send transducer-specific commands. '''
        for transducer in range(0, self.MAX_SENSORS): # For each Transducer,
            if self.m_sensorActive[transducer]: # If this transducer is active,
                xpwr    = profile.getXPWRCommand       (transducer)
                filterr = profile.getFilterCommand     (transducer)
                trans   = profile.getTransducerCommand (transducer)
                calib   = profile.getCalibrationCommand(transducer)
                
                self.sendCommandAndWaitForResponse(xpwr)        # Send XPWR   command
                self.sendCommandAndWaitForResponse(filterr)     # Send FILTER command
                
                if len(calib) > 0:
                    self.sendCommandAndWaitForResponse(trans)   # Send TRANS command,
                    self.sendCommandAndWaitForResponse(calib)   # Send CALIB command.
                    
    '''
    Selects either Gage or Force/Torque data output.
    @param forceTorqueButton True to select F/T data, false to select Gage data.
    @throws CommSeveredException if the
    commands cannot be sent for any reason.
    '''
    def selectGageOrFTData(self, forceTorqueButton):
        '''
        Demo keeps it simple for user by selecting gage or FT data globally, 
        but you actually have to set it for each transducer.
         
        2/24/14: Matrix multiplication is set to on/off for all transducers, regardless of whether or not they
        are sending data.
        '''
        userMode = self.SetTechnicianMode() #  Set technician mode.
        
        for transducer in range(0, self.MAX_SENSORS): # For all Transducers,
            if self.m_sensorActive[transducer]:
                self.sendCommandAndWaitForResponse("TRANS "    + str(transducer + 1)) # Transducer is origin 1 to the user
                if forceTorqueButton:
                    status = 'ON'
                else:
                    status = 'OFF'
                self.sendCommandAndWaitForResponse("CAL MULT " + status)
                
        self.RestoreWnetMode(userMode) # restore Wnet mode
        
    '''
    Sets the active calibration index.
    @param cal The calibration index (0-2).
    @throws CommSeveredException if the
    command cannot be sent for any reason.
    '''
    def setActiveCalibration(self, cal):
        self.sendCommandAndWaitForResponse("CALIB " + str(cal + 1)) # Calibration is origin 1 to the user
        
    '''
    Sets the active sensor index.
    @param transducer The transducer index (0-5).
    @throws CommSeveredException if the
    command cannot be sent for any reason.
    '''
    def setActiveSensor(self, transducer):
        self.sendCommandAndWaitForResponse("TRANS " + str(transducer + 1)) # Transducer is origin 1 to the user
        
    '''
    Reads the active calibration of the active transducer.
    @return The calibration data.
    @throws CommSeveredException if the
    command cannot be sent for any reason.
    '''
    def readActiveCalibration(self):
        self.cal = self.Calibration.Calibration()
        response = self.sendCommandAndWaitForResponse("CAL")
        rtn      = self.cal.parseCalibrationFromTelnetResponse(response)
        return rtn
        
    '''
    Stops writing to any open files and closes UDP and TCP connections for the WNet.
    '''
    def disconnect(self):
        try:
            self.m_sensor.stopStreamingData() #  Tell the Wnet to stop sending UDP packets
        except Exception as e:
            self.logging.warning('WARNING: ' + str(e))
            print e
        
        try:
            self.m_sensor.endCommunication()
        except Exception as e:
            print e
        
    '''
    Sets the bias to "on" for the given sensor.
    @param transducer The sensor to bias (0 to 5).
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''
    def biasSensor(self, transducer):
        self.m_sensor.sendTelnetCommand("BIAS " + str(transducer + 1) + " ON", True) # Transducer is origin 1 to the user
        
    '''
    Sets the bias to "off" for the given sensor.
    @param transducer The sensor to un-bias (0 to 5).
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''
    def unbiasSensor(self, transducer):
        self.m_sensor.sendTelnetCommand("BIAS " + str(transducer + 1) + " OFF", True) # Transducer is origin 1 to the user
        
    '''
    Starts a multiple-file upload thread.
    @param fs The list of file(s) to upload.
    @param m_model
    @throws FileNotFoundException If file(s) not found.
    @throws IOException If file(s) cannot be parsed into byte-arrays.
    '''
    def startFileUpload(self, fs):
        self.m_fileUploadProgress = 0.0
        files = []
        for i in range(0, len(fs)):
            f = fs[i]
            files.append(f)
        write = self.WriteFileTask(self, files)
        write.run()
    
    ''' Verifies that the file upload task is complete. '''    
    def checkFileUploadStatus(self):
        return self.m_flagFileUploadComplete
        
    m_NeedWnetReset = False # Did we need to reset the WNet?
    
    def etNeedWnetReset(self):
        return self.m_NeedWnetReset
    
    '''
    Writing data to a file is pushed to a separate thread
    to keep UI, network communication, and other activities
    running smoothly.
    '''
    class WriteFileTask:
        
        import threading
        
        m_fileName  = []  # The name of the file(s), as stored on the WNet.
        m_data      = []  # Raw byte-data from each read-in file.
        m_totalSize = 0.0 # The total size of the upload job (in bytes).
        
        def __init__(self, outer, files):
            self.outer = outer
            self.files = files
            
        '''
        Gets the size (in bytes) of any file in the upload list.
        @param filename The name of the file.
        @return The total size, in bytes, of the file to be sent to the WNet.
        '''
        def getFileSize(self, filename):
            i = self.m_fileName.index(filename)
            if i != -1:
                return len(self.m_data[i])
            return -1 # File not found.
        
        '''
        Creates new WriteFileThread to upload file to WNet.
        @param fs The list of files write.
        @throws FileNotFoundException If invalid file(s) passed.
        @throws IOException If the given file(s) cannot be parsed into byte-arrays.
        '''
        def WriteFileTask(self, fs):
            import functions
            for f in fs:
                fileToWrite = []
                try:
                    fileToWrite = functions.int2bytes(len(f), 2)
                except Exception as e:
                    print(e)
                self.m_data.append(fileToWrite)
                fname = self.getName(f)
                self.m_fileName.append(fname)
            for b in self.m_data:
                self.m_totalSize += len(b)
                
        '''
        The actual task of writing the files to the WNet's
        Serial Flash memory, performed when the thread starts.
        @throws CommSeveredException if the
        commands cannot be sent for any reason.
        '''
        def call(self):
            chunksize = 106
            bytesUp   = 0.0
            
            self.outer.m_NeedWnetReset = False
            
            for file in range(0, len(self.m_fileName)):             # For each file in the list of files to upload,
                fileName = self.m_fileName[file]                    # get the name of the file.
                fileLen  = len(self.m_data[file])
                
                self.sendCommandAndWaitForResponse("FDEL " + fileName)   # Delete the file, just in case it already exists in the Wnet.
                
                if fileName == "appl.bin":                          # If this file is appl.bin,
                    self.outer.m_NeedWnetReset = True               # set flag to do a reset when we are done uploading files.
                    
                for i in range(0, fileLen, chunksize):              # For each chunk of data in this file,
                    chunkHex = ""
                    if (i + chunksize) > fileLen:
                        chunkLen = fileLen - i
                    else:
                        chunksize
                        
                    for j in range(0, chunksize):                   # For each byte of data in this file chunk,
                        dataByte = 0xff & self.m_data[file][i + j]
                        byteHex  = '{:2x}'.format(dataByte)
                        chunkHex += byteHex
                        
                    self.sendCommandAndWaitForResponse("FHEX " + fileName + " " + chunkHex) # Send a chunk of datas.
                    
                    bytesUp += chunkLen # Update the progress bar.
                    self.m_fileUploadProgress = bytesUp / self.m_totalSize
                                        
                self.sendCommandAndWaitForResponse("FCLOSE")
                
            if self.outer.m_NeedWnetReset: # If appl.bin was one of the files that was uploaded,
                try:
                    self.outer.m_sensor.sendTelnetCommand("RESET", True) #  issue RESET to Wnet.
                except Exception as e:
                    print(e)
            
            return None
            
        def getName(self):
            return self.__class__.__name__
            
        def task(self):
            self.WriteFileTask(self.files)
            self.call()
            self.outer.m_flagFileUploadComplete = True
            
        def run(self):
            self.t = self.threading.Thread(target=self.task)
            self.t.start() # Start thread to finish
        
        def wait(self):
            self.t.join() # Waits for thread to finish.
    
    '''
    Reads WNet's current IP settings.
    @return The current IP settings.
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''        
    def readIPSettings(self):
        response = self.sendCommandAndWaitForResponse("IP")
        return self.IPSettings.IPSettings.IPSettings(response) # See Java code: what is IPSettings()?
    
    '''
    Writes new IP settings to WNet.
    @param settings The settings to write.
    @throws CommSeveredException if the commands cannot be sent for any reason.
    '''
    def writeIPSettings(self, settings):
        self.sendCommandAndWaitForResponse("MYIP "     + settings.IPAddress)
        self.sendCommandAndWaitForResponse("GATEIP "   + settings.DefaultGateway)
        self.sendCommandAndWaitForResponse("NETMASK "  + settings.SubnetMask)
        self.sendCommandAndWaitForResponse("SSID "     + settings.SSID)
        self.sendCommandAndWaitForResponse("NET DHCP " + settings.DHCP)
        
        bandString = '' # Parameter to band command.
        if settings.Band == 'Spectrum2_4Ghz':
            bandString = "2.4"
        elif settings.Band == 'Spectrum5Ghz':
            bandString = "5"
        else:
            print('Unexpected value for band setting.')
        self.sendCommandAndWaitForResponse("BAND " + bandString);            
        self.sendCommandAndWaitForResponse("SAVEALL")
    
    '''
    Sends a firmware command over Telnet (TCP port 23) and waits 
    for a full response (any response text up to the next prompt).
    @param command The command to send.
    @return The response string.
    @throws CommSeveredException if the command cannot be sent for any reason.
    '''
    def sendCommandAndWaitForResponse(self, command):
        response = ''
        print 'Telnet command being sent: ' + str(command)
        self.m_sensor.sendTelnetCommand(command, True) # send command, clearing the input buffer first.
        while not response.endswith('\r\n>'):
            response = response + self.m_sensor.readTelnetData(True) # Blocks if no available data
        print 'Telnet message received:' + str(response)
        return response