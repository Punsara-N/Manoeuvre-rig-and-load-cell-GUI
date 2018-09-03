'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 22-06-2017
-------------------------------------------------------------------------------------------------
'''

class WirelessFTSample:
    
    import WirelessFTDemoModel
    
    def __init__(self):
        
        self.PACKET_OVERHEAD    = 4 + 4 + 4 + 4 + 1 + 1 # The overhead in a 32-bit sample packet. 4+4+4+4+1+1 = Timestamp, sequence, status code 1, status code 2, battery level, and mask.
        self.SENSOR_RECORD_SIZE = self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES * 4  # The size of a 32-bit sensor record within a packet.
        self.m_sensorActive     = [False, False, False, False, False, False] # Keeps track of which sensors are active.
        
        # Creating an array of size MAX_SENSORS x NUM_AXES
        self.m_ftOrGageData     = []
        for i in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS):
            A = []
            for j in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES):
                A.append([])
            self.m_ftOrGageData.append(A)
        
        self.m_timeStamp        = 0
        self.m_sequence         = 0
        self.m_statusCode1      = 0
        self.m_statusCode2      = 0
        self.m_batteryLevel     = 0x00
        self.m_sensorMask       = 0x00
        
        self.m_timeStampms      = 0
        
        self.m_numSensors = 1 # Assuming 1 active transducer to begin with
        
    
    def toString(self): # Returns the string representation of the sample
        string = "Timestamp: " + str(self.m_timeStamp) \
                + "\nSequence number: " + str(self.m_sequence) \
                + "\nStatus Code 1: " + str(self.m_statusCode1) \
                + "\nStatus Code 2: "   + str(self.m_statusCode2) \
                + "\nBattery Level: "   + str(self.m_batteryLevel) \
                + "\nSensor Mask: "     + str(self.m_sensorMask)
        return string
    
    def listOfSamplesFromPacket(self, udpPacketData, udpPacketLength, receiveTime, T0_loadcell):
    
        import numpy as np
    
        self.receiveTime = receiveTime
        self.T0_loadcell = T0_loadcell
        samples = np.array([]) # Making new array (timestamp, sequence, statusCode1, statusCode2, batteryLevel, sensorMask, latency)
        sampleLength = self.getNumSensors() * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD # Get length of the sample block  
        for i in range(0, udpPacketLength, sampleLength):
            singleRecord = udpPacketData[i:i+udpPacketLength] # Pick out next sample block
            self.WirelessFTSample(singleRecord, udpPacketLength, self.receiveTime, self.T0_loadcell) # Decode the sample block
            sampleLength = self.getNumSensors() * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD # Get length of the sample block            
            #sample = np.array([self.m_timeStamp, self.m_sequence, self.m_statusCode1, self.m_statusCode2, self.m_batteryLevel, self.m_sensorMask, self.m_latency])
            sample = self
            if len(samples) > 0:
                samples = np.vstack((samples,sample)) # Add sample block data to ArrayList
            else:
                samples = [sample]
           
        return samples
    
    '''
    Constructs new Wireless F/T sample from received network data.
    @param packetData The data received from the network.
    @param length     The length of data in packetData.
    @throws IllegalArgumentException If length is incorrect or data is invalid.
    Samples come in at the packet RATE.
    '''
    def WirelessFTSample(self, packetData, length, receiveTime, T0_loadcell):
    
        import struct
        import time
        
        packet_beginning_length = 18
        packet = struct.unpack('>LLLLBB', packetData[0:packet_beginning_length])
        self.m_timeStamp    = packet[0]
        self.m_sequence     = packet[1]
        self.m_statusCode1  = packet[2]
        self.m_statusCode2  = packet[3]
        self.m_batteryLevel = packet[4]
        self.m_sensorMask   = packet[5]
    
        if self.m_sensorMask != 0x00: # If a Transducer mask is given in the packet,
            for transducer in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS): # for each Transducer,
                if ((self.m_sensorMask & (1 << transducer)) != 0): # that is active,
                    self.m_sensorActive[transducer] = True # save an active flag.
        else: # If a sensor mask is NOT given in the data (due to very old Wnet firmware)
            # use packet length to determine active transducers.
            if (length % (0 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [False, False, False, False, False, False]
            elif (length % (1 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, False, False, False, False, False]
            elif (length % (2 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, True, False, False, False, False]
            elif (length % (3 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, True, True, False, False, False]
            elif (length % (4 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, True, True, True, False, False]
            elif (length % (5 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, True, True, True, True, False]
            elif (length % (6 * self.SENSOR_RECORD_SIZE + self.PACKET_OVERHEAD) == 0):
                self.m_sensorActive = [True, True, True, True, True, True]
            else: # This can and does happen when UDP packets contain multiple data packets AND you turn transducers on and off.
                self.m_sensorActive = [False, False, False, False, False, False]
                print("Invalid packet length.")
               
        self.m_numSensors = 0 # Count the active transducers.
        for transducer in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS): # for each Transducer,
            if (self.m_sensorActive[transducer]): # that is active,
                self.m_numSensors += 1 # count the active Transducer.
                packet = struct.unpack('>llllll', packetData[(packet_beginning_length+24*(self.m_numSensors-1)):(packet_beginning_length+24*self.m_numSensors)])
                for channel in range (0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES): # For each channel,
                    self.m_ftOrGageData[transducer][channel] = packet[channel] # get the data. (I am taking the first four bytes and converting it into an integer)
    
        
        '''
        # wnetTime, sysTime, and years70 are all type long in Java source code
        years70 = (((70 * 365) + 17) * 24 * 60 * 60) & 0xFFFFFFFF # 70 years (in seconds)
        wnetTime = self.m_timeStamp & 0xFFFFFFFF # Wnet's number of seconds since 1/1/1900 00:00 NTP (format 20.12) (unsigned long)
        sysTime   = self.receiveTime & 0xFFFFFFFF# int(time.time()*1000) & 0xFFFFFFFF # JAVA: System.currentTimeMillis() # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
        sysTime   = (sysTime + (years70 * 1000)) & 0xFFFFFFFF # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
        sysTime   = (((sysTime << 12) & 0xFFFFFFFF) / 1000)  & 0xFFFFFFFF # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)
        self.m_latency = (sysTime - wnetTime) & 0xFFFFFFFF # Calculate modulo 32-bits latency (20.12)
        if self.m_latency > 0x7FFFFFFF:
            self.m_latency -= 0xFFFFFFFF
        self.m_latency = (self.m_latency * 1000) & 0xFFFFFFFF
        if self.m_latency > 0x7FFFFFFF:
            self.m_latency -= 0xFFFFFFFF
        self.m_latency = (self.m_latency >> 12) & 0xFFFFFFFF # Convert to mS (32.0)
        if self.m_latency > 0x7FFFFFFF:
            self.m_latency -= 0xFFFFFFFF
        '''
        
        '''    
        self.m_timeStampms = self.m_timeStamp & 0xFFFFFFFF
        self.m_timeStampms = (self.m_timeStamp * 1000) & 0xFFFFFFFF
        self.m_timeStampms = (self.m_timeStamp >> 12) & 0xFFFFFFFF
        print (sysTime * 1000) & 0xFFFFFFFF - self.m_timeStampms
        '''
        
        
        # Convert timestamp to unsigned 32bit
        m_timeStamp = self.m_timeStamp#2078044892
        wnetTime  = float(m_timeStamp)
        if wnetTime >= 0:
            pass
        else:
            wnetTime += 2**32
        
        # Find when last rollover started, the loadcell clock rests ever 2^20 seconds, clock started at midnight January 1, 1900 (70 years before Epoch (midnight January 1, 1970))
        years70 = ((70 * 365) + 17) * 24 * 60 * 60 # 70 years (in seconds)
        secondsSinceStartOfTodayToNow = (receiveTime/1000) % (24*60*60)
        #print 'secondsSinceStartOfTodayToNow: ' + time.strftime('%H:%M:%S', time.localtime(secondsSinceStartOfTodayToNow)) 
        secondsSinceStartOfWNetClockToStartOfDay = (receiveTime/1000) - secondsSinceStartOfTodayToNow + years70
        A = secondsSinceStartOfWNetClockToStartOfDay % 2**20 # seconds from start of last rollover before midnight to midnight
        B = wnetTime/(2**12) # Received timestamp, in seconds
        
        # Check if clock rolled over after midnight that day (before the packet was received), and correct date/time of start of last rollover accordingly
        # Note startOfRollOver is relative to epoch, in seconds
        if A > B:
            startOfRollover = secondsSinceStartOfWNetClockToStartOfDay - years70 - A #+ 2**20 # Rollover happened after midnight before packet was received
        else:
            startOfRollover = secondsSinceStartOfWNetClockToStartOfDay - years70 - A
        
        # So packet date/time = timestamp on packet + date/time of start of last rollover
        packetTime = startOfRollover + wnetTime/(2**12) # packet time since Epoch, in seconds
        #print 'Wnet time: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(packetTime))
        
        self.delay = self.receiveTime - packetTime*1000 # in milliseconds
        #print 'Delay: ' + str(self.delay) + ' ms'
        self.m_latency = self.delay
        #print self.m_latency
        
        self.loadcellTimeStamp = (packetTime*1000 - T0_loadcell/1000)/1000 # in seconds
        
        
    def parse_bin(self, s):
        t = s.split('.')
        return int(t[0], 2) + int(t[1], 2) / 2.**len(t[1])
    
    # The time stamp.
    def getTimeStamp(self):
        return self.loadcellTimeStamp#self.m_timeStamp
    
    # The latency value in mS.
    def getLatency(self):
        return self.m_latency
    
    # The sequence number.
    def getSequence(self):
        return self.m_sequence
    
    # The status code (transducers 1-3).
    def getStatusCode1(self):
        return self.m_statusCode1
        
    # The status code (transducers 4-6).
    def getStatusCode2(self):
        return self.m_statusCode2
    
    # The battery level.
    def getBatteryLevel(self):
        return self.m_batteryLevel
        
    # The mask corresponding to the currently active sensors.
    def getSensorMask(self):
        return self.m_sensorMask
    
    # The F/T or gage data from the sample.
    def getFtOrGageData(self):
        return self.m_ftOrGageData
        
    # Tells how many sensors are active for the entire WFT.
    def getNumSensors(self):
        return self.m_numSensors
        
    #Tells which sensors are currently in-use.
    def getActiveSensors(self):
        return self.m_sensorActive