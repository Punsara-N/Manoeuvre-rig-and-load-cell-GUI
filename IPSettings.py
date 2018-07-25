'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 14-06-2017
-------------------------------------------------------------------------------------------------
'''

''' The Wi-Fi and IP settings for a Wireless F/T. '''
class IPSettings:

    AntennaSetting      = ['External', 'Internal']              # The possible antenna settings.
    Antenna             = ''                                    # The antenna setting.
    BandSetting         = ['Spectrum2_4Ghz', 'Spectrum5Ghz']    # The possible band settings.
    Band                = BandSetting[0]                        # The band setting.
    DHCP                = True                                  # Whether or not the DHCP is turned on.
    IPAddress           = '192.168.1.20'                        # The IP address.
    DefaultGateway      = '192.168.1.1'                         # The default gateway.
    SubnetMask          = "255.255.255.0"                       # The subnet mask.
    SSID                = "Test"                                # The Wi-Fi SSID.

    def __init__(self):
        pass

    ''' Initializes IP settings based on IP command response from the Wireless F/T. '''
    def IPSettings(self, ipCommandResponse):
        antenna = self.getFieldValue(ipCommandResponse, 'ANTENNA', '\r\n').strip();
        ant     = antenna.split(' ')

        if ant[0] == 'External':
            self.Antenna = self.AntennaSetting[0]
        elif ant[0] == 'Internal':
            self.Antenna = self.AntennaSetting[1]
        else:
            print('Unexpected value for antenna setting.')

        B = self.getFieldValue(ipCommandResponse, 'BAND', '\r\n').strip()
        if B == '2.4 GHz':
            Band = self.BandSetting[0]
        elif B == '5 GHz':
            Band = self.BandSetting[1]
        else:
            print('Unexpected value for band setting.')

        dhcp                = self.getFieldValue(ipCommandResponse, 'NET DHCP', '\r\n').strip()
        self.DHCP           = dhcp.upper()
        self.IPAddress      = self.getFieldValue(ipCommandResponse, 'DEVIP',    '\r\n').strip()
        self.DefaultGateway = self.getFieldValue(ipCommandResponse, 'GATEIP',   '\r\n').strip()
        self.SSID           = self.getFieldValue(ipCommandResponse, 'SSID',     '\r\n').strip()
        self.SubnetMask     = self.getFieldValue(ipCommandResponse, 'NETMASK',  '\r\n').strip()

        splitIP      = self.IPAddress.split(' ')
        splitGateway = self.DefaultGateway.split(' ')
        splitSSID    = self.SSID.split(' ')
        splitMask    = self.SubnetMask.split(' ')
        split        = [splitIP, splitGateway, splitSSID, splitMask]

        print(split)

        ipData      = []
        gatewayData = []
        SSIDData    = []
        maskData    = []
        data        = [ipData, gatewayData, SSIDData, maskData]

        for i in range(0,len(split)):
            for j in range(0,len(split[i])):
                item = split[i]
                if not split[i][j]:
                    data[i].append(item)

        print(data)

        self.IPAddress      = ipData[0]
        self.DefaultGateway = gatewayData[1]
        self.SSID           = SSIDData[1]
        self.SubnetMask     = maskData[1]
            

        
    def getFieldValue(self, commandResponse, beginMarker, endMarker):
        startIndex = commandResponse.index(beginMarker) + len(beginMarker)
        endIndex   = commandResponse.index(endMarker, startIndex)
        if (startIndex == -1 or endIndex == -1):
            print('Field begin or end not found in command response.')
        return commandResponse[startIndex:endIndex]
