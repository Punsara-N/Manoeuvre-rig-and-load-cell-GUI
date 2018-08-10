# THIS IS MY TEST CLIENT

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

soc = socket.socket(family, typee, proto)
#soc.sendto('Hi', addr)
soc.sendto('Done', addr)

data, recvaddr = soc.recvfrom(1024)
print data