'''
Custom loggging class (print will add to logg)

Punsara Navaratna 13-Aug-2018
'''
import sys
import time
import datetime
import threading
import os

class _myLog(object):
        
    def __init__(self, GUI=None):
        
        self.GUI = GUI
        self.fullLog = ''
        self.old_stdout = sys.stdout
        sys.stdout = self # This makes "write" function below to be called whenever "print" command is used
    
  
    def write(self, text): 
        
        if text != '\n':
            self.stringText = text
            timestamp = time.time()
            timestampString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
            self.fullText = "\n" + timestampString[0:23]+ ": " + self.stringText
            self.addToFullLog(self.fullText)
            self.GUIAction()
        
        
    def addToFullLog(self, text):
        
        self.fullLog += text
        
        
    def getFullLog(self):
        
        return self.fullLog
        
        
    def close(self):
        
        sys.stdout = self.old_stdout
        
        
    def save(self):
        
        directory = "Logs"
        
        # Makes log directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = time.time()
        timestampString = datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d_%H_%M_%S_%f')
        
        saveFileName = directory + "/log_" + timestampString[0:23] + ".txt"
        logFile = open(saveFileName, 'w')
        logFile.write(self.fullLog)
        
    
    def clear(self):
        
        self.fullLog = ''
    
    
    def GUIAction(self):
        
        self.GUI.controlTextLog.write(self.fullText)
    
    
def myLogInstance(GUI=None):
    
    global logg
    
    logg = _myLog(GUI)
    print "loggging started"
    

class myLog():
    
    def __init__(self, GUI=None):
    
        global logg
        
        self.logThread = threading.Thread(target=myLogInstance, args=(GUI,))
        self.logThread.daemon = True
        self.logThread.start()
        time.sleep(1)
        self.logg = logg
        print "Active threads:" + str(threading.active_count())
        
    def close(self):
        
        self.logg.close()
        self.logThread.join()
        
    def getFullLog(self):
        
        return self.logg.getFullLog()
    
    def save(self, event):
        
        self.logg.save()
        
    def clear(self):
        
        self.logg.clear()
    

if __name__ == '__main__':
    
    logg = myLog()
    
    print 'Hello world'
    
    try:
        a = 1/0
    except Exception as error:
        print error
    
    print 'Hello world123'
    print 'Hello world123456'
    print 'Hello world123456789'
    
    logg.close()
    print logg.getFulllogg()
    
    print "Active threads:" + str(threading.active_count())
