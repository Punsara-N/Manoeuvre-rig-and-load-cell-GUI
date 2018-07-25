''' This is essentially the RTA device. '''

'''
multicast_group = '224.0.5.128'
RECEIVE_PORT     = 28250
SEND_PORT        = 51000
'''

import socket
import struct
import sys

multicast_group = '224.0.5.128'
server_address = ('', 51000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

try:
    # Receive/respond loop
    while True:
        print >>sys.stderr, '\nwaiting to receive message'
        data, address = sock.recvfrom(1024)
        
        print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
        print >>sys.stderr, data
    
        print >>sys.stderr, 'sending acknowledgement to', (address[0], 28250)
        sock.sendto('ack', (address[0], 28250))
        
except KeyboardInterrupt as e:
    print('Keyboard interrupt.')
    pass

finally:
    sock.close()