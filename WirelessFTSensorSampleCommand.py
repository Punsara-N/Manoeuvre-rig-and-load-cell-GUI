'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 27-06-2017
-------
'''

class WirelessFTSensorSampleCommand:
    
    import crc
    import struct

    UDP_SERVER_PORT = 49152

    def __init__(self):
        pass
    
    ''' Sends a command to start streaming to the Wireless F/T system. '''
    def sendStartStreamingCommand(self, socket, hostNameOrAddress, numSamples):        
        
        LENGTH      = 10    # Length of this command.
        sequence    = 0     # Sequence number / unused.
        command     = 1     # Command.  1 = start streaming.
        packetDATA = self.struct.pack('>HBBL', LENGTH, sequence, command, numSamples)
        CRC = self.crc.crcBuf(packetDATA, LENGTH-2)
        packetDATA = packetDATA + self.struct.pack('>H', CRC)

        # Sending packet to socket
        UDP_IP = hostNameOrAddress
        UDP_PORT = self.UDP_SERVER_PORT
        try:
            socket.sendto(packetDATA, (UDP_IP, UDP_PORT))
            print 'Sent command to start streaming.'
        except Exception as e:
            print("Failed to send command!")
            print(e)

    ''' Sends a command to stop streaming to the Wireless F/T system. '''
    def sendStopStreamingCommand(self, socket, hostNameOrAddress):

        LENGTH      = 6     # Length of this command.
        sequence    = 0     # Sequence number / unused.
        command     = 2     # Command.  1 = start streaming.
        packetDATA = self.struct.pack('>HBB', LENGTH, sequence, command)
        CRC = self.crc.crcBuf(packetDATA, LENGTH-2)
        packetDATA = packetDATA + self.struct.pack('>H', CRC)

        # Sending packet to socket
        UDP_IP = hostNameOrAddress
        UDP_PORT = self.UDP_SERVER_PORT
        try:
            socket.sendto(packetDATA, (UDP_IP, UDP_PORT))
            print 'Sent command to stop streaming.'
        except Exception as e:
            print("Failed to send command!")
            print(e)

    ''' Sends a command to reset the telnet socket in the Wireless F/T system. '''
    def sendResetTelnetCommand(self, m_udpSocket, hostNameOrAddress): 
        
        LENGTH      = 6     # Length of this command.
        sequence    = 0     # Sequence number / unused.
        command     = 5     # Command.  1 = start streaming.
        packetDATA = self.struct.pack('>HBB', LENGTH, sequence, command)
        CRC = self.crc.crcBuf(packetDATA, LENGTH-2)
        packetDATA = packetDATA + self.struct.pack('>H', CRC)

        # Sending packet to socket
        UDP_IP = hostNameOrAddress
        UDP_PORT = self.UDP_SERVER_PORT
        try:
            m_udpSocket.sendto(packetDATA, (UDP_IP, UDP_PORT))
            print 'Sent command to reset telnet.'
        except Exception as e:
            print("Failed to send command!")
            print(e)