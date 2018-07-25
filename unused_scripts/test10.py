import time
import struct

# wnetTime, sysTime, and years70 are all type long
years70 = (70 * 365 + 17) * 24 * 60 * 60 # 70 years (in seconds)
years70 = struct.unpack('l', struct.pack('L', years70))[0] # Making the value signed so it behaves the same as in java.
#wnetTime  = long(self.m_timeStamp) # Wnet's number of seconds since 1/1/1900 00:00 NTP (format 20.12)
sysTime   = time.time()*1000 # JAVA: System.currentTimeMillis() # System's number of milliseconds since 1/1/1970 00:00 UTC (format 64.0)
sysTime   = sysTime + (years70 * 1000) # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
#sysTime   = (sysTime << 12)   / 1000 # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)
#self.m_latency = int(sysTime - wnetTime) & 0xffffffff # Calculate modulo 32-bits latency (20.12)
#self.m_latency = (self.m_latency * 1000) >> 12 # Convert to mS (32.0)

#print sysTime
#print years70

''' Need sysTime from 1900. '''
# wnetTime, sysTime, and years70 are all type long
years70 = (70 * 365 + 17) * 24 * 60 * 60 # 70 years (in seconds)
#years70 = struct.unpack('l', struct.pack('L', years70))[0] # Making the value signed so it behaves the same as in java.
#wnetTime  = long(self.m_timeStamp) # Wnet's number of seconds since 1/1/1900 00:00 NTP (format 20.12)
sysTime   = time.time() # In seconds.
sysTime   = sysTime + (years70) # Convert to number of milliseconds since 1/1/1900 00:00 (add 70 years)
#sysTime   = (sysTime << 12)   / 1000 # Convert to number of seconds since 1/1/1900 00:00 NTP (format 20.12)
#self.m_latency = int(sysTime - wnetTime) & 0xffffffff # Calculate modulo 32-bits latency (20.12)
#self.m_latency = (self.m_latency * 1000) >> 12 # Convert to mS (32.0)

sysTime_int = int(sysTime)
sysTime_blah = struct.unpack('L',struct.pack('L',sysTime_int))[0]
sysTime_blah_bin = bin(sysTime_blah)[2:]
sysTime_blah_bin2 = sysTime_blah_bin[20:]

print sysTime_blah_bin
print sysTime_blah_bin2
print int(sysTime_blah_bin2,2)

sysTime_blah_blah = sysTime_blah << 12
sysTime_blah_blah2 = sysTime_blah_bin[12:] + '000000000000'

