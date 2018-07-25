"""
UDP test server for broadcasting
"""

import socket
import WirelessFTDemoModel
import time
import struct

UDP_IP   = 'localhost'
UDP_PORT = 49152
MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

time.sleep(1)

ii = 0
while True:
    
    ''' New way of packing bytes: '''
    timeStamp       = 0x12345678
    sequence        = 0xaabbccdd
    firstStatus     = 0x552233aa
    secondStatus    = 0x83927561
    batteryLevel    = 0x80
    transMask       = 0x07
    
    # Fancy timestamp to actually measure latency
    years70 = long((70 * 365 + 17) * 24 * 60 * 60) # 70 years (in seconds)
    timeStamp2   = long(time.time()*1000) # JAVA: System.currentTimeMillis() # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
    timeStamp2   = timeStamp2 + years70 * 1000 # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
    timeStamp2   = (timeStamp2 << 12)   / 1000 # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)
    timeStamp2   = timeStamp2 & 0xffffffff
    
    packetDATA = struct.pack('>LLLLBB', timeStamp2, sequence, firstStatus, secondStatus, batteryLevel, transMask)
    #print packetDATA
    #packet = struct.unpack('LLLLBB', packetDATA)
    #print packet
    #print struct.calcsize('LLLLBB')
    
    sample_data = []
    for i in range(0, 3):
        A = []
        for j in range(0, 6):
            A.append(0)
        sample_data.append(A)
    
    WirelessFTDemoModel_instance = WirelessFTDemoModel.WirelessFTDemoModel()
    for transducer in range(0, 3):
        for axis in range(0, WirelessFTDemoModel_instance.NUM_AXES):
            sample_data[transducer][axis] = (transducer + 1) * (axis + 2)
            packetDATA = packetDATA + struct.pack('>l', sample_data[transducer][axis])
    
    #print packetDATA      
    packet = struct.unpack('>LLLLBBllllllllllllllllll', packetDATA)
    #print packet

    sock.sendto(packetDATA, (UDP_IP, UDP_PORT))
    print('%i Message sent! %i' %(ii+1, (timeStamp2*1000)>>12))
    time.sleep(1.000)
    ii += 1
    
#import socket
#
#UDP_IP = "127.0.0.1"
#UDP_PORT = 5005
#MESSAGE = "Hello, World!"
#
#print "UDP target IP:", UDP_IP
#print "UDP target port:", UDP_PORT
#print "message:", MESSAGE
#
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))