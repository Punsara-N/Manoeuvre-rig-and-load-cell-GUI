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

class RTADevice:
    
    m_ipa               = ''    # The IP address of the device.
    m_macstring         = ''    # String representation of mac address
    m_ipaGateway        = ''    # The device's default gateway.
    m_ipaNetmask        = ''    # The network mask of the device.
    m_strApplication    = ''    # The application description string of the device, i.e. what it is, its name.
    m_strLocation       = ''    # The location of the device. This is a string provided by the Wnet.
    
    def __init__(self):
        pass
    
    def toString(self):
        
        # Convert IP Address to good looking string. toString() works but puts a "/" in front of the ip address.
        tempByteArray = self.m_ipa.split('.')
        tempString = ''
        
        for i in range(0, 4):
            x = tempByteArray[i]
            if x < 0:
                x += 256 # Compensate for the lack of an unsigned char type.
            tempString += str(x)
            if i < 3:
                tempString += '.'
                
        return 'IP: %s, MAC: %s, INFO: %s, LOC: %s' %(tempString, self.m_macstring, self.m_strApplication, self.m_strLocation)
        
    ''' Compares two RTADevices for equality. Returns True if obj has the same property values as this. '''    
    def Equals(self, obj):
        return (obj.m_ipa==self.m_ipa \
                and obj.m_ipaGateway==self.m_ipaGateway \
                and obj.m_ipaNetmask==self.m_ipaNetmask \
                and obj.m_macstring==self.m_macstring \
                and obj.m_strApplication==self.m_strApplication \
                and obj.m_strLocation==self.m_strLocation)