'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 04-07-2017
-------------------------------------------------------------------------------------------------
'''

class DiscoveryClient:
    
    import socket
    import struct
    import binascii
    
    def __init__(self):
        self.RECEIVE_PORT     = 28250 # The port to which discovery protocol responses are sent.
        self.SEND_PORT        = 51000 # The port to which discovery protocol requests are sent.
        self.MULTICAST_IP     = '224.0.5.128' # The Multicast IP address we use to listen for responses.
        self.DELAY_MULTIPLIER = 7 # Delay multiplier sent with discovery request of 10 ms. Delay multipliers are used to spread out the responses from the devices and avoid collisions.
        self.DISCOVERY_REQUEST_HEADER  = 'RTA Device DiscoveryRTAD' # Beginning of every discovery request message. Text lets the device know that this is a discovery request.
        self.DISCOVERY_RESPONSE_HEADER = 'RTAD' # Beginning of every RTA response message.
        self.IP_FIELD_LENGTH  = 4 # At this time, all IP fields are of length 4.
        
        # The following definitions were taken from the RTA Discovery Protocol Guide.
        self.RTA_DISC_TAG_MAC  = 1 # MAC,  same as Digi
        self.RTA_DISC_TAG_IP   = 2 # IP,   same as Digi
        self.RTA_DISC_TAG_MASK = 3 # Mask, same as Digi
        self.RTA_DISC_TAG_GW   = 0x0b # Gateway, same as Digi
        self.RTA_DISC_TAG_HW   = 0x81 # Hardware platform
        self.RTA_DISC_TAG_APP  = 0x0d # Application, same as Digi
        self.RTA_DISC_TAG_VER  = 8 # Version, same as Digi
        self.RTA_DISC_TAG_SEQ  = 0x82 # Sequence number
        self.RTA_DISC_TAG_CRCS = 0x96 # CRC of selected parts of message
        self.RTA_DISC_TAG_CRC  = 0xf0 # CRC of entire message
        self.RTA_DISC_TAG_TICK = 0x83 # Clock tick when response message sent
        self.RTA_DISC_TAG_RND2 = 0x93 # Random number (for encryption)
        self.RTA_DISC_TAG_RND1 = 0x84 # Random number (for encryption)
        self.RTA_DISC_TAG_RND  = 0x94 # Random number (for encryption)
        self.RTA_DISC_TAG_PSWD = 0x85 # Encrypted password
        self.RTA_DISC_TAG_LOC  = (0x86 - 256) # Location of the unit // Compensate for the lack of an unsigned char type.
        self.RTA_DISC_TAG_DISC = 0x95 # Discovery SW revision
        self.RTA_DISC_TAG_MULT = 0xf2 # Response-delay multiplier for broadcast
     
    ''' Summary:
    Broadcasts a discovery request to your local network and listens for responses
    from RTA devices.  Even devices which aren't configured properly can be found
    with this method, because it requests the devices to respond to a multicast
    address, which allows the devices to ignore their default gateway, netmask,
    etc., and "just send" the response.
    Return: The list of discovered devices.
    Param name="ipaLocal": The local interface to search from.  Setting this parameter
    to null causes the function to search from any available interface.
    '''
    def discoverRTADevicesLocalBroadcast(self, *args):
        if len(args) == 0:
            return self.discoverRTADevicesLocalBroadcast_function(None)
        if len(args) == 1:
            return self.discoverRTADevicesLocalBroadcast_function(*args)
           
    def discoverRTADevicesLocalBroadcast_function(self, ipaLocal):

        multicastAddress    = self.MULTICAST_IP # Set up the multicast address.
        discoveryMessage    = self.createMulticastDiscoveryRequest() # Create the discovery request message.
        sendPacket          = discoveryMessage # + bytes(0) + bytes(len(discoveryMessage)) + bytes('255.255.255.255') + bytes(self.SEND_PORT)
        rtaList             = [] # List of RTA Devices to be built.
        
        try: 
            
            multicastSocket_recv = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_DGRAM, self.socket.IPPROTO_UDP)
            multicastSocket_recv.settimeout(0.257*self.DELAY_MULTIPLIER)#(0.2)
            multicastSocket_recv.setsockopt(self.socket.SOL_SOCKET, self.socket.SO_REUSEADDR, 1)
            # Tell the kernel that we are a multicast socket.
            multicastSocket_recv.setsockopt(self.socket.IPPROTO_IP, self.socket.IP_MULTICAST_TTL, 255) 
            multicastSocket_recv.setsockopt(self.socket.SOL_SOCKET, self.socket.SO_BROADCAST, 1)
            # Tell the operating system to add the socket to the multicast group on all interfaces.
            group = self.socket.inet_aton(multicastAddress)
            mreq = self.struct.pack('4sL', group, self.socket.INADDR_ANY)
            multicastSocket_recv.setsockopt(self.socket.IPPROTO_IP, self.socket.IP_ADD_MEMBERSHIP, mreq)            
            # Bind to the port that we know will receive multicast data.
            multicastSocket_recv.bind(('', self.RECEIVE_PORT))
            multicast_address_send = ('255.255.255.255' , self.SEND_PORT)
            multicastSocket_recv.sendto(sendPacket, multicast_address_send)
            
            timeout_counter = 1
            
            while True:
                try:
                    print('\nWaiting to detect load cell...')
                    receiveMessage, address = multicastSocket_recv.recvfrom(205)
                    #print self.binascii.hexlify(receiveMessage), address
                    if receiveMessage>0:
                        print('Load cell found!')
                        tempRTA = self.parseDiscoveryResponse(receiveMessage) # Parse received discovery response packet.
                        if tempRTA != None: # If we got a discovery response packet,
                            ip1 = int(tempRTA.m_ipa.split('.')[3]) # Get last byte of IP address that we just read.
                            if (ip1 < 0):
                                ip1 += 256 # Compensate for the lack of an unsigned char type.
                            multicastSocket_recv.settimeout((257 - ip1)*self.DELAY_MULTIPLIER/1000) # Set new socket timeout based on IP address.
                        rtaList.append(tempRTA) # Add new device to list of devices.
                except self.socket.timeout as e:
                    print 'Timed out. (%i / 5)' % timeout_counter
                    timeout_counter += 1
                    if timeout_counter > 5:
                        print 'No device found.'
                        break
                    pass
                except Exception as e:
                    print e
                    pass
                
            
                
        except KeyboardInterrupt as e:
            pass
        
        except Exception as e:
            print e
            pass
        
        try:
            multicastSocket_recv.close()
        except Exception as e:
            print e
            pass
        
        '''
        tempRTA = self.parseDiscoveryResponse(receiveMessage) # Parse received discovery response packet.
        print tempRTA.m_ipa
        print tempRTA.m_macstring
        print tempRTA.m_ipaNetmask
        print tempRTA.m_strApplication
        print tempRTA.m_strLocation
        '''

        return rtaList
            
    '''
    Creates a discovery request message with a multicast reply-to address.
    Returns: The discovery request message.   
    '''    
    def createMulticastDiscoveryRequest(self):
        discoveryRequest = bytearray(len(self.DISCOVERY_REQUEST_HEADER)+9) # Array to be returned.
        
        # Place DISCOVERY_REQUEST_HEADER in bytes into discoveryRequest.
        for i in range(0, len(self.DISCOVERY_REQUEST_HEADER)):
            discoveryRequest[i] = self.DISCOVERY_REQUEST_HEADER[i]
        
        i += 1
        discoveryRequest[i] = self.RTA_DISC_TAG_IP
        i += 1
        discoveryRequest[i] = 4 # Length of an IP address.
        
        # Add in the IP address.
        ipValues = self.MULTICAST_IP.split('.') # Split operand is a regular expression
        
        for index in range(0, 4):
            i += 1
            discoveryRequest[i] = int(ipValues[index])
            
        i += 1
        discoveryRequest[i] = self.RTA_DISC_TAG_MULT
        i += 1
        discoveryRequest[i] = 1 # Length of delay multiplier.
        i += 1
        discoveryRequest[i] = self.DELAY_MULTIPLIER
        
        return discoveryRequest
    
    '''
    Parses an RTADevice structure from a discovery response from an RTA device. 
    Param: abResponse, the response data received from the network.
    Return: The RTADeviceStructure represented by the response, or null
    if the response does not contain a valid discovery protocol response.
    '''    
    def parseDiscoveryResponse(self, abResponse):
        
        import RTADevice
        
        rtad = RTADevice.RTADevice()
        
        for i in range(0, len(self.DISCOVERY_RESPONSE_HEADER)): # First check response for correct header.
            if abResponse[i] != self.DISCOVERY_RESPONSE_HEADER[i]:
                return None
                
        i += 1
                
        # The message had the correct header, ready to start parsing message.
        while i < (len(abResponse)-1):
            iFieldLength_byte = abResponse[i + 1] # Byte after tag specifier is the field length
            iFieldLength = self.struct.unpack('b', iFieldLength_byte)[0]
            
            if ((i + 2 + iFieldLength) > len(abResponse)):
                return None # The field length specified goes beyond the end of the packet, packet is invalid.
            
            abResponse_i_byte = abResponse[i]
            abResponse_i = self.struct.unpack('b', abResponse_i_byte)[0]
            
            if abResponse_i == self.RTA_DISC_TAG_MAC: # Mac address field.
                rtad.m_macstring = ''
                for k in range(0, iFieldLength):
                    # note:  I am conditionally adding 256 to the bytes from abResponse because java falsely thinks they
                    # represent negative numbers instead of unsigned positive numbers.  Java does not support
                    # unsigned variables, so I took a roundabout way to accomplish the same task.
                    tempValue_byte = abResponse[i + 2 + k]
                    tempValue = self.struct.unpack('b', tempValue_byte)[0]
                    if (tempValue >= 0):
                        value = tempValue
                    else:
                        value = tempValue + 256
                    
                    if k > 0:
                        rtad.m_macstring += '-'
                    
                    if value<16:
                        rtad.m_macstring += '0%s' % hex(value)[2:] # Generate two characters for mac address fields.
                    else:
                        rtad.m_macstring += '%s' % hex(value)[2:]
                
            elif abResponse_i == self.RTA_DISC_TAG_IP: # IP Address field.
                if iFieldLength != self.IP_FIELD_LENGTH:
                    return None
                rtad.m_ipa = self.IPFromSubArray(abResponse, i + 2)
                
            elif abResponse_i == self.RTA_DISC_TAG_MASK: # Netmask Field.
                if (iFieldLength != self.IP_FIELD_LENGTH):
                    return None
                rtad.m_ipaNetmask = self.IPFromSubArray(abResponse, i + 2)
                
            elif abResponse_i == self.RTA_DISC_TAG_APP: # Application Description field.
                rtad.m_strApplication = ''
                # Precondition: iFieldLength = length of description field in
                # response, abResponse = response from RTA device, i = position
                # of application description tag in response, rtad.m_strApplication
                # = "".
                # Postcondition: rtad.m_strApplication = The application
                # description from the response, j = length of the description.
                for j in range(0, iFieldLength):
                    rtad.m_strApplication += abResponse[i + 2 + j]
            
            elif abResponse_i == self.RTA_DISC_TAG_LOC:
                rtad.m_strLocation = ''
                for j in range(0, iFieldLength):
                    rtad.m_strLocation += abResponse[i + 2 + j]
            
            else:
                pass
            
            
            i += iFieldLength + 2 # Move i to next tag
            
        return rtad
                
    def IPFromSubArray(self, abPacket, iStartPos):
        
        abSubArray = [] # The subarray containing ip address.
        
        # Precondition: abSubArrray has IP_FIELD_LENGTH slots, abPacket = the response
        # packet, iStartPos = the position of the IP address in the response packet.
        # Postcondition: abSubArray has the elements of the IP address, i ==
        # IP_FIELD_LENGTH.
        
        abSubArray.append(self.struct.unpack('B', abPacket[iStartPos+0])[0])
        abSubArray.append(self.struct.unpack('B', abPacket[iStartPos+1])[0])
        abSubArray.append(self.struct.unpack('B', abPacket[iStartPos+2])[0])
        abSubArray.append(self.struct.unpack('B', abPacket[iStartPos+3])[0])
        
        return '%i.%i.%i.%i' %(abSubArray[0], abSubArray[1], abSubArray[2], abSubArray[3])
        
'''

USEFUL INFO:

AF_UNIX: single string
AF_INET: (host, port)

    host is a string representing either a hostname in Internet domain notation 
    like 'daring.cwi.nl' or an IPv4 address like '100.50.200.5'
    OR the empty string ('') represents INADDR_ANY, and the string 
    '<broadcast>' represents INADDR_BROADCAST
    
    port is an integer
    
First argument to socket(), these constants represent the address (and 
protocol) families:
    socket.AF_UNIX
    socket.AF_INET
    socket.AF_INET6
    
Second argument to socket(), these constants represent the socket types:
    socket.SOCK_STREAM
    socket.SOCK_DGRAM
    socket.SOCK_RAW
    socket.SOCK_RDM
    socket.SOCK_SEQPACKET
    
To get current IP of computer: socket.gethostbyname(socket.gethostname())

'''