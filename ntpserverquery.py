import ntplib
from time import ctime

c = ntplib.NTPClient()
print 'Requesting...'
#response = c.request('europe.pool.ntp.org', version=3)
response = c.request('192.168.1.65', version=3) #c.request('localhost', version=3) 192.168.1.65



print response.version
print ctime(response.tx_time)
print ntplib.leap_to_text(response.leap)
print response.root_delay
print ntplib.ref_id_to_text(response.ref_id)