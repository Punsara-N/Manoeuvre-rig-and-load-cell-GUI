import datetime
import socket
import struct
import time
import Queue
import threading
import select
import win32serviceutil
import admin


def system_to_ntp_time(timestamp):
    """Convert a system time to a NTP time.

    Parameters:
    timestamp -- timestamp in system time

    Returns:
    corresponding NTP time
    """
    return timestamp + NTP.NTP_DELTA

def _to_int(timestamp):
    """Return the integral part of a timestamp.

    Parameters:
    timestamp -- NTP timestamp

    Retuns:
    integral part
    """
    return int(timestamp)

def _to_frac(timestamp, n=32):
    """Return the fractional part of a timestamp.

    Parameters:
    timestamp -- NTP timestamp
    n         -- number of bits of the fractional part

    Retuns:
    fractional part
    """
    return int(abs(timestamp - _to_int(timestamp)) * 2**n)

def _to_time(integ, frac, n=32):
    """Return a timestamp from an integral and fractional part.

    Parameters:
    integ -- integral part
    frac  -- fractional part
    n     -- number of bits of the fractional part

    Retuns:
    timestamp
    """
    return integ + float(frac)/2**n


class NTPException(Exception):
    """Exception raised by this module."""
    pass


class NTP:
    """Helper class defining constants."""

    _SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
    """system epoch"""
    _NTP_EPOCH = datetime.date(1900, 1, 1)
    """NTP epoch"""
    NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600
    """delta between system and NTP time (in seconds)"""

    REF_ID_TABLE = {
            'DNC': "DNC routing protocol",
            'NIST': "NIST public modem",
            'TSP': "TSP time protocol",
            'DTS': "Digital Time Service",
            'ATOM': "Atomic clock (calibrated)",
            'VLF': "VLF radio (OMEGA, etc)",
            'callsign': "Generic radio",
            'LORC': "LORAN-C radionavidation",
            'GOES': "GOES UHF environment satellite",
            'GPS': "GPS UHF satellite positioning",
    }
    """reference identifier table"""

    STRATUM_TABLE = {
        0: "unspecified",
        1: "primary reference",
    }
    """stratum table"""

    MODE_TABLE = {
        0: "unspecified",
        1: "symmetric active",
        2: "symmetric passive",
        3: "client",
        4: "server",
        5: "broadcast",
        6: "reserved for NTP control messages",
        7: "reserved for private use",
    }
    """mode table"""

    LEAP_TABLE = {
        0: "no warning",
        1: "last minute has 61 seconds",
        2: "last minute has 59 seconds",
        3: "alarm condition (clock not synchronized)",
    }
    """leap indicator table"""

class NTPPacket:
    """NTP packet class.

    This represents an NTP packet.
    """
    
    _PACKET_FORMAT = "!B B B b 11I"
    """packet format to pack/unpack"""

    def __init__(self, version=2, mode=3, tx_timestamp=0, printFlag=False):
        
        self.printFlag = printFlag
        """Constructor.

        Parameters:
        version      -- NTP version
        mode         -- packet mode (client, server)
        tx_timestamp -- packet transmit timestamp
        """
        self.leap = 0
        """leap second indicator"""
        self.version = version
        """version"""
        self.mode = mode
        """mode"""
        self.stratum = 0
        """stratum"""
        self.poll = 0
        """poll interval"""
        self.precision = 0
        """precision"""
        self.root_delay = 0
        """root delay"""
        self.root_dispersion = 0
        """root dispersion"""
        self.ref_id = 0
        """reference clock identifier"""
        self.ref_timestamp = 0
        """reference timestamp"""
        self.orig_timestamp = 0
        self.orig_timestamp_high = 0
        self.orig_timestamp_low = 0
        """originate timestamp"""
        self.recv_timestamp = 0
        """receive timestamp"""
        self.tx_timestamp = tx_timestamp
        self.tx_timestamp_high = 0
        self.tx_timestamp_low = 0
        """tansmit timestamp"""
        
    def to_data(self):
        """Convert this NTPPacket to a buffer that can be sent over a socket.

        Returns:
        buffer representing this packet

        Raises:
        NTPException -- in case of invalid field
        """
        try:
            packed = struct.pack(NTPPacket._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode),
                self.stratum,
                self.poll,
                self.precision,
                _to_int(self.root_delay) << 16 | _to_frac(self.root_delay, 16),
                _to_int(self.root_dispersion) << 16 |
                _to_frac(self.root_dispersion, 16),
                self.ref_id,
                _to_int(self.ref_timestamp),
                _to_frac(self.ref_timestamp),
                #Change by lichen, avoid loss of precision
                self.orig_timestamp_high,
                self.orig_timestamp_low,
                _to_int(self.recv_timestamp),
                _to_frac(self.recv_timestamp),
                _to_int(self.tx_timestamp),
                _to_frac(self.tx_timestamp))
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")
        return packed

    def from_data(self, data):
        """Populate this instance from a NTP packet payload received from
        the network.

        Parameters:
        data -- buffer payload

        Raises:
        NTPException -- in case of invalid packet format
        """
        try:
            unpacked = struct.unpack(NTPPacket._PACKET_FORMAT,
                    data[0:struct.calcsize(NTPPacket._PACKET_FORMAT)])
        except struct.error:
            raise NTPException("Invalid NTP packet.")

        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]
        self.ref_timestamp = _to_time(unpacked[7], unpacked[8])
        self.orig_timestamp = _to_time(unpacked[9], unpacked[10])
        self.orig_timestamp_high = unpacked[9]
        self.orig_timestamp_low = unpacked[10]
        self.recv_timestamp = _to_time(unpacked[11], unpacked[12])
        self.tx_timestamp = _to_time(unpacked[13], unpacked[14])
        self.tx_timestamp_high = unpacked[13]
        self.tx_timestamp_low = unpacked[14]
        
        if self.printFlag == True:
            print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
            print 'Packet received from client:'
            print 'Leap: ' + str(self.leap)
            print 'Version: ' + str(self.version)
            print 'Mode: ' + str(self.mode)
            print 'Stratum: ' + str(self.stratum)
            print 'Poll: ' + str(self.poll)
            print 'Precision: ' + str(self.precision)
            print 'Root delay: ' + str(self.root_delay)
            print 'Root dispersion: ' + str(self.root_dispersion)
            print 'Ref ID: ' + str(self.ref_id)
            print 'Ref timestamp: ' + str(self.ref_timestamp)
            print 'Original timestamp: ' + str(self.orig_timestamp)
            print 'Recv timestamp: ' + str(self.recv_timestamp)
            print 'Tx timestamp: ' + str(self.tx_timestamp)
            print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        

    def GetTxTimeStamp(self):
        return (self.tx_timestamp_high,self.tx_timestamp_low)

    def SetOriginTimeStamp(self,high,low):
        self.orig_timestamp_high = high
        self.orig_timestamp_low = low
        

class RecvThread(threading.Thread):
    def __init__(self,socket,queue,GUI, printFlag):
        self.printFlag = printFlag
        threading.Thread.__init__(self)
        self.socket = socket
        self.stopFlag = False
        self.taskQueue = queue
        self.requestsReceived = 0
        self.GUI = GUI
    def run(self):
        while True:
            if self.stopFlag == True:
                if self.printFlag:
                    print "RecvThread Ended"
                break
            rlist,wlist,elist = select.select([self.socket],[],[],1);
            if len(rlist) != 0:
                '''
                print "Received %d packets" % len(rlist)
                '''
                for tempSocket in rlist:
                    try:
                        data,addr = tempSocket.recvfrom(1024)
                        recvTimestamp = system_to_ntp_time(time.time())
                        self.taskQueue.put((data,addr,recvTimestamp))
                        self.requestsReceived += 1
                        try:
                            self.GUI.textNoSycRequestReceived.SetLabel(str(self.requestsReceived))
                        except:
                            pass
                    except socket.error,msg:
                        print msg;

class WorkThread(threading.Thread):
    def __init__(self,socket,queue, printFlag):  
        self.printFlag = printFlag      
        threading.Thread.__init__(self)
        self.socket = socket
        self.stopFlag = False
        self.taskQueue = queue
    def run(self):
        while True:
            if self.stopFlag == True:
                if self.printFlag:
                    print "WorkThread Ended"
                break
            try:
                data,addr,recvTimestamp = self.taskQueue.get(timeout=1)
                recvPacket = NTPPacket(printFlag=False)
                recvPacket.from_data(data)
                timeStamp_high,timeStamp_low = recvPacket.GetTxTimeStamp()
                sendPacket = NTPPacket(version=4,mode=4,printFlag=False)
                sendPacket.stratum = 1
                sendPacket.poll = 10
                sendPacket.precision = -20 #0xfa
                sendPacket.root_delay = 0 #0x0bfa
                sendPacket.root_dispersion = 0 #0x0aa7
                sendPacket.ref_id = 0xC0A8BF05#192.168.191.5 #0x808a8c2c
                sendPacket.ref_timestamp = recvTimestamp # recvTimestamp is the time the server received the request from the client
                sendPacket.orig_timestamp = recvPacket.tx_timestamp
                sendPacket.SetOriginTimeStamp(timeStamp_high,timeStamp_low) # Takes tx_timestamp_high and tx_timestamp_low from packet received from client and puts in into orig_timestamp_high and orig_timestamp_low into sending packet from server.
                sendPacket.recv_timestamp = recvTimestamp
                sendPacket.tx_timestamp = system_to_ntp_time(time.time()) # Time right now
                self.socket.sendto(sendPacket.to_data(),addr)
                
                if self.printFlag:
                    print "Sent to %s:%d" % (addr[0],addr[1])
                    
                    print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                    print 'Packet sent to client:'
                    print 'Leap: ' + str(sendPacket.leap)
                    print 'Version: ' + str(sendPacket.version)
                    print 'Mode: ' + str(sendPacket.mode)
                    print 'Stratum: ' + str(sendPacket.stratum)
                    print 'Poll: ' + str(sendPacket.poll)
                    print 'Precision: ' + str(sendPacket.precision)
                    print 'Root delay: ' + str(sendPacket.root_delay)
                    print 'Root dispersion: ' + str(sendPacket.root_dispersion)
                    print 'Ref ID: ' + str(sendPacket.ref_id)
                    print 'Ref timestamp: %.5f' %(sendPacket.ref_timestamp)
                    print 'Original timestamp: %.5f' %(sendPacket.orig_timestamp)
                    print 'Recv timestamp: %.5f' %(sendPacket.recv_timestamp)
                    print 'Tx timestamp: %.5f' %(sendPacket.tx_timestamp)
                    print 'Delay (s): %.6f (recv - original timestamp)' %(sendPacket.recv_timestamp - sendPacket.orig_timestamp)
                    print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                
        
            except Queue.Empty:
                continue
              

class NTPServer():
    
    def __init__(self, GUI, serverIP, printFlag=False):
        
        self.printFlag = printFlag
        
        self.taskQueue = Queue.Queue()
        
        try:
            win32serviceutil.StopService('W32Time') # Stops windows time service
        except Exception as error:
            if self.printFlag:
                print error
                print "Note: Make sure W32Time service is stopped to ensure NTP port is accessible"
        print "Starting NTP server..."
        print "Server IP: " + serverIP
        
        host = serverIP#'192.168.1.65'#'192.168.191.5'
        port = 'ntp' # To check if port is in use, try cmd: netstat -ano|findstr 123
        
        #print socket.getaddrinfo(host, port)
        addrInfo = socket.getaddrinfo(host, port)[0] # (23, 2, 0, '', ('::1', 123, 0, 0))
        family = addrInfo[0]
        typee = addrInfo[1]
        proto = addrInfo[2]
        addr = addrInfo[4]
        
        try:
            socNTP = socket.socket(family, typee, proto)
            socNTP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # This allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state for several minutes, waiting for late packets to arrive.
            socNTP.bind(addr)
        except Exception as error:
            print error
            print "Make sure W32Time service is stopped (services can be stopped via task manager)."
        
        if self.printFlag:            
            print "local socket: ", socNTP.getsockname();
            print "Active threads:" + str(threading.active_count())
        self.recvThread = RecvThread(socNTP, self.taskQueue, GUI, self.printFlag)
        self.recvThread.daemon = True
        self.recvThread.start()
        if self.printFlag:
            print "Active threads:" + str(threading.active_count())
        self.workThread = WorkThread(socNTP, self.taskQueue, self.printFlag)
        self.workThread.daemon = True
        self.workThread.start()
        if self.printFlag:
            print "Active threads:" + str(threading.active_count())
        
        if self.printFlag:
            print "NTP server started!"
        
        
    def stopServer(self):
        
        print "Stopping NTP server..."
        self.recvThread.stopFlag = True
        self.workThread.stopFlag = True
        #time.sleep(1)
        #self.recvThread.join()
        #self.workThread.join()
        try:
            win32serviceutil.StartService('W32Time')
        except Exception as error:
            if self.printFlag:
                print error
        
        if self.printFlag:    
            print 'Emptying Queue...'
        while not self.taskQueue.empty():
            if self.printFlag:
                print 'Emptying...'
            self.taskQueue.get()
        if self.printFlag:
            print 'Queue empty? ' +  str(self.taskQueue.empty())
        if self.printFlag:
            print 'Emptied!' 
            
        print "Stopped"
            
            
if __name__ == '__main__':

    server = NTPServer(None, '192.168.191.5', printFlag = True)
    while True:
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                print "Exiting..."
                server.stopServer()
                print "Exited"
                break
        
