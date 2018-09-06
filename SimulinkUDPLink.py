'''
Creates UDP socket to send data to Simulink.

Created on Aug 30, 2018

@author: PD Banneheka
'''

import socket
import struct
import Queue
import threading

class SimulinkSocket(object):
    
    def __init__(self, parent):

        self.host = '127.0.0.1'
        self.port = 25000 # To check if port is in use, try cmd: netstat -ano|findstr 123
        self.addr = (self.host, self.port)
        
        print "Starting Simulink socket: (%s, %i)" %(self.host, self.port)

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # This allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state for several minutes, waiting for late packets to arrive.

        self.queue = Queue.Queue()
        
        self.active = True
        
        # Load conversion factors
        self.forceCF      = 1e-6
        self.torqueCF     = 1e-6
        
        self.process = threading.Thread(target=self.mainLoop)
        self.process.daemon = True
        self.process.start()
        
    def addToQueue(self, parent, item):
        
        loads = [0,0,0,0,0,0]
        
        for transducer in range(0, parent.WirelessFTDemoModel.WirelessFTDemoModel.MAX_SENSORS): # For each Transducer,
            if parent.m_model.m_sensorActive[transducer]: # If this Transducer is active,
                # Note: 's.getFtOrGageData()[transducer]' is a row vector, need to convert to a column for matrix multiplication.
                getFtOrGageData = []
                for v in item.getFtOrGageData()[transducer]:
                    getFtOrGageData.append([v])
                data = parent.matrixMult(parent.m_profile.getTransformationMatrix(transducer), getFtOrGageData)
                for axis in range(0, parent.WirelessFTDemoModel.WirelessFTDemoModel.NUM_AXES): # For each channel,
                    value = data[axis][0] # get the data value.
                    # Multiplying reading my conversion factor
                    if axis < 3:
                        loads[axis] = value * self.forceCF
                    else:
                        loads[axis] = value * self.torqueCF
                time = item.getTimeStamp()
                
                data = loads
                data.append(time)
        
        self.queue.put_nowait(data)

    def sendData(self, data):
        
        self.tx_pack = struct.Struct("<7d") # little-endian 6 doubles
        self.data = self.tx_pack.pack(data[0],data[1],data[2],data[3],data[4],data[5],data[6])
        self.soc.sendto(self.data, self.addr)
        
    def mainLoop(self):
        
        while self.active:
        
            while not self.queue.empty():
                
                data = self.queue.get()
                self.sendData(data)
                
    def stop(self):
        
        print "Stopping..."
        self.active = False
        print "Emptying queue..."
        while not self.queue.empty(): # Empyties queue
            self.queue.get()
        print "Joining process"
        self.process.join()
        print "Done"


if __name__ == '__main__':
    
    a = 123.123
    b = -456.456
    c = -789.789
    
    data = [a,b,c,a,b,c]
    
    print "Sending data to Simulink:"
    print data
    
    simulinkLink = SimulinkSocket()
    simulinkLink.addToQueue(data)
    simulinkLink.stop()