'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 22-06-2017
-------------------------------------------------------------------------------------------------
'''

'''
Represents the XML profiles used by the Java Demo to set the state of a connected WNet.
@author colch (ATI)
'''
class WirelessFTDemoProfile:
    
    ''' ---------- Default Settings ---------- '''
    DEFAULT_RATE                    = '125'
    DEFAULT_OVERSAMPLING            = '32'
    DEFAULT_SD                      = 'OFF'
    DEFAULT_FORCE_UNITS             = 'Default'
    DEFAULT_TORQUE_UNITS            = 'Default'
    DEFAULT_FILTER_TYPE             = 'Running Mean'
    DEFAULT_FILTER_VALUE            = '8'
    DEFAULT_DISPLACEMENT_UNITS      = 'm'
    DEFAULT_ROTATION_UNITS          = 'Degrees'
    
    DEFAULT_XPWR    = ['ON', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF']
    
    DEFAULT_FILTERS = [[DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
                       [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
                       [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
                       [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
                       [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
                       [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE]]
                       
    DEFAULT_CALS = ['0', '0', '0', '0', '0', '0'] # Calibration defaults = "Default"
    
    DEFAULT_XFORMS = [[[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
                      [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
                      [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
                      [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
                      [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
                      [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]]]
                      
    NUM_SENSORS = 6
    
    ''' 6x6 Identity matrices for each sensor. '''
    IDENTITY_MATRICES = [
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ],
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ],
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ],
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ],
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ],
        [
            [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]
        ]
    ]

    ''' ----------      ^END^      ---------- '''

    ''' The rate at which to send UDP packets, initially the default profile's value. '''
    m_rate = DEFAULT_RATE
    
    ''' The rate at which to sample transducer data, initially the default profile's value. '''
    m_oversampling = DEFAULT_OVERSAMPLING
    
    ''' Whether or not the MicroSD is recording, initially the default profile's value. '''
    m_sd = DEFAULT_SD
    
    ''' The units used to measure force, initially the default profile's value. '''
    m_force = DEFAULT_FORCE_UNITS
    
    ''' The units used to measure torque, initially the default profile's value. '''
    m_torque = DEFAULT_TORQUE_UNITS
    
    ''' The active transducers, initially the default profile's value. '''
    m_xpwr = DEFAULT_XPWR
    
    ''' The filters, initially the default profile's value. '''
    m_filters = DEFAULT_FILTERS
    
    '''
    The active calibrations, initially the default profile's value.
    Format: [command to set transducer]|[calibration for that transducer]
    '''
    m_cals = DEFAULT_CALS
    
    ''' The rotations and displacements as strings, initially the default profile's value. '''
    m_xforms = DEFAULT_XFORMS
    
    ''' The rotation and displacement values initially the identity. '''
    m_xformValues = IDENTITY_MATRICES
    
    m_Notes = ""
    
    m_Wnet = 3 #  WNet-3 or WNet-6
    
    m_ntpUse           = False
    m_ntpServer        = ''
    m_ntpOffsetHours   = 0
    m_ntpOffsetMinutes = 0
    m_ntpDst           = True
    
    def __init__(self):
        
        ''' Conversion constants. '''
        self.CONVERT_DISP_INCHES_IN          =  1
        self.CONVERT_DISP_FEET_FT            = 12
        self.CONVERT_DISP_METERS_M           = 39.3701
        self.CONVERT_DISP_CENTIMETERS_CM     =  0.393701
        self.CONVERT_DISP_MILLIMETERS_MM     =  0.0393701
        
        self.m_displacementConversionFactors = [self.CONVERT_DISP_INCHES_IN, self.CONVERT_DISP_FEET_FT, self.CONVERT_DISP_METERS_M, 
                                                self.CONVERT_DISP_CENTIMETERS_CM, self.CONVERT_DISP_MILLIMETERS_MM]
        
        ''' Constructs a new profile with the default settings for a new WNet. '''                                        
        self.m_rate         = self.DEFAULT_RATE
        self.m_oversampling = self.DEFAULT_OVERSAMPLING
        self.m_sd           = self.DEFAULT_SD
        self.m_force        = self.DEFAULT_FORCE_UNITS
        self.m_torque       = self.DEFAULT_TORQUE_UNITS
        self.m_xpwr         = self.DEFAULT_XPWR
        self.m_filters      = self.DEFAULT_FILTERS
        self.m_cals         = self.DEFAULT_CALS
        self.m_xforms       = self.DEFAULT_XFORMS
        self.m_Notes        = ''
        self.m_Wnet         = 3

        self.m_ntpUse           = False
        self.m_ntpServer        = ''
        self.m_ntpOffsetHours   = 0
        self.m_ntpOffsetMinutes = 0
        self.m_ntpDst           = True
      
        
    '''
    Constructs a custom WNet profile based on a given XML file.
    @param profileXML The file to parse.
    @throws Exception If file-parse failed.
    '''
    def WirelessFTDemoProfile(self, profileXML):  # Input arg example: 'DefaultProfile.xml'
        try:
            open(profileXML, 'rt')
        except Exception as e:
            print("No XML file provided.")
            print(e)
        
        self.parseXMLToWNetProfile(profileXML) # Read the xml file
        
    '''
    Populates the fields of this demo profile with settings from a valid-format XML profile.
    @param profileXML The file to parse.
    @throws Exception If the file cannot be parsed for any reason.
    '''
    def parseXMLToWNetProfile(self, profileXML): # Read the xml file
        from xml.etree import ElementTree
        with open(profileXML, 'rt') as f:
            tree = ElementTree.parse(f)
            
        general = tree.find('general')
            
        self.m_rate         = general[0].text # Transmit rate
        self.m_oversampling = general[1].text # Oversampling rate
        self.m_sd           = general[2].text # MicroSD Recording
        self.m_force        = general[3].text # Force units
        self.m_torque       = general[4].text # Torque units
        
        transducers = tree.find('general/transducers')

        for i in range(0, self.NUM_SENSORS):
            self.m_xpwr[i] = transducers[i].text
        
        try: # Try to read the Notes field from the XML file.
            self.m_Notes = general[6].text
        except Exception as e: # If the Notes field is not there,
            self.m_Notes = '' # put in the default.
        
        try: # Try to read the WNet field from the XML file.
            self.m_Wnet = int(general[7].text)
        except Exception as e: # If the WNet field is not there,
            self.m_Wnet = 3 # put in the default.    
        
        try: # Try to read the NTP on/off field from the XML file.
            self.m_ntpUse = general[8].text == 'ON'
        except Exception as e: # If the NTP on/off field is not there,
            self.m_ntpUse = False # put in the default. 
        
        try: # Try to read the NTP server field from the XML file.
            self.m_ntpServer = general[9].text
        except Exception as e: # If the NTP server field is not there,
            self.m_ntpServer = '' # put in the default. 
        
        try: # Try to read the NTP hours field from the XML file.
            self.m_ntpOffsetHours = int(general[10].text)
        except Exception as e: # If the NTP hours field is not there,
            self.m_ntpOffsetHours = 0 # put in the default. 
            
        try: # Try to read the NTP minutes field from the XML file.
            self.m_ntpOffsetMinutes = int(general[11].text)
        except Exception as e: # If the NTP minutes field is not there,    
            self.m_ntpOffsetMinutes = 0 # put in the default.
        
        try: # Try to read the NTP minutes field from the XML file.
            self.m_ntpDst = general[12].text == 'ON'
        except Exception as e: # If the NTP minutes field is not there,    
            self.m_ntpDst = False # put in the default. 
            
        trans = tree.find('filters') # Filters (averaging) for each transducer
        for i in range(0, self.NUM_SENSORS):
            self.m_filters[i][0] = trans[i][0].text
            self.m_filters[i][1] = trans[i][1].text
            
        calibration = tree.find('calibration') # Calibration index for each transducer
        for i in range(0, self.NUM_SENSORS):
            self.m_cals[i] = calibration[i].text
        
        UNITS_AND_VALUES = 4
        transformation = tree.find('transformation') # Transformations for each transducer
        for i in range(0, self.NUM_SENSORS):
            trans = transformation[i]
            disp = trans.find('displacement')
            for j in range(0, UNITS_AND_VALUES):
                self.m_xforms[i][0][j] = disp[j].text
            rot = trans.find('rotation')
            for j in range(0, UNITS_AND_VALUES):
                self.m_xforms[i][1][j] = rot[j].text
                
    def setForceUnits(self, units):
        self.m_force = units
        
    def setTorqueUnits(self, units):
        self.m_torque = units
        
    def setRate(self, rate):
        self.m_rate = "" + str(rate)
        
    def setOversampling(self, ovrsmp):
        self.m_oversampling = "" + str(ovrsmp)
        
    def setSD(self, on):
        if on:
            self.m_sd = 'ON'
        else:
            self.m_sd = 'OFF'
            
    def setXPWR(self, transducer, on):
        if on:
            self.m_xpwr[transducer] = 'ON'
        else:
            self.m_xpwr[transducer] = 'OFF'
            
    def setFilterType(self, transducer, Type):
        self.m_filters[transducer][0] = Type
        
    def setFilterValue(self, transducer, val):
        self.m_filters[transducer][1] = "" + str(val)
        
    def setCal(self, transducer, cal):
        self.m_cals[transducer] = "" +str(cal)
        
    def setDisplacementUnits(self, transducer, units):
        self.m_xforms[transducer][0][0] = units
        
    def setDisplacementValue(self, transducer, val):
        self.m_xforms[transducer][0][1] = "" + str(val)
        
    def setRotationUnits(self, transducer, units):
        self.m_xforms[transducer][1][0] = units
        
    def setRotationValue(self, transducer, val):
        self.m_xforms[transducer][1][1] = "" + str(val)
        
    '''
    Gets the command that should be written to the firmware to set the UDP packet transmit rate.
    @return The rate command.
    '''
    def getRateCommand(self):
        return "RATE " + self.m_rate + " " + self.m_oversampling
        
    '''
    Gets the demo force units.
    @return The force units.
    '''
    def getForceUnits(self):
        return self.m_force
        
    '''
    Gets the demo torque units.
    @return The torque units.
    '''
    def getTorqueUnits(self):
        return self.m_torque
        
    '''
    Gets the firmware command to set whether or not data records will
    be written to the WNet's MicroSD card.
    @return
    '''
    def getSDCommand(self):
        return "SDREC " + self.m_sd
        
    '''
    Gets the firmware command to set power for a particular transducer index.
    @param transducer The index of the transducer.
    @return The xpwr command for that transducer.
    '''
    def getXPWRCommand(self, transducer):
        return "XPWR " + str(transducer + 1) + " " + self.m_xpwr[transducer] #  Transducer is origin 1 to the user
        
    '''
    Gets the filter type (MEAN, MEADIAN, or IIR) for a particular transducer.
    @param transducer The index of the transducer.
    @return The filter type for that transducer.
    '''
    def getFilterType(self, transducer):
        return self.m_filters[transducer][0] # Zero-based in array.
        
    '''
    Gets the filter samples (or time constant) for a particular transducer.
    @param transducer The index of the transducer.
    @return The filter value for that transducer.
    '''
    def getFilterValue(self, transducer):
        return self.m_filters[transducer][1] # Zero-based in array.
        
    '''
    Gets the firmware command to set filter for a particular transducer index.
    @param transducer The index of the transducer.
    @return The filter command for that transducer.
    '''
    def getFilterCommand(self, transducer):
        Filter  = ''
        value   = ''
        Filter  = self.m_filters[transducer][0] # Transducer number is zero-based in array.
        value   = self.m_filters[transducer][1]
        
        if Filter == 'Running Mean':
            Filter = 'Mean'
        elif Filter == 'Running Median':
            Filter = 'Median'
        elif Filter == 'IIR':
            Filter == 'IIR'
        elif Filter == 'No Filtering':
            pass
        else:
            Filter = 'Mean'
            value = 1
           
        return "FILTER " + str(transducer + 1) + " " + Filter + " " + str(value) # Transducer is origin 1 to the user
        
    '''
    Gets the active calibration for a particular transducer.
    @param transducer The index of the transducer.
    @return The calibration index for that transducer.
    '''
    def getActiveCalibration(self, transducer):
        return self.m_cals[transducer] # Zero-based in array.
        
    '''
    Gets the firmware command to set calibration for a particular transducer index.
    @param transducer The transducer number, 0 to 5.
    @return The TRANS command for that transducer.
    '''
    def getTransducerCommand(self, transducer):
        return "TRANS " + str(transducer + 1) # Transducer is origin 1 to the user
        
    '''
    Gets the firmware command to set calibration for a particular transducer index.
    @param transducer The transducer number, 0 to 5.
    @return The CALIB command for that transducer.
    '''
    def getCalibrationCommand(self, transducer):
        cal = self.m_cals[transducer]
        text = ''
        if '0' in cal:
            text = ''
        else:
            text = "CALIB " + cal
        
        return text;
        
    '''
    Gets the displacement units for a particular transducer.
    @param transducer The index of the transducer.
    @return The displacement units for the transducer.
    '''
    def getDisplacementUnits(self, transducer):
        return self.m_xforms[transducer][0][0] # Zero-based in array.
        
    '''
    Gets the applied displacement for a particular transducer index.
    @param transducer The index of the transducer.
    @return The displacement values for the transducer.
    Format: [dx]|[dy]|[dz]
    '''
    def getDisplacementValues(self, transducer):
        xforms = ''
        for i in range(1, len(self.m_xforms[transducer][0])):
            xforms += self.m_xforms[transducer][0][i] + '|'
        return xforms[0 : len(xforms)-1] # Remove trailing |
        
    '''
    Gets the rotation units for a particular transducer.
    @param transducer The index of the transducer.
    @return The rotation units for the transducer.
    '''
    def getRotationUnits(self, transducer):
        return self.m_xforms[transducer][1][0] # Zero-based in array.
        
    '''
    Gets the applied rotation for a particular transducer index.
    @param transducer The index of the transducer.
    @return The rotation values for the transducer.
    Format: [rx]|[ry]|[rz]
    '''
    def getRotationValues(self, transducer):
        xforms = ''
        for i in range(1, len(self.m_xforms[transducer][1])):
            xforms += self.m_xforms[transducer][1][i] + '|'
        return xforms[0 : len(xforms)-1] # Remove trailing |
        
    '''
    Gets the transformation matrix for a particular transducer index.
    @param transducer The zero-based index of the transducer.
    @return The transformation matrix.
    '''
    def getTransformationMatrix(self, transducer):
        return self.m_xformValues[transducer]
        
    '''
    Applies tool transformations for each transducer,
    setting the matrix locally to prevent doing the
    transformation math each time a sample comes in.
    '''
    def applyTransformations(self):
        import math
        
        rotations       = self.IDENTITY_MATRICES # Rotations are done from scratch.
        displacements   = self.IDENTITY_MATRICES # Displacements are a modified identity matrix (see below).
        rChanged = [False] * self.NUM_SENSORS # Did we apply a rotation/displacement to this transducer?
        dChanged = [False] * self.NUM_SENSORS
        
        # Setup the rotation matrix.
        for i in range(0, self.NUM_SENSORS):
            rotationUnits = self.getRotationUnits(i)
            if not not rotationUnits:
                if rotationUnits == 'Radians':
                    radians = True
                elif rotationUnits == 'Degrees':
                    radians = False
                else: # No units selected, no rotation.
                    rChanged[i] = False
                    
                '''
                Setup the rotation matrix.

                ROTATION MATRIX FORMAT (c = cosine, s = sine):
                         [0]            [1]                [2]             [3]             [4]               [5]
                [0]   | cy*cz   (sx*sy*cz)+(cx*sz)  (sx*sz)-(cx*sy*cz)  |   0               0                 0         |
                [1]   |-cy*sz   (-sx*sy*sz)+(cx*cz) (sx*cz)+(cx*sy*sz)  |   0               0                 0         |
                [2]   |__sy___________-sx*cy______________cx*cy_________|___0_______________0_________________0_________|
                [3]   |   0              0                  0           | cy*cz   (sx*sy*cz)+(cx*sz)  (sx*sz)-(cx*sy*cz)|
                [4]   |   0              0                  0           |-cy*sz   (-sx*sy*sz)+(cx*cz) (sx*cz)+(cx*sy*sz)|
                [5]   |   0              0                  0           |  sy           -sx*cy              cx*cy       |
                '''
                
                try:
                    rX = float(self.getRotationValues(i).split('|')[0]) # Get x, y, and z rotations.
                    rY = float(self.getRotationValues(i).split('|')[1])
                    rZ = float(self.getRotationValues(i).split('|')[2])
                    
                    # if radians: # Convert radians to degrees, if applicable.
                    #    rX = rX * 180 / math.pi
                    #    rY = rY * 180 / math.pi
                    #    rZ = rZ * 180 / math.pi
                    
                    # Above not used because pythons math class methods work in radians
                    if not radians: # Convert radians to degrees, if applicable.
                        rX = math.radians(rX)
                        rY = math.radians(rY)
                        rZ = math.radians(rZ)
                        
                    rotations[i][0][0] =   math.cos(rY) * math.cos(rZ)                                           #  cy*cz
                    rotations[i][3][3] = rotations[i][0][0]
                    
                    rotations[i][0][1] =  (math.sin(rX) * math.sin(rY)*math.cos(rZ))+(math.cos(rX)*math.sin(rZ)) # (sx*sy*cz)+(cx*sz)
                    rotations[i][3][4] = rotations[i][0][1]
                   
                    rotations[i][0][2] =  (math.sin(rX) * math.sin(rZ))-(math.cos(rX)*math.sin(rY)*math.cos(rZ)) # (sx*sz)-(cx*sy*cz)
                    rotations[i][3][5] = rotations[i][0][2]
                   
                    rotations[i][1][0] =  -math.cos(rY) * math.sin(rZ)                                           # -cy*sz
                    rotations[i][4][3] = rotations[i][1][0]
                  
                    rotations[i][1][1] = (-math.sin(rX) * math.sin(rY)*math.sin(rZ))+(math.cos(rX)*math.cos(rZ)) #(-sx*sy*sz)+(cx*cz)
                    rotations[i][4][4] = rotations[i][1][1]
                  
                    rotations[i][1][2] =  (math.sin(rX) * math.cos(rZ))+(math.cos(rX)*math.sin(rY)*math.sin(rZ)) # (sx*cz)+(cx*sy*sz)
                    rotations[i][4][5] = rotations[i][1][2]
                   
                    rotations[i][2][0] =   math.sin(rY)                                                          #  sy
                    rotations[i][5][3] = rotations[i][2][0]
                   
                    rotations[i][2][1] =  -math.sin(rX) * math.cos(rY)                                           # -sx*cy
                    rotations[i][5][4] = rotations[i][2][1]
                   
                    rotations[i][2][2] =   math.cos(rX) * math.cos(rY)                                           #  cx*cy
                    rotations[i][5][5] = rotations[i][2][2]
                    
                    rChanged[i] = True # A valid rotation will be applied.
                    
                except Exception as e:
                    rChanged[i] = False # Something was invalid, do not apply rotation.
                    print e
            
            else:
                rChanged[i] = False # No units, no rotation.
            
        for i in range(0, self.NUM_SENSORS):
            displacementUnits = self.getDisplacementUnits(i)
            
            if not not displacementUnits: # Set the units for this displacement.
                if displacementUnits == 'in':
                    conversion = self.m_displacementConversionFactors[0]
                elif displacementUnits == 'ft':
                    conversion = self.m_displacementConversionFactors[1]
                elif displacementUnits == 'm':
                    conversion = self.m_displacementConversionFactors[2]
                elif displacementUnits == 'cm':
                    conversion = self.m_displacementConversionFactors[3]
                elif displacementUnits == 'mm':
                    conversion = self.m_displacementConversionFactors[4]
                else:
                    dChanged[i] = False # No units selected, no displacement.
                
                '''
                Setup the 3rd quadrant of the displacement matrix.
                
                DISPLACMENT MATRIX FORMAT:
                        [0]  [1]  [2]   [3]  [4]  [5]
                [0]   |  1    0    0  |  0    0    0  |
                [1]   |  0    1    0  |  0    0    0  |
                [2]   |__0____0____1__|__0____0____0__|
                [3]   |  0    dz  -dy |  1    0    0  |
                [4]   | -dz   0    dx |  0    1    0  |
                [5]   |  dy  -dx   0  |  0    0    1  |
                '''
                
                try:
                    dX = float(self.getDisplacementValues(i).split('|')[0]) # Get x, y, and z rotations.
                    dY = float(self.getDisplacementValues(i).split('|')[1])
                    dZ = float(self.getDisplacementValues(i).split('|')[2])
                    
                    displacements[i][3][1] =        dZ * conversion #  dz
                    displacements[i][3][2] = -1.0 * dY * conversion # -dy
                    displacements[i][4][0] = -1.0 * dZ * conversion # -dz
                    displacements[i][4][2] =        dX * conversion #  dx
                    displacements[i][5][0] =        dY * conversion #  dy
                    displacements[i][5][1] = -1.0 * dZ * conversion # -dx
                    dChanged     [i]       = True                   # A valid displacement will be applied.
                except Exception as e:
                    dChanged[i] = False # Something was invalid, do not apply displacement.
                    
            else:
                dChanged[i] = False # No units, no displacement.
                
        self.m_xformValues = self.matrixMult(rotations, displacements, rChanged, dChanged) # [Transformation] = [Rotations]*[Displacements]
        if self.m_xformValues == None: # If they somehow managed to give us invalid dimensions,
            self.m_xformValues = self.IDENTITY_MATRICE # reset to the identity matrix.
    
     
    '''       
    Steps through the 6 rotation/displacement matrices
    and multiplies them together. If a matrix was not
    populated via the Tool Transform settings, it is
    treated as an identity matrix (no effect).
    @param r The matrix of all rotations, valid or otherwise.
    @param d The matrix of all displacements, valid or otherwise.
    @param validR Which transducers are being rotated?
    @param validD Which transducers are being displaced?
    @return The resulting transformation matrices for the 6 transducers.
    '''
    def matrixMult(self, r, d, validR, validD):
        if len(r) != len(d):
            return None # invalid dims
            
        ans = [[[0.0]*self.NUM_SENSORS]*self.NUM_SENSORS]*self.NUM_SENSORS
        
        for x in range(0, self.NUM_SENSORS): # 6 Matrices.
            # Only do math for valid transformations.
            if validR[x] or validD[x]:
                for i in range(0, self.NUM_SENSORS): # 6 Rows each
                    for j in range(0, self.NUM_SENSORS): # 6 Cols in d
                        for k in range(0, self.NUM_SENSORS): # 6 Cols in r
                            ans[x][i][j] += r[x][i][k] * d[x][k][j]
            else: # Don't change this transducer (use the identity matrix).
                for i in range(0, self.NUM_SENSORS):
                    ans[x][i][i] = 1.0
        
        return ans