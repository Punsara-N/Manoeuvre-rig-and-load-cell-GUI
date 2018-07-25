'''
Test RTA Device
'''

import socket
import struct
import binascii

multicast_group = '224.0.5.128'
server_address = ('', 51000)

'''
# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.settimeout(0.257*7)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
'''



MCAST_GRP = '224.0.5.128'
MCAST_PORT = 51000# or 28250 ?
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                             # to MCAST_GRP, not all groups on MCAST_PORT
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


MCAST_PORT_recv = 28250
'''
sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sockSend.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
'''
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)


string = 'RTAD'
abResponse = bytearray(36)
for i in range(0, len(string)):
    abResponse[i] = string[i]
i += 1
abResponse[i]   = 1
abResponse[i+1] = 6
abResponse[i+2] = 0x00
abResponse[i+3] = 0x23
abResponse[i+4] = 0xa7
abResponse[i+5] = 0x0c
abResponse[i+6] = 0x3d
abResponse[i+7] = 0x7e
i += 6+2
abResponse[i]   = 2
abResponse[i+1] = 4
abResponse[i+2] = 192
abResponse[i+3] = 168
abResponse[i+4] = 0
abResponse[i+5] = 11
i += 4+2
abResponse[i]   = 3
abResponse[i+1] = 4
abResponse[i+2] = 255
abResponse[i+3] = 255
abResponse[i+4] = 255
abResponse[i+5] = 0
i += 4+2
abResponse[i]   = 0x0d
abResponse[i+1] = 4
abResponse[i+2] = 'T'
abResponse[i+3] = 'E'
abResponse[i+4] = 'S'
abResponse[i+5] = 'T'
i += 4+2
abResponse[i]   = 0x86 #(0x86 - 256)
abResponse[i+1] = 4
abResponse[i+2] = 'T'
abResponse[i+3] = 'E'
abResponse[i+4] = 'S'
abResponse[i+5] = 'T'

try:
    # Receive/respond loop
    while True:
        try:
            print '\nwaiting to receive message'
            data, address = sock.recvfrom(1024)
            
            print 'received %s bytes from %s' % (len(data), address)
            print 'Received data: %s' % binascii.hexlify(data) #data[0:10]
        
            '''
            send_addr = (address[0], 28250) #(address[0], 28250) #51000 #28250
            print 'sending acknowledgement to', send_addr
            print 'Sending data: %s' % binascii.hexlify(abResponse)
            #sock.sendto('ack', (address[0], 28250))
            sock.sendto(abResponse, send_addr)
            '''
            
            print 'sending acknowledgement to', (MCAST_GRP, MCAST_PORT_recv)
            print 'Sending data: %s' % binascii.hexlify(abResponse)
            sock.sendto(abResponse, (MCAST_GRP, MCAST_PORT_recv))
            
        except Exception as e:
            print e
            pass
        
except KeyboardInterrupt as e:
    print('Keyboard interrupt.')
    pass

finally:
    sock.close()