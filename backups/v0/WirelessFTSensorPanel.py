'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 28-06-2017
-------------------------------------------------------------------------------------------------
'''

class WirelessFTSensorPanel:
    
    import WirelessFTDemoProfile
    import WirelessFTDemoModel
    import time
    
    DEFAULT_RATE = 125  # The default packet send rate.
    UI_UPDATE_HZ = 25.0 # Display new data at this rate.
    m_txtTitle  = ''    # Displays the transducer and serial numbers for a device.
    m_lblFUnits = ''    # Force unit labels.
    m_lblTUnits = ''    # Torque unit labels.
    
    # Axis Toggle Buttons.
    m_btnTitleFx = None
    m_btnTitleFy = None
    m_btnTitleFz = None
    m_btnTitleTx = None
    m_btnTitleTy = None
    m_btnTitleTz = None
    
    # The axis title toggle buttons.
    m_btnAxisTitles = None
    
    # The VBox that groups the data values.
    m_vboxDataDisplay = None
    
    # The toggle group for controlling graph views.
    m_toggleGroupPower = None
    
    # Turns the display on and off.
    m_btnDisplay = None
    
    # The auto-scale check box.
    m_chkAutoscale = None
    
    # The x-axis of the chart.
    m_xAxisForc = None
    m_xAxisTorq = None
    
    # The y-axis of the chart.
    m_yAxisForc = None
    m_yAxisTorq = None
    
    # The line chart that displays the data over time.
    m_lineChartForc = None # Force chart
    m_lineChartTorq = None # Torque chart
    
    m_lblFx = '' # The FX label.
    m_lblFy = '' # The FY label.
    m_lblFz = '' # The FZ label.
    m_lblTx = '' # The TX label.
    m_lblTy = '' # The TY label.
    m_lblTz = '' # The TZ label.
    
    m_ftLabels = '' # The labels that display the current data.
    
    # The WNet profile which applies to all transducers.
    m_profile = WirelessFTDemoProfile.WirelessFTDemoProfile()
    
    # The sensor within the WNet for which this panel is displaying data.
    m_sensorIndex = None
    
    # The number of UI update cycles.
    m_uiTicks = 0
    
    # The total graph history displayed.
    m_historySeconds = 10.0
    
    # The current F/T or gage data.
    m_currentData = []
    for i in range(0, WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES)  :
        m_currentData.append([])
    
    # The current power setting.
    m_powerSetting = 1
    
    # Conversion factors.
    CONVERT_FORCE_POUND_LBF      =    1
    CONVERT_FORCE_KILOPOUND_KLBF = 1000
    CONVERT_FORCE_NEWTON_N       =    4.448222
    CONVERT_FORCE_KILONEWTON_KN  =    0.004448222
    CONVERT_FORCE_GRAM_G         =  453.5924
    CONVERT_FORCE_KILOGRAM_KG    =    0.4535924
    
    CONVERT_TORQUE_POUND_INCHES_LBFIN       =   1
    CONVERT_TORQUE_POUND_FEET_LBFFT         =   0.0833333
    CONVERT_TORQUE_NEWTON_METER_NM          =   0.1129848
    CONVERT_TORQUE_NEWTON_MILLIMETER_NMM    = 112.984829
    CONVERT_TORQUE_KILOGRAM_CENTIMETER_KGCM =   1.15212462
    CONVERT_TORQUE_KILONEWTON_METER         =   0.000112985
    
    m_forceUnits  = 'N'
    m_torqueUnits = 'N-m'
    
    m_forceConversionFactor  = 1
    m_torqueConversionFactor = 1
    
    # Are we displaying secondary axis?
    m_forceTorqueButton = False

    # Used to monitor bias requests. (Use a listner in python, pubsub)
    def biasMonitor(self):
        pass
    
    # Used to monitor un-bias requests.
    def unbiasMonitor(self):
        pass
    
    # Set the action to take when the user requests a bias.
    def eventBias(self):
        pass
    
    # Set the action to take when the user requests an un-bias.
    def eventUnbias(self):
        pass
    
    # Called when the bias button is pressed.
    def biasButtonPressed(self):
        pass
    
    # Called when the clear button is pressed.
    def unbiasButtonPressed(self):
        pass
    
    # Gets the current power setting for this transducer.
    # 0 = on, 1 = off, 2 = warm/idle
    def getPowerSetting(self):
        return self.m_powerSetting
        
    # Set the sample data to which this sensor corresponds,
    # then apply transformations (if applicable).
    def setSensorData(self, sample):
        gageData = sample.getFtOrGageData()[self.m_sensorIndex]
        for i in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES): # For each data channel,
            self.m_currentData[i] = gageData[i]
        # Apply transformations for this transducer, if there were any.
        # Putting self.m_currentData into a column vector
        currentDataColumn = []
        for ii in self.m_currentData:
            currentDataColumn.append([ii])
        self.m_currentData = currentDataColumn
        self.m_currentData = self.matrixMult(self.m_profile.getTransformationMatrix(self.m_sensorIndex), self.m_currentData)
        
    # Called when the auto-scale check-box is pressed.
    def autoscaleChecked(self):
        pass 
    
    # Checks to see how many seconds have passed since this panel was first drawn.
    def timeInSeconds(self):
        return self.m_uiTicks / self.UI_UPDATE_HZ
        
    def SetForceTorqueOrRawCounts(self, forceTorque):
        if forceTorque: # If displaying in force/torque only,
            pass
        else: # If we are only displaying the primary X axis,
            pass
    
    # Creates new WirelessFTSensorPanel (see JAVA source code)
    def WirelessFTSensorPanel(self, profile):
        self.m_profile = profile
    
    # Displays the most-recently read data.
    def updatePlot(self):
        
        voltage = self.m_forceUnits.lower()=='mv'
        if not self.m_forceTorqueButton: # If displaying in gage,
            forceCF      = 1.0
            torqueCF     = 1.0
            numberFormat = '%12.0f'
            self.FUnitsHeading = 'Raw counts'
            self.TUnitsHeading = ' '
            #self.m_lblFUnits.setText('Raw counts');
            #self.m_lblTUnits.setText('');
        elif voltage: # If displaying in voltage,
            forceCF      = self.m_forceConversionFactor
            torqueCF     = self.m_torqueConversionFactor
            numberFormat = '%12.4f'
            self.FUnitsHeading = 'Voltage (' + self.m_forceUnits  + ')'
            self.TUnitsHeading = ' '
            #self.m_lblFUnits.setText("Voltage (" + m_forceUnits  + ")")
            #self.m_lblTUnits.setText("")
        else: # If displaying in force/torque,
            forceCF      = self.m_forceConversionFactor;
            torqueCF     = self.m_torqueConversionFactor;
            numberFormat = '%12.4f'
            self.FUnitsHeading = 'Force ('   + self.m_forceUnits  + ')'
            self.TUnitsHeading = 'Torque ('  + self.m_torqueUnits + ')'
            #self.m_lblFUnits.setText("Force ("   + m_forceUnits  + ")");
            #self.m_lblTUnits.setText("Torque ("  + m_torqueUnits + ")")
        
        #self.m_yAxisForc.setLabel(m_lblFUnits.getText());
        #self.m_yAxisTorq.setLabel(m_lblTUnits.getText());
        
        #self.m_yAxisForc.setForceZeroInRange(m_forceTorqueButton);
        #self.m_yAxisTorq.setForceZeroInRange(m_forceTorqueButton);
        
        timeNow           = self.time.time() # Note that this is the current python time, not the Wnet packet generation time.
        minimumLowerBound = timeNow - self.m_historySeconds # Timestamp of the oldest data we should be displaying.
        
        # Add new data to chart series, and erase old data if necessary.
        wholeStringForces = ''
        wholeStringMoments = ''
        for gage in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES):
            if gage < self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES/2: # Pick the correct units
                units = forceCF
            else:
                units = torqueCF
            value  = self.m_currentData[gage][0] * units # Get current gage data, convert to units
            number = numberFormat % value # get data value to be printed left of graph
            #self.m_ftLabels[gage].setText(number) # Print the number on the graph
            if gage < 3:
                wholeStringForces = wholeStringForces + number + '\n\n'
            else:
                wholeStringMoments = wholeStringMoments + number + '\n\n'
        return [wholeStringForces, wholeStringMoments]
            
    # Gets the index of the sensor represented by this panel.
    def getSensorIndex(self):
        return self.m_sensorIndex
        
    # Sets which sensor in the WNet to display on this panel.
    def setSensorIndex(self, transducer):
        self.m_sensorIndex = transducer
        
    # Changes the title on this graph panel.
    def setTitle(self, title):
        #self.m_txtTitle.setText(title)
        pass
    
    # Sets the force conversion factors.
    def setConversions(self, forceConv, torqueConv):
        self.m_forceConversionFactor  = forceConv
        self.m_torqueConversionFactor = torqueConv
    def setForceTorqueUnits(self, fUnits, tUnits):
        self.m_forceUnits  = fUnits
        self.m_torqueUnits = tUnits
        
    # Sets the axis labeling.
    def setDataDisplay(self, forceTorqueButton) :
        self.m_forceTorqueButton = forceTorqueButton
        voltage = self.m_forceUnits.lower()=='mv'
        ft      = self.m_forceTorqueButton and not voltage # If force/torque button is pressed and we are not displaying in mV, display in force/torque.
        if ft: # If force/torque,
            labelText = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']
        else: # If voltage or gage,
            labelText = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5']
        for i in range(0, self.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES):
            label = labelText[i]
            #self.m_btnAxisTitles[i].setText(label)
        self.SetForceTorqueOrRawCounts(ft)
        
    def matrixMult(self, A, B):
        # Creating size of results matrix.
        results = []
        numOfRowsInMatrixA = len(A)
        numOfColoumnsInMatrixB = len(B[0])
        for ii in range(0, numOfRowsInMatrixA): # This will create the right number of rows.
            results.append([])
            for jj in range(0, numOfColoumnsInMatrixB): # This will create the right number of columns.
                results[ii].append(0)
    
        # Iterate through rows of A.
        for i in range(len(A)):
           # Iterate through columns of B
           for j in range(len(B[0])):
               # Iterate through rows of B
               for k in range(len(B)):
                   results[i][j] += A[i][k] * B[k][j]
                  
        return results
    
    def __init__(self, profile):
        self.WirelessFTSensorPanel(profile)