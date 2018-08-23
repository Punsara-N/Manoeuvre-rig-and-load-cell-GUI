import time
import struct
import ctypes
import numpy
import sys
import datetime

def int_overflow(val):
    maxint = 0x7FFFFFFF
    if not -maxint-1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val

'''
years70 = long((70 * 365 + 17) * 24 * 60 * 60) #& 0xffffffff
years70 = int_overflow(years70)
print years70
#years70 = struct.unpack('l', struct.pack('L', years70))[0]
m_timeStamp = 2078044892
wnetTime  = m_timeStamp
sysTime = long(1534860805430)
sysTime = int_overflow(sysTime)
print sysTime
#sysTime   = System.currentTimeMillis() #System's   number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
sysTime1   = sysTime + years70 * 1000 #Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
print (sysTime1)
print numpy.binary_repr(numpy.uint64(sysTime1))
sysTime2   = numpy.uint64(sysTime1 << 12 ) #/ 1000)   #Convert to number of      seconds since 1/1/1900 00:00 NTP (format 20.12)
print (sysTime2)
print numpy.binary_repr(sysTime2)

diff = (sysTime2 - wnetTime)*0
#diff = numpy.int32( numpy.uint32(diff) ) # struct.unpack('i', struct.pack('I', diff))[0]
diff_binary = numpy.uint32( diff )
print diff
print numpy.binary_repr(diff_binary)
m_latency = numpy.int32(diff_binary & 0xffffffff) #Calculate modulo 32-bits latency (20.12)
#print "{0:b}".format(m_latency)
#m_latency = struct.unpack('i', struct.pack('I', m_latency))[0]
#print "{0:b}".format(m_latency)

if m_latency < 0:
    m_latency2 = ((numpy.uint32(m_latency * 1000)) >> 12) | 0xFFF00000#Convert to mS (32.0)
else:
    m_latency2 = ((numpy.uint32(m_latency * 1000)) >> 12)
print numpy.binary_repr(m_latency2)
m_latency2 = numpy.int32(m_latency2)




#m_latency2 = struct.unpack('i', struct.pack('I', m_latency2))[0]
#print "{0:b}".format(m_latency2)

#print years70
#print sysTime1
#print sysTime2
#print m_latency
print m_latency2

1111111111111111111111100001101010101110110100110110100100110110
1111111111100001101010101110110100110110100100110110000000000000

2,208,988,800

n = numpy.uint64(-5)
print numpy.binary_repr(n)

print '.................'
years70 = ((70 * 365 + 17) * 24 * 60 * 60) & 0xFFFFFFFF# 2,208,988,800
print '{0:b}'.format(years70)
m_timeStamp = 2078044892 & 0xFFFFFFFF
print 'wnetTime', '{0:b}'.format(m_timeStamp)
wnetTime  = m_timeStamp
sysTime = 1534860805430 & 0xFFFFFFFF
print 'sysTime', '{0:b}'.format(sysTime)
sysTime1   = (sysTime + years70 * 1000) & 0xFFFFFFFF #Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
print '{0:b}'.format(sysTime1)
sysTime2 = (((sysTime1 << 12) & 0xFFFFFFFF) / 1000) & 0xFFFFFFFF
print '{0:b}'.format(sysTime1)
print '{0:b}'.format((sysTime1 << 12) & 0xFFFFFFFF)
m_latency = (sysTime2 - wnetTime) & 0xFFFFFFFF
m_latency2 = (((m_latency*1000) & 0xFFFFFFFF) >> 12) & 0xFFFFFFFF
print m_latency2
'''
'''
print "##################"
years70 = (((70 * 365) + 17) * 24 * 60 * 60) & 0xFFFFFFFF # 70 years (in seconds)
wnetTime = 2078044892 & 0xFFFFFFFF # Wnet's number of seconds since 1/1/1900 00:00 NTP (format 20.12) (unsigned long)
sysTime   = 1534860805430 & 0xFFFFFFFF # JAVA: System.currentTimeMillis() # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
sysTime   = (sysTime + (years70 * 1000)) & 0xFFFFFFFF # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
sysTime   = (((sysTime << 12) & 0xFFFFFFFF) / 1000)  & 0xFFFFFFFF # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)
m_latency = (sysTime - wnetTime) & 0xFFFFFFFF # Calculate modulo 32-bits latency (20.12)
if m_latency > 0x7FFFFFFF:
    m_latency -= 0xFFFFFFFF
print m_latency
print '{0:b}'.format(m_latency)
m_latency = (m_latency * 1000) & 0xFFFFFFFF
if m_latency > 0x7FFFFFFF:
    m_latency -= 0xFFFFFFFF
m_latency = (m_latency >> 12) & 0xFFFFFFFF# Convert to mS (32.0)
if m_latency > 0x7FFFFFFF:
    m_latency -= 0xFFFFFFFF
print m_latency
print '{0:b}'.format(m_latency) # 1111 1111 1111 1110 0111

m_timeStampms = wnetTime & 0xFFFFFFFF
m_timeStampms = (m_timeStampms * 1000) & 0xFFFFFFFF
m_timeStampms = (m_timeStampms >> 12) & 0xFFFFFFFF
sysTime = ((1534860805430 & 0xFFFFFFFF) + (years70 * 1000)) & 0xFFFFFFFF
lat = (sysTime - m_timeStampms) & 0xFFFFFFFF
print lat 
'''

# TEST TIMESTAMP ############################
# Making current system time a test loadcell timestamp
years70 = ((70 * 365) + 17) * 24 * 60 * 60 # 70 years (in seconds)
secondsSinceStartOfTodayToNow = time.time() % (24*60*60)
secondsSinceStartOfWNetClockToStartOfDay = time.time() - secondsSinceStartOfTodayToNow + years70
A = secondsSinceStartOfWNetClockToStartOfDay % 2**20 # seconds from start of last rollover before midnight to midnight
startOfRollover = secondsSinceStartOfWNetClockToStartOfDay - years70 - A # seconds
timestamp = int((time.time() - startOfRollover) * 2**12)
print timestamp
#############################################

# Convert timestamp to unsigned 32bit
m_timeStamp = timestamp#2078044892
wnetTime  = float(m_timeStamp)
if wnetTime >= 0:
    pass
else:
    wnetTime += 2**32

# Find when last rollover started, the loadcell clock rests ever 2^20 seconds, clock started at midnight January 1, 1900 (70 years before Epoch (midnight January 1, 1970))
#testTime = (datetime.datetime(2018,8,21,15,13,25) - datetime.datetime(1970,1,1)).total_seconds()
#testTime = 1534860805430/1000 + 60*60
#testTimeTodayStart = (datetime.datetime(2018,8,21,0,0) - datetime.datetime(1970,1,1)).total_seconds()
years70 = ((70 * 365) + 17) * 24 * 60 * 60 # 70 years (in seconds)
secondsSinceStartOfTodayToNow = time.time() % (24*60*60)
secondsSinceStartOfWNetClockToStartOfDay = time.time() - secondsSinceStartOfTodayToNow + years70
A = secondsSinceStartOfWNetClockToStartOfDay % 2**20 # seconds from start of last rollover before midnight to midnight
B = wnetTime/(2**12) # Received timestamp, in seconds

# Check if clock rolled over after midnight that day (before the packet was received), and correct date/time of start of last rollover accordingly
# Note startOfRollOver is relative to epoch, in seconds
if A > B:
    startOfRollover = secondsSinceStartOfWNetClockToStartOfDay - years70 - A + 2**20 # Rollover happened after midnight before packet was received
else:
    startOfRollover = secondsSinceStartOfWNetClockToStartOfDay - years70 - A

# So packet date/time = timestamp on packet + date/time of start of last rollover
packetTime = startOfRollover + wnetTime/(2**12) # packet time since Epoch, in seconds

print 'Wnet time: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(packetTime))

