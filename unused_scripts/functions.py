def TestFunction1(num,DebugFlag):
    print ("Test function 1 running...")
    if DebugFlag:
        print (num)
    return

def DebugMode(var):
    if var == True:
        DebugFlag = True
        print ("Debug mode active.")
    elif var == False:
        DebugFlag = False
        print ("Debug mode not active.")
    else:
        print ("Debug mode not detected!")
    return DebugFlag

## FUNCTION BELOW IS RETIRED, USE FUNCTION int2bytes INSTEAD
def int2shortbytes(var): # Input var is an integer, returns 2 bytes
    short_byte = bytearray(2)
    if var<=255: # For int that require only one byte
        short_byte[0] = 0
        short_byte[1] = var
    else: # For int that require two bytes
        var_hex_string = hex(var)[2:] # The integer variable as a hex string.
        if len(var_hex_string)<4: # If the hex string has only three characters, like "0xdaf"
            var_hex_string_byte_1 = '0' + var_hex_string[0] # First byte as a hex string.
            var_hex_string_byte_2 = var_hex_string[1:3]     # Second byte as a hex string.
        else: # If the hex string has four characters
            var_hex_string_byte_1 = var_hex_string[0:2] # First byte as a hex string.
            var_hex_string_byte_2 = var_hex_string[2:4] # Second byte as a hex string.
        var_int_byte_1 = int(var_hex_string_byte_1, 16) # First byte as an integer.
        var_int_byte_2 = int(var_hex_string_byte_2, 16) # Second byte as an integer.
        short_byte[0] = var_int_byte_1
        short_byte[1] = var_int_byte_2
    return short_byte

## Input integer var and the number of bytes that that the var will be represented in.
## short: numbytes = 2
## int  : numbytes = 4 (for a 32 bit system)
## Function will return the integer in a bytearray.
def int2bytes(var,numbytes): 
    int_byte = bytearray(numbytes)
    numhexchar = numbytes*2 # Number of hex characters required in string.
    var_hex_string = hex(var)[2:] # The integer variable as a hex string.
    if len(var_hex_string)<numhexchar: # If the length of the hex string is lower than number of characters required
        zeropadding = numhexchar-len(var_hex_string) # Number of zeros to be padded in from of string
        for i in range(0,zeropadding):
            var_hex_string = '0' + var_hex_string
    #print(var_hex_string)
    for i in range(0,numbytes):
        int_byte[i] = int(var_hex_string[(i*2):(i*2+2)], 16)
        
    return int_byte

## Use module 'struct' and struct.unpack("<L", var)[0] instead of function below
## Input byte or any length, outputs integer num.
def bytes2int(var):
    length = len(var) # Length of bytes.
    hex_string_all = ""
    for i in range(0, length):
        hex_string = hex(var[i])[2:] # Each byte as a hex string.
        print(hex_string)
        hex_string_all = hex_string_all + hex_string # Total hex string.
    num = int(hex_string_all, 16) # Converting entire hex string to an integer
    return num
