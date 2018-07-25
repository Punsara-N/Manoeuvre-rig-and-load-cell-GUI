'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 13-06-2017
-------------------------------------------------------------------------------------------------
'''

''' The active calibration. '''
class Calibration:

    ActiveCalibration   = 0                 # Active calibration.
    ActiveTransducer    = 0                 # Active transducer.
    SerialNumber        = ''                # Serial number.
    PartNumber          = ''                # Part number of a calibration.
    CalibrationDate     = ''                # Calibration date.
    Matrix              = None              # Calibration matrix.
    GainOffset          = None              # Gain and offset data matrix.
    ForceUnits          = 'Force Counts'    # Force units.
    TorqueUnits         = 'Torque Counts'   # Torque units.
    CountsPerUnitForce  = 1                 # Counts per unit force.
    CountsPerUnitTorque = 1                 # Counts per unit torque.
    MaxRatings          = ''                # The max ratings of each Gage.

    def __int__(self):
        pass

    '''
    Fills a calibration structure from values in the response to the "CAL"
    console command of the Wireless F/T.
    @param calCommandResponse The response to the "CAL" command from the
    Wireless F/T.
    @return A calibration structure initialized based on the fields in the
    response.
    '''
    def parseCalibrationFromTelnetResponse(self, calCommandResponse):
        
        lines     = calCommandResponse.split('\r\n')    # The individual lines.
        splitLine = lines[3].strip().split()            # The first matrix line split at whitespace.

        self.ActiveTransducer   = int(splitLine[0])
        self.ActiveCalibration  = int(splitLine[1])
        self.SerialNumber       = self.getFieldValue(calCommandResponse, 'Serial: ', '\r\n')
        self.CalibrationDate    = self.getFieldValue(calCommandResponse, 'Date:   ', '\r\n')
        self.PartNumber         = self.getFieldValue(calCommandResponse, 'Part:   ', '\r\n')

        ''' Parse matrix info. '''
        numAxes   = 6
        numGauges = 6
        self.Matrix     = []
        for i in range(0, numAxes):
            self.Matrix.append(0) # Initiatizing matrix with numAxes number of rows
        self.MaxRatings = [''] * numAxes    # Initializing empty string array of size numAxes
        axisNames  = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']

        for axis in range(0, numAxes):
            A = []
            for ii in range(0, numGauges):
                A.append(0)
            self.Matrix[axis] = A # Each matrix row will have numGauges number of columns

            ''' The line containing the gage coefficients for this axis. '''
            axisText            = self.getFieldValue(calCommandResponse, axisNames[axis], "\r\n").strip()
            axisCoefficients    = axisText.split()

            if (len(axisCoefficients) < numGauges):
                print('Could not parse all gage coefficients for axis from command response.')

            for gage in range(0, numGauges):
                self.Matrix[axis][gage] = float(axisCoefficients[gage])

        ''' Parse gain and offset info. '''
        self.GainOffset     = [[] * 2] * numAxes
        numLinesConsole     = 11

        consoleLines = [''] * numLinesConsole
        consoleLinesList = [] # See "https://www.tutorialspoint.com/python/python_lists.htm" for list methods
        console = lines # Java uses "scanner" method to read string lines
        
        for i in range(0,len(consoleLines)):
            consoleLines[i] = console[i]
            consoleLines_split = consoleLines[i].split()
            consoleLinesList_temp = []

            for j in range(0,len(consoleLines_split)):
                consoleLinesList_temp.append(consoleLines_split[j])

                for k in range(0,len(consoleLinesList_temp)):
                    if consoleLinesList_temp[k] == '':
                        del consoleLinesList_temp[k]

            consoleLinesList.append(consoleLinesList_temp)     

        for i in range(0,3): # Remove header information.
            del consoleLinesList[0]

        gainGrab   = 2
        offsetGrab = 3

        for i in range(0,len(self.GainOffset)):
            gain   = int(consoleLinesList[i][gainGrab])
            offset = int(consoleLinesList[i][offsetGrab])
            self.GainOffset[i] = [gain, offset]

        ''' The force and torque counts/unit string. '''
        countsAndUnits           = self.getFieldValue(calCommandResponse, 'Force:', '\r\n').strip()
        splitCountsAndUnits      = countsAndUnits.split('counts/')
        self.CountsPerUnitForce  = int(splitCountsAndUnits[0].strip())
        if len(splitCountsAndUnits) > 1: # Don't check if there's no units set.
            self.ForceUnits = splitCountsAndUnits[1].strip()
        else:
            self.ForceUnits = ''

        countsAndUnits            = self.getFieldValue(calCommandResponse, 'Torque:', '\r\n').strip()
        splitCountsAndUnits       = countsAndUnits.split('counts/')
        self.CountsPerUnitTorque  = int(splitCountsAndUnits[0].strip())
        if len(splitCountsAndUnits) > 1: # Don't check if there's no units set.
            self.TorqueUnits = splitCountsAndUnits[1].strip()
        else:
            self.TorqueUnits = ''

        ''' Get all six max ratings. '''
        for i in range(0,len(lines)):
            line = lines[i]

            if 'MaxRatings' in line:
                tokens = lines[i+1].split()
                n = len(tokens) - 3
                n = max(n, 0) # n is always an integer between 0 and 6
                n = min(n, 6) # n is always an integer between 0 and 6

                for j in range(0,n):
                    self.MaxRatings[j] = tokens[j+3]
                


    def max(self,a,b):
        if a>b:
            return a
        else:
            return b

    def getMaxRangeForce(self):
        maxRF = float(self.MaxRatings[0])
        maxRF = max(float(self.MaxRatings[1]), maxRF)
        maxRF = max(float(self.MaxRatings[2]), maxRF)
        return str(maxRF)

    def getMaxRangeTorque(self):
        maxRT = float(self.MaxRatings[3])
        maxRT = max(float(self.MaxRatings[4]), maxRT)
        maxRT = max(float(self.MaxRatings[5]), maxRT)
        return str(maxRT)

    def getFieldValue(self, commandResponse, beginMarker, endMarker):
        startIndex = commandResponse.index(beginMarker) + len(beginMarker)
        endIndex   = commandResponse.index(endMarker, startIndex)
        if (startIndex == -1 or endIndex == -1):
            print('Field begin or end not found in command response.')
        return commandResponse[startIndex:endIndex]

    def getSerialNumber(self):
        return self.SerialNumber

    def setSerialNumber(self, SerialNumber):
        self.SerialNumber = SerialNumber

    def getPartNumber(self):
        return self.PartNumber

    def setPartNumber(self, PartNumber):
        self.PartNumber = PartNumber

    def getCalibrationDate(self):
        return self.CalibrationDate

    def setCalibrationDate(self, CalibrationDate):
        self.CalibrationDate = CalibrationDate
    
    def getActiveCalibration(self):
        return self.ActiveCalibration
    
    def getActiveTransducer(self):
        return self.ActiveTransducer

    def getMatrix(self):
        return self.Matrix

    def setMatrix(self, Matrix):
        self.Matrix = Matrix

    def getForceUnits(self):
        return self.ForceUnits

    def setForceUnits(self, ForceUnits):
        self.ForceUnits = ForceUnits

    def getTorqueUnits(self):
        return self.TorqueUnits

    def setTorqueUnits(self, TorqueUnits):
        self.TorqueUnits = TorqueUnits

    def getCountsPerUnitForce(self):
        return self.CountsPerUnitForce

    def setCountsPerUnitForce(self, CountsPerUnitForce):
        self.CountsPerUnitForce = CountsPerUnitForce

    def getCountsPerUnitTorque(self):
        return self.CountsPerUnitTorque

    def setCountsPerUnitTorque(self, CountsPerUnitTorque):
        self.CountsPerUnitTorque = CountsPerUnitTorque
    
    def getGainOffset(self):
        return self.GainOffset

    def setGainOffset(self, GainOffset):
        self.GainOffset = GainOffset

    def getForceTorqueConversionFactors(self, outputForceUnits, outputTorqueUnits, transducer):
        forceUnits        = ["", "lbf",    "klbf",     "n",       "kn",          "g",        "kg",         "mv"] # The supported force  units.
        torqueUnits       = ["", "lbf-in", "lbf-ft",   "n-m",     "n-mm",        "kg-cm",    "kn-m",       "mv"] # The supported torque units.

        forceConversions  = [1.0, 1.0,      0.001,      4.44822,     0.004448222, 453.5924,   0.4535924,    1.0] # Conversion from lbf    to each element in forceUnits.
        torqueConversions = [1.0, 1.0,      0.08333333, 0.1129848, 112.9848,        1.152128, 0.0001129848, 1.0] # Conversion from lbf-in to each element in torqueUnits.

        ''' It might be better to just throw an Exception here if they try to convert to/from voltage.'''
        reqForceUnits  = self.getForceUnits().lower() # For case-insensitive searching.
        reqTorqueUnits = self.getTorqueUnits().lower()

        outputForceUnits  = outputForceUnits.lower()
        outputTorqueUnits = outputTorqueUnits.lower()

        calibrationForceIndex = -1 # The index of the calibration force units in forceUnits.
        userForceIndex        = -1 # The index of the requested   force units in forceUnits.

        for i in range(0,len(forceUnits)):
            if (forceUnits[i] == reqForceUnits):
                calibrationForceIndex = i
            if (forceUnits[i] == outputForceUnits):
                userForceIndex = i

        if (calibrationForceIndex == -1):
            print("Calibration force unit '" + reqForceUnits    + "' on Transducer " + str(transducer + 1) + " is not a supported unit.") # Transducer is origin 1 to the user
            
        if (userForceIndex == -1):
            print("Requested force unit '"   + outputForceUnits + "' on Transducer " + str(transducer + 1) + " is not a supported unit.") # Transducer is origin 1 to the user

        calibrationTorqueIndex = -1 # The index of the calibration torque units in torqueUnits.
        userTorqueIndex        = -1

        for i in range(0,len(torqueUnits)):
            if (torqueUnits[i] == reqTorqueUnits):
                calibrationTorqueIndex = i
            if (torqueUnits[i] == outputTorqueUnits):
                userTorqueIndex = i

        if (calibrationTorqueIndex == -1):
            print( "Calibration torque unit '" + reqTorqueUnits    + "' on Transducer " + str(transducer + 1) + " is not a supported unit." ) # Transducer is origin 1 to the user

        if (userTorqueIndex == -1):
            print( "Requested torque unit '"   + outputTorqueUnits + "' on Transducer " + str(transducer + 1) + " is not a sported unit." ) #  Transducer is origin 1 to the user

        forceFactor  = forceConversions[userForceIndex]/forceConversions[calibrationForceIndex]
        torqueFactor = torqueConversions[userTorqueIndex]/torqueConversions[calibrationTorqueIndex]
        
        return [forceFactor, forceFactor, forceFactor, torqueFactor, torqueFactor, torqueFactor]
