'''
Test broadcast client
'''

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)

address = ('', 12345)

sock.bind(address)

try:
    
    while True:
        print('...')
        data, addr = sock.recvfrom(1024)
        print data
        if data>0:
            break
        
except KeyboardInterrupt as e:
    
    print('Keyboard inturrupted!')
    pass

except Exception as e:
    
    print e
    pass

sock.close()