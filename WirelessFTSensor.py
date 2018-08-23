'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 26-06-2017
-------
'''

'''
Communicates with the WNET over Telnet.
@author Sam Skuce, Chris Collins (ATI)
'''
class WirelessFTSensor:
    
    import time
    import socket
    import telnetlib
    
    def __init__(self):
        
        import logging
        import WirelessFTSensorSampleCommand
        import WirelessFTSample
        
        self.TCP_TIMEOUT            = 5000/1000 # Telnet timeout is fairly short. If the user can't send commands pretty much instantly, there's probably a network problem.
        self.TELNET_PORT            = 23 # Reserved port number for TCP connection via Telnet.
        self.UDP_TIMEOUT            = 5000/1000 # Default timeout allows up to 5 seconds between each record read.
        self.ASCII_CHARSET          = 'US-ASCII' # ASCII characters are always used for WNet commands.
        self.DEFAULT_BUFFER_SIZE    = 1024 # Default size of network buffers.
        self.m_udpSocket            = None # The socket that sends and receives each data sample.
        self.m_telnetSocket         = None # The Telnet socket that sends and receives firmware commands.
        log                         = logging.basicConfig(filename='wirelessft.log')  # Logs handled exceptions and (optionally) reports them to the UI.
        self.m_logger               = logging.getLogger(log)    
        self.m_sensorAddress        = '' # The host name or IP address of the WNet.
        self.WirelessFTSensorSampleCommand = WirelessFTSensorSampleCommand.WirelessFTSensorSampleCommand()
        self.WirelessFTSample       = WirelessFTSample.WirelessFTSample()

    '''
    Stops using the TCP and UDP sockets. TCP sockets are
    set back to 0.0.0.0 addresses when this happens, but
    the WNet will keep the last-used UDP destination
    to which records were sent.
    '''
    def endCommunication(self):

        if self.m_udpSocket != None:
            self.m_udpSocket.close()
            
        try:
            self.time.sleep(0.25)
        except Exception as e: 
            pass # Do nothing.
        
        if self.m_telnetSocket != None: 
            try:
                self.m_telnetSocket.close()
            except:
                self.m_logger.info('Exception closing Wireless F/T Telnet socket: '+e) # Do nothing.
    
    ''' Constructor that initializes WNet address and network connections. '''
    def WirelessFTSensor(self, hostNameOrIPAddress):
        self.setSensorAddress(hostNameOrIPAddress)
        
    ''' Closes existing sockets and opens new ones to connect to the specified Wireless F/T sensor. '''
    def initSockets(self, hostNameOrIPAddress):

        self.endCommunication() # Close existing sockets.
        sensorAddress = hostNameOrIPAddress # Set the WNet's address.

        '''        
        The telnet socket should automatically bind to the correct local 
        address, even if we have more than NIC installed locally. Use this 
        same local address to bind the UDP socket.
        '''
        # addr = "0.0.0.0" # EXAMPLE: "localhost"
        # port = 0 # EXAMPLE: 10000
        # server_address = (addr, port)
        try:
            self.m_udpSocket = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_DGRAM)
            self.m_udpSocket.settimeout(self.UDP_TIMEOUT)
            #self.m_udpSocket.setblocking(0)
            #self.m_udpSocket.bind((hostNameOrIPAddress, self.WirelessFTSensorSampleCommand.UDP_SERVER_PORT))
            self.m_udpSocket.setsockopt(self.socket.SOL_SOCKET, self.socket.SO_REUSEADDR, 1) # This allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state for several minutes, waiting for late packets to arrive.
            self.m_udpSocket.bind(('0.0.0.0', self.WirelessFTSensorSampleCommand.UDP_SERVER_PORT))
        except Exception as e:
            print('Failed to create UDP socket.')
            print(e)
        
        self.resetTelnetSocket() # Make very sure that the telnet socket is available for use.
        
        # Open new ports to this address.
        try:
            self.m_telnetSocket = self.telnetlib.Telnet(sensorAddress, self.TELNET_PORT, self.TCP_TIMEOUT)
        except Exception as e:
            print('Failed to create telnet port.')
            print(e)
        
        try:
            self.time.sleep(0.1)
        except:
            pass # Do nothing.
    
    ''' Gets the IP address or hostname of the currently-connected WNet. '''
    def getSensorAddress(self):
        return self.m_sensorAddress
    
    ''' Attempts to connect to a given IP address or hostname and sets the current address to it if it was successful. '''
    def setSensorAddress(self, val):
        self.m_sensorAddress = val
        self.initSockets(self.m_sensorAddress)
    
    ''' Sends the command to start streaming UDP samples. '''
    def startStreamingData(self): # Sends the command to start streaming UDP samples.
        self.WirelessFTSensorSampleCommand.sendStartStreamingCommand(self.m_udpSocket, self.m_sensorAddress, 0)
    
    ''' Sends the command to stop streaming UDP samples. '''
    def stopStreamingData(self): # Sends the command to stop streaming UDP samples.
        self.WirelessFTSensorSampleCommand.sendStopStreamingCommand(self.m_udpSocket, self.m_sensorAddress)
    
    ''' Sends the command to reset the Telnet socket in the WNet. '''
    def resetTelnetSocket(self):
        for i in range(0,3):
            try:
                self.WirelessFTSensorSampleCommand.sendResetTelnetCommand(self.m_udpSocket, self.m_sensorAddress)              
                try:
                    self.time.sleep(0.2) # Give the WNet time to close and reopen the socket.
                except: # If we are interrupted during this delay,
                    pass # Do nothing.
                print 'Telnet socket reset. %s %s' % (self.m_udpSocket, self.m_sensorAddress)
            except Exception as e:
                print("Failed to reset telnet socket!")
                print(e)
                
        return
    
    ''' Reads a single F/T sample from the UDP socket. '''
    def readStreamingSample(self):
        while True:
            data = self.m_udpSocket.recv(self.DEFAULT_BUFFER_SIZE)
            if len(data) >= 18:
                break  
        return self.WirelessFTSample.WirelessFTSample(data, len(data))
    
    ''' Reads multiple samples from the UDP socket. '''
    def readStreamingSamples(self):
        import binascii
        
#        i = 0
#        dataPackets = []
        while True:
            dataPacket = self.m_udpSocket.recv(self.DEFAULT_BUFFER_SIZE) # Get UDP packet from Wnet, server is the address of the socket sending the data.                 
            #data_hexString = binascii.hexlify(dataPacket)
            #print 'Received data: %s' % data_hexString
#            if len(dataPacket):
#                i += 1 # Packet received.
#                #dataPackets = dataPackets + data
#                dataPackets.append(dataPacket)
#            if i>10:
#                break # Break loop after i number of packets have received.
            return self.WirelessFTSample.listOfSamplesFromPacket(dataPacket, len(dataPacket)) # Split UDP packet into indivual samples
        
    ''' Sends a firmware command over the WNet's Telnet socket. '''
    def sendTelnetCommand(self, command, clearInputBufferFirst):
        
        if not command.endswith('\r\n'):
            command = command + '\r\n'
            
        if 'RESET' in command: # If this is a RESET command,
            command = 'RESET\r' # send the bare minimum command.
            
        try:
            if clearInputBufferFirst:
                pass
                
            self.testTelnetConnection()
            self.m_telnetSocket.write(command)    
            
            if 'RESET' in command: # If this is a RESET command,
                self.endCommunication()
                self.m_logger.info('Communications ended')
            
        except Exception as e1:
            print e1
            if 'RESET' in command:
                self.endCommunication()
                self.m_logger.info('Communications ended catch: ' + e1)
            else:
                try:
                    self.m_logger.warning('Connection lost, attempting to re-establish Telnet Write ... ')
                    self.testTelnetConnection()
                    self.m_logger.info('Connection re-established.')
                    self.m_telnetSocket.write(command)
                except Exception as e2:
                    print e2
                    try:
                        self.m_telnetSocket.close() # Reopen the socket with the same address.
                        self.m_telnetSocket = self.telnetlib.Telnet(self.m_sensorAddress, self.TELNET_PORT, self.TCP_TIMEOUT)
                        self.m_logger.info('Connection re-established.')
                        self.m_telnetSocket.write(command)
                    except Exception as e3:
                        print e3
                        self.m_logger.critical('Could not re-establish connection: ' + e3)
                        self.m_logger.critical('Lost Telnet connection.')
                        print('Lost Telnet connection.')
    
    ''' Reads data from telnet link. '''    
    def readTelnetData(self, blockIfNoAvailableData):
        telnetData = ''
        try:
            telnetData = self.parseTelnetResponse(blockIfNoAvailableData)
        except Exception as e1: # Command failed, try to "ping" port 23 with "\r\n".
            print e1
            try:
                self.m_logger.warning('Connection lost, attempting to re-establish Telnet Read... ')
                self.testTelnetConnection()
                self.m_logger.info('Connection re-established.')
                self.parseTelnetResponse(blockIfNoAvailableData)
            except Exception as e2: # Could not "ping" Telnet.
                print e2
                try: # Reopen the socket with the same address.
                    self.m_telnetSocket.close()
                    self.m_telnetSocket = self.telnetlib.Telnet(self.m_sensorAddress, self.TELNET_PORT, self.TCP_TIMEOUT)
                    self.m_logger.info('Connection re-established.')
                    telnetData = self.parseTelnetResponse(blockIfNoAvailableData)
                except Exception as e3:
                    print e3
                    self.m_logger.critical('Could not re-establish connection: ' + str(e3))
                    self.m_logger.critical('Lost Telnet connection.')
    
        return telnetData
    
    ''' Tests to see if the Telnet connection is still active by sending a "\r\n" and (ideally) generating a new prompt. '''
    def testTelnetConnection(self): # Tests to see if the Telnet connection is still active by sending a "\r\n" and (ideally) generating a new prompt.
        self.m_telnetSocket.write('\r\n')
        self.time.sleep(0.01) # Give the port time (10 mS) to populate a response.
        self.m_telnetSocket.read_until('\r\n', 0.2) # Try to read something.
    
    ''' Attempts to buffer and parse a Telnet response into a String. '''
    def parseTelnetResponse(self, blockIfNoAvailableData): # Attempts to buffer and parse a Telnet response into a String.
        inputStream = self.m_telnetSocket.read_until('\r\n', 0.2)
        if blockIfNoAvailableData:
            return inputStream
        
        return ''