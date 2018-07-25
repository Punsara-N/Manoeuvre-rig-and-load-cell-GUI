'''
Test broadcast server
'''

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
address = ('<broadcast>', 12345) # '<broadcast>' '255.255.255.255'


try:
    
    i = 1
    while True:
        print('%i Sending...' % i)
        data = 'Hello %i' % i
        sock.sendto(data, address)
        time.sleep(1)
        i += 1
        
except KeyboardInterrupt as e:
    
    print('Keyboard inturrupted!')
    pass

except Exception as e:
    
    print e
    pass

sock.close()