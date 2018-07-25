##hex_str = "AD4"
##hex_int = int(hex_str, 16)
##print hex(hex_int)
##new_int = hex_int + 0x200
##print hex(new_int)
##
##print("/n------------------------------------/n")
##
##LENGTH = 6
##packet = bytearray(LENGTH)
##packet[1] = 6
##packet[2] = 0
##packet[3] = 5
##CRC = 0x1234 # int = 4660 
##for i in range(0,LENGTH):
##    print hex(packet[i])
##print hex(CRC)
##
##print("/n------------------------------------/n")
##
##import functions
##
##short_byte = functions.int2bytes(4660,2)
##print hex(short_byte[0])
##print hex(short_byte[1])
##
##print("/n------------------------------------/n")
##
##short_byte = functions.int2bytes(3503,2)
##print hex(3503)
##print hex(short_byte[0])
##print hex(short_byte[1])
##
##print("/n------------------------------------/n")
##
##packet = bytearray(4)
##packet[0] = 0
##packet[1] = 6
##packet[2] = 0
##packet[3] = 5
##for i in range(0,4):
##    print hex(packet[i])
##import crc
##CRC = crc.crcBuf(packet,4)
### First loop crc = crcByte(0x1234,0), crc=0x1234 ch=0
##
##print("/n------------------------------------/n")
##
##import numpy as np
##udpPacketLength = 10
##udpPacketData = bytearray(udpPacketLength)
##for i in range(10): udpPacketData[i] = i
##sampleLength = 3
##for i in range(0, udpPacketLength, sampleLength):
##    singleRecord = udpPacketData[i:udpPacketLength] # Pick out next sample block
##    print(i)
##    for i in range(0,2):    
##        print hex(singleRecord[i])
##    print("")
       
##''' Calibration.py test. '''
##from Calibration import *
##
##calCommandResponse = '1 2 3 4\r\n5 6 7 8\r\n9 10 11 12\r\n13 14 15 16\r\n17 18 19 20\r\n21 22 23 24\r\n25 26 27 28\r\n29 30 31 32\r\n33 34 35 36\r\nSerial: 123\r\nDate:   345\r\nPart:   678\r\n4 5 6\r\nFx 1 2 3 4 5 6\r\nFy 1 2 3 4 5 6\r\nFz 1 2 3 4 5 6\r\nTx 1 2 3 4 5 6\r\nTy 1 2 3 4 5 6\r\nTz 1 2 3 4 5 6\r\n7 8 9\r\nForce: 123 counts/N\r\nTorque: 456 counts/Nm\r\n1 2 3\r\nThe MaxRatings are:\r\n1 2 3 4 5 6 7 8 9 10'
##print(calCommandResponse)
##cal = Calibration()
##cal.parseCalibrationFromTelnetResponse(calCommandResponse)

##''' Dictionary test. '''
##x = 'c'
##
##result = {
##    'a': 1,
##    'b': 2,
##    }.get(x, 9)
##
##print(result)

#''' Calibration.py test. '''
#from IPSettings import *
#
#ipCommandResponse = '1 2 3\r\nANTENNA Internal\r\n1 2 3\r\nBAND 5 GHz\r\n1 2 3\r\nNET DHCP false\r\nDEVIP 192.168.0.10  192.168.0.20\r\nGATEIP 192.168.0.1 192.168.0.2\r\nSSID loadcell matt-laptop\r\nNETMASK 255.255.255.0 255.255.255.0\r\n1 2 3'
#print(ipCommandResponse)
#ip = IPSettings()
#ip.IPSettings(ipCommandResponse)

#''' WirelessFTDemoModel.py test. '''
#import WirelessFTDemoModel
#model = WirelessFTDemoModel.WirelessFTDemoModel()

#''' Multithreading test 1. '''
#import threading
#import time
#
#exitFlag = 1
#
#class myThread (threading.Thread):
#   def __init__(self, threadID, name, counter):
#      threading.Thread.__init__(self)
#      self.threadID = threadID
#      self.name = name
#      self.counter = counter
#   def run(self):                               # Task that it does.
#      print "Starting " + self.name
#      print_time(self.name, self.counter, 2)
#      print "Exiting " + self.name
#
#def print_time(threadName, counter, delay):
#   while counter:
#      if exitFlag:
#         threadName.exit()
#      time.sleep(delay)
#      print "%s: %s" % (threadName, time.ctime(time.time()))
#      counter -= 1
#
## Create new threads
#thread1 = myThread(1, "Thread-1", 1)
#thread2 = myThread(2, "Thread-2", 5)
#
## Start new Threads
#thread1.start()
#thread2.start()
#
#print "Exiting Main Thread"

#''' Multithreading test 1. '''
#import threading
#from random import randint
#from time import sleep
#
#
#def print_number(number):
#    # Sleeps a random 1 to 10 seconds
#    rand_int_var = randint(1, 10)
#    sleep(rand_int_var)
#    print "Thread " + str(number) + " slept for " + str(rand_int_var) + " seconds"
#
#thread_list = []
#
#for i in range(1, 10):
#    # Instantiates the thread
#    # (i) does not make a sequence, so (i,)
#    t = threading.Thread(target=print_number, args=(i,))
#    # Sticks the thread in a list so that it remains accessible
#    thread_list.append(t)
#
## Starts threads
#for thread in thread_list:
#    thread.start()
#
## This blocks the calling thread until the thread whose join() method is called is terminated.
## From http://docs.python.org/2/library/threading.html#thread-objects
#for thread in thread_list:
#    thread.join()
#
## Demonstrates that the main process waited for threads to complete
#print "Done"

#''' My multithreading test. '''
#import threading
#import time
#
#class complete:
#    
#    def __init__(self):
#        return
#        
#    def done(self):
#        self.flagComplete = True
#
#class hello(complete):
#    
#    flagComplete = False
#
#    def __init__(self, text):
#        complete.__init__(self)
#        self.text = text
#        
#    def printing(self):
#        print('Hello world...' + self.text)
#        time.sleep(5)
#        print('Hello world2...' + self.text)
#        self.done()
#        
#    def run(self):
#        self.t = threading.Thread(target=self.printing)
#        self.t.start()            
#        
#    def wait(self):
#        self.t.join() # Waits for thread to finish.
#        
#        
#helloo = hello('Bob')
#helloo.run()
#print('Main thread done.')
##helloo.wait()
##print threading.active_count() # Shows the number of active threads.
##print threading.enumerate() # Lists the number of active threads.
##print threading.current_thread() # Shows the current thread.

#''' My multithreading test. '''
#import threading
#import time
#
#class hello:
#    
#    flagComplete = False
#
#    def __init__(self, text):
#        self.text = text
#        
#    def printing(self):
#        print('Hello world...' + self.text)
#        time.sleep(5)
#        print('Hello world2...' + self.text)
#        blah = self.complete(self)
#        blah.done()
#        
#    def run(self):
#        self.t = threading.Thread(target=self.printing)
#        self.t.start()            
#        
#    def wait(self):
#        self.t.join() # Waits for thread to finish.
#        
#    class complete:
#    
#        def __init__(self,outer):
#            self.outer = outer
#            
#        def done(self):
#            self.outer.flagComplete = True
#        
#        
#helloo = hello('Bob')
#helloo.run()
#print('Main thread done.')
##helloo.wait()
##print threading.active_count() # Shows the number of active threads.
##print threading.enumerate() # Lists the number of active threads.
##print threading.current_thread() # Shows the current thread.

#''' XML parsing test. '''
#from xml.etree import ElementTree
#with open('DefaultProfile.xml', 'rt') as f:
#    tree = ElementTree.parse(f)
#Tag  = []
#Text = []
#for node in tree.iter():
#    Tag.append(node.tag)
#    Text.append(node.text)
#    #print node.tag, node.text # , node.tail, node.attrib
#rate_index = Tag.index('rate')
#rate = Text[rate_index]
##print rate
#for i in range(0, len(Tag)):
#    print i, Tag[i], Text[i]
#    
#print '----------'
#
#general = tree.find('general')
#for i in general:
#    print i.text
#    
#print '----------'
#    
#transducers = tree.find('general/transducers')
#for i in transducers:
#    print i.text
#    
#print '----------'
#    
#filters = tree.find('filters')
#for i in filters:
#    print i.text
#    
#print '----------'
#
#trans = tree.find('filters')
#for i in range(0, 6):
#    print trans[i][0].text, trans[i][1].text
#    
#print '----------'
#    
#calibration = tree.find('calibration')
#for i in calibration:
#    print i.text
#
#print '----------'
#
#m_xforms = [[[],[]]]
#transformation = tree.find('transformation')
#for i in range(0, 6):
#    trans = transformation[i]
#    disp = trans.find('displacement')
#    if i>0:
#        m_xforms.append([[],[]])
#    for j in range(0, 4):
#        m_xforms[i][0].append(disp[j].text)
#    rot = trans.find('rotation')
#    for j in range(0, 4):
#        m_xforms[i][1].append(rot[j].text)
#        
#DEFAULT_RATE                    = '125'
#DEFAULT_OVERSAMPLING            = '32'
#DEFAULT_SD                      = 'OFF'
#DEFAULT_FORCE_UNITS             = 'Default'
#DEFAULT_TORQUE_UNITS            = 'Default'
#DEFAULT_FILTER_TYPE             = 'Running Mean'
#DEFAULT_FILTER_VALUE            = '8'
#DEFAULT_DISPLACEMENT_UNITS      = 'm'
#DEFAULT_ROTATION_UNITS          = 'Degrees'
#
#DEFAULT_XPWR    = ['ON', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF']
#
#DEFAULT_FILTERS = [[DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
#                   [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
#                   [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
#                   [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
#                   [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE],
#                   [DEFAULT_FILTER_TYPE, DEFAULT_FILTER_VALUE]]
#                   
#DEFAULT_CALS = ['0', '0', '0', '0', '0', '0'] # Calibration defaults = "Default"
#
#DEFAULT_XFORMS = [[[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
#                  [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
#                  [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
#                  [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
#                  [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]],
#                  [[DEFAULT_DISPLACEMENT_UNITS, "0.0","0.0","0.0"], [DEFAULT_ROTATION_UNITS, "0.0","0.0","0.0"]]]
#                  
#NUM_SENSORS = 6
#
##UNITS_AND_VALUES = 4
##transformation = tree.find('transformation') # Transformations for each transducer
##for i in range(0, NUM_SENSORS):
##    trans = transformation[i]
##    disp = trans.find('displacement')
##    for j in range(0, UNITS_AND_VALUES):
##        m_xforms[i][0][j] = disp[j].text
#
#m_xforms = DEFAULT_XFORMS
#
##x='c'
##result = {
##            'a': 1,
##            'b': 2,
##            }.get(x, 9) # 9 is default if x not found
#
#transducer = 1
#xforms = ''
#
#for i in range(1, len(m_xforms[transducer][0])):
#    xforms += m_xforms[transducer][0][i] + '|'
#    print xforms
#
#print xforms[0 : len(xforms)-1] # Remove trailing |

import WirelessFTSensorSampleCommand
instance = WirelessFTSensorSampleCommand.WirelessFTSensorSampleCommand()
instance.sendStartStreamingCommand()