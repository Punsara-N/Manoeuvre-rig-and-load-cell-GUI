"""
This file contains the tests using in WirelessFTSensorTest.java. 
"""



import WirelessFTDemoModel
import WirelessFTSensor

## Test of getSensorAddress method, of class WirelessFTSensor.
#print('')
#print('getSensorAddress')
#instance = WirelessFTSensor.WirelessFTSensor()
#expResult = '' # Should default to an empty string.
#result = instance.getSensorAddress()
#print('expResult=' + expResult + ' result=' + result)
#expResult = 'localhost'
#try:
#    instance.setSensorAddress(expResult)
#except Exception as e:
#    print('Exception setting sensor address: ' + e)
#result = instance.getSensorAddress()
#print('expResult=' + expResult + ' result=' + result)
#instance.endCommunication()
#
## Test of setSensorAddress method, of class WirelessFTSensor.
#print('')
#print('setSensorAddress')
#val = 'this.is.not.a.valid.address.and.if.it.is.your.network.admin.is.crazy'
#instance = WirelessFTSensor.WirelessFTSensor()
#try:
#    instance.setSensorAddress(val)
#except Exception as e:
#    print(e)
#val = 'localhost'
#instance.setSensorAddress(val)
#print val, instance.getSensorAddress()

## Test of readStreamingSample method, of class WirelessFTSensor.
#print('')
#print('readStreamingSample')
#instance = WirelessFTSensor.WirelessFTSensor()
#instance.setSensorAddress('localhost')
#try:
#    print('Reading UDP...')
#    i = 0
#    while i<=10:
#        result = instance.readStreamingSample()
#        print 'Latency:', instance.WirelessFTSample.getLatency()
#        if i>10:
#            break
#        i += 1
#        
#    print('Reading done.')
#except Exception as e:
#    print('Could not read UDP.')
#    print e
#    instance.m_udpSocket.shutdown(1)
#    instance.m_udpSocket.close()
#
#instance.endCommunication()

print('')
print('readTelnetData')
instance = WirelessFTSensor.WirelessFTSensor()
instance.setSensorAddress("localhost")
expectedVal = "hello\r\n"
instance.m_telnetSocket.write(expectedVal)
result = instance.readTelnetData(False) # Should get 'Wrong message received.'
result = instance.readTelnetData(True)  # Should get 'Wrong message received with blocking.'
result = instance.readTelnetData(False) # Should get 'Didn't get empty value when not blocking and no input data'.