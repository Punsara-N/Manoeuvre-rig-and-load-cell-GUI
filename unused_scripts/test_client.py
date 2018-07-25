#import socket
#
## Create a TCP/IP socket
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
## Connect the socket to the port where the server is listening
#server_address = ('localhost', 23)
#print('connecting to %s port %s' % server_address)
#sock.connect(server_address)
#
#try:
#
#    # Send data
#    message = 'This is the message.  It will be repeated.'
#    print('sending "%s"' % message)
#    sock.sendall(message)
#
#    # Look for the response
#    amount_received = 0
#    amount_expected = len(message)
#
#    while amount_received < amount_expected:
#        data = sock.recv(16)
#        amount_received += len(data)
#        print('received "%s"' % data)
#
#finally:
#    print('Closing socket')
#    sock.close()

import socket
import time
import struct

UDP_IP = "localhost"
UDP_PORT = 49152

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


while True:

    #time.sleep(0.100)
    
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    if len(data) >= 18:
        packet_beginning_length = 18
        packet = struct.unpack('>LLLLBB', data[0:packet_beginning_length])
        m_timeStamp    = packet[0]
        m_sequence     = packet[1]
        m_statusCode1  = packet[2]
        m_statusCode2  = packet[3]
        m_batteryLevel = packet[4]
        m_sensorMask   = packet[5]
        
        years70   = long((70 * 365 + 17) * 24 * 60 * 60) # 70 years (in seconds)
        wnetTime  = long(m_timeStamp) # Wnet's number of seconds since 1/1/1900 00:00 NTP (format 20.12)
        sysTime   = long(time.time()*1000) # JAVA: System.currentTimeMillis() # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
        sysTime   = sysTime + years70 * 1000 # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
        sysTime   = (sysTime << 12)   / 1000 # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)        
        sysTime   = sysTime & 0xffffffff        
        m_latency = int((sysTime - wnetTime) & 0xffffffff) # Calculate modulo 32-bits latency (20.12)
        m_latency = (m_latency * 1000) >> 12
        
        print (wnetTime*1000)>>12, (sysTime*1000)>>12, m_latency