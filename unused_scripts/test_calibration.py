''' 
This file contains the tests using in CalibrationTest.java. 
'''

import Calibration

print('-----------------------')

transducer = 0 # Transducer 1

calTest = Calibration.Calibration()
calTest.setForceUnits('A broken force')
calTest.setTorqueUnits('Nm')
try:
    calTest.getForceTorqueConversionFactors('lbf', 'Nm', transducer)
except Exception as e:
    print(e)
    
calTest.setForceUnits('lbf')
calTest.setTorqueUnits('One moment please')
try:
    calTest.getForceTorqueConversionFactors('lbf', 'Nm', transducer)
except Exception as e:
    print(e)
    
calTest.setTorqueUnits('N-m')
try:
    calTest.getForceTorqueConversionFactors('A force for evil.', 'Nm', transducer)
except Exception as e:
    print(e)
    
try:
    calTest.getForceTorqueConversionFactors('lbf', 'turtle', transducer)
except Exception as e:
    print(e)
    
print('-----------------------')

forceUnits    = [ "lbf",    "klbf",   "n",   "kn",   "g",     "kg"   ] # The supported force  units.
torqueUnits   = [ "lbf-in", "lbf-ft", "n-m", "n-mm", "kg-cm", "kn-m" ] # The supported torque units.
expForceConv  = [ 1.0,     0.001,    4.44822,    0.004448222, 453.5924, 0.4535924 ]
expTorqueConv = [ 8.85075, 0.737561, 1.0,     1000,            10.1972, 0.001     ]

for i in range(0, len(forceUnits)):
    results = calTest.getForceTorqueConversionFactors(forceUnits[i], 'n-m', transducer)
    print('Wrong force conversion to ' + forceUnits[i] + ' ' + str(abs( results[0] - expForceConv[i] ) < 0.001) )
for i in range(0, len(torqueUnits)):
    results = calTest.getForceTorqueConversionFactors('lbf', torqueUnits[i], transducer)
    diff = abs(results[3] - expTorqueConv[i])
    print('Wrong torque conversion to ' + torqueUnits[i] + ' ' + str(diff < 0.001) )
    
    
    
''' Test of parseCalibrationFromTelnetResponse method, of class Calibration. '''
# Calibration text that caused a parse error due to units not being set.
calCommandResponse = "CAL\r\n" + \
"Tr Cal   Gain Offset Row           G0        G1        G2        G3        G4        G5  Properties\r\n" + \
"-- ---   ---- ------ ---           --        --        --        --        --        --  ----------\r\n" + \
" 2   0      0  32768   0 Fx         1         0         0         0         0         0  Serial: Serial-4\r\n" + \
" 2   0      0  32768   1 Fy         0         1         0         0         0         0  Date:   1970/01/04\r\n" + \
" 2   0      0  32768   2 Fz         0         0         1         0         0         0  Part:   Part-4\r\n" + \
" 2   0      0  32768   3 Tx         0         0         0         1         0         0  Force:  0 counts/\r\n" + \
" 2   0      0  32768   4 Ty         0         0         0         0         1         0  Torque: 0 counts/\r\n" + \
" 2   0      0  32768   5 Tz         0         0         0         0         0         1  Mult:   ON\r\n" + \
" 2                 0 MaxRatings:\r\n" + \
" 2                 0                0         0         0         0         0         0\r\n" + \
">"

expResult = Calibration.Calibration()
expResult.setCalibrationDate("1970/01/04");
expResult.setSerialNumber("Serial-4");
expResult.setCountsPerUnitForce(0);
expResult.setCountsPerUnitTorque(0);
expResult.setForceUnits("");
expResult.setTorqueUnits("");
expResult.setPartNumber("Part-4")

# Create identity matrix.
identityMatrix = []
for i in range(0, 6):
    A = []
    for j in range(0, 6):
        A.append(0)
    identityMatrix.append(A)
    
for i in range(0, 6):
    for j in range(0, 6):
        if i == j:
            identityMatrix[i][j] = 1
        else:
            identityMatrix[i][j] = 0

expResult.setMatrix(identityMatrix)

result = Calibration.Calibration()
result.parseCalibrationFromTelnetResponse(calCommandResponse)

# Comparing between expResult and result instances
print expResult.getCalibrationDate(), result.getCalibrationDate()
print expResult.getCountsPerUnitForce(), result.getCountsPerUnitForce()
print expResult.getCountsPerUnitTorque(), result.getCountsPerUnitTorque()
print expResult.getForceUnits(), result.getForceUnits()
print expResult.getPartNumber(), result.getPartNumber()
print expResult.getSerialNumber(), result.getSerialNumber()
print expResult.getTorqueUnits(), result.getTorqueUnits()