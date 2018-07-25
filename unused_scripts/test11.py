''' Converting binary with binary point to a decimal. '''

a = 0110110

print a

# 0110.110 (4 bit integer, 3 bit fraction)
def parse_bin(s):
    t = s.split('.')
    print t
    return int(t[0], 2) + int(t[1], 2) / 2.**len(t[1])
    
print parse_bin('0110.110')