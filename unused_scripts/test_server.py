"""
Simulated telnet server
"""

## Simulates the telnet server on the Wireless F/T to aid in testing.
#import socket
#import time
#
#m_telnetSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('0.0.0.0', 23)
#m_telnetSocket.bind(server_address)
#m_telnetSocket.listen(1)
#
#connection, client_address = m_telnetSocket.accept()
#
#time.sleep(10)
#
#connection.close()

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
server_address = ('localhost', 23) # Bind the socket to the port
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = sock.accept()

    try:
        print('connection from ' + str(client_address))

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('Received "%s"' % data)
            if data:
                print('Sending data back to the client...')
                connection.sendall(data)
            else:
                print('No more data incoming from ' + str(client_address))
                break

    finally:
        # Clean up the connection
        connection.close()