'''
Custom logging class

Punsara Navaratna 13-Aug-2018
'''
import sys
from cStringIO import StringIO
import time
import datetime

class log():
        
    def __init__(self, GUI):
        
        self.parentGUI = GUI
        self.fullLog = ''
        
        self.old_stdout = sys.stdout
        sys.stdout = self
    
    def write(self, text): 
        
        '''
        self.stringInputOutput = StringIO()
        self.stringInputOutput.write(text)
        self.stringText = self.stringInputOutput.getvalue()
        '''
        if text != '\n':
            self.stringText = text
            timestamp = time.time()
            timestampString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
            self.fullText = "\n" + timestampString[0:23]+ ": " + self.stringText
            #self.controlTextLog.write("\n" + timestampString[0:23]+ ": " + self.stringText)
            self.addToFullLog(self.fullText)
        
    def addToFullLog(self, text):
        
        self.fullLog += text
        
    def close(self):
        
        sys.stdout = self.old_stdout
        

if __name__ == '__main__':
    
    GUI = None
    myLog = log(GUI)
    print 'Hello world'
    
    try:
        a = 1/0
    except Exception as error:
        print error

    print 'Hello world123'
    print 'Hello world123456'
    print 'Hello world123456789'
    myLog.close()
    txt = myLog.fullLog
    print txt