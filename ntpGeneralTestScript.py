# THE IS MY TEST SERVER

import socket

#ctypes.windll.shell32.IsUserAnAdmin()

host = 'localhost'
port = 'ntp' # To check if port is in use, try cmd: netstat -ano|findstr 123

print socket.getaddrinfo(host, port)
addrInfo = socket.getaddrinfo(host, port)[1] # (23, 2, 0, '', ('::1', 123, 0, 0))
family = addrInfo[0]
typee = addrInfo[1]
proto = addrInfo[2]
print family, typee, proto
addr = addrInfo[4]
print addr

#soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc = socket.socket(family, typee, proto)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # This allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state for several minutes, waiting for late packets to arrive.
soc.bind(addr)  
#soc.listen(1)
#conn, addr = soc.accept()
#print 'Connection accepted:'
#print conn, addr
while True:
    data, recvaddr = soc.recvfrom(1024)
    print 'Data reveived:'
    #print data
    soc.sendto('hi', recvaddr)
    break

print 'Closing socket'
soc.close()