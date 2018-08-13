'''
Custom logging class

Punsara Navaratna 13-Aug-2018
'''
import sys
import time
import datetime
import threading

class myLog(object):
        
    def __init__(self, GUI=None):
        
        #self.logThread = self.thread()
        self.parentGUI = GUI
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
        
        
    def addToFullLog(self, text):
        
        self.fullLog += text
        
        
    def getFullLog(self):
        
        return self.fullLog
        
        
    def close(self):
        
        sys.stdout = self.old_stdout
        #self.logThread.join()
        
        
    def thread(self):
        
        try:
            dataThread = threading.Thread(target=self)
            dataThread.daemon = True
            dataThread.start()
        except Exception, errorText:
            print errorText
            
        return dataThread
    
    
    def GUIAction(self, objectHandles):
        
        pass
        

if __name__ == '__main__':
    
    def test():
        myLogg = myLog()
        print 'Hello world'
        
        try:
            a = 1/0
        except Exception as error:
            print error
    
        print 'Hello world123'
        print 'Hello world123456'
        print 'Hello world123456789'
        
        print "Active threads:" + str(threading.active_count())
        myLogg.close()
        print myLogg.getFullLog()
        time.sleep(2)
        print "Active threads:" + str(threading.active_count())
    
    dataThread = threading.Thread(target=test)
    dataThread.daemon = True
    dataThread.start()
    print dataThread.is_alive()
    time.sleep(2)
    dataThread.join()
    print dataThread.is_alive()
    print "Active threads:" + str(threading.active_count())
    
    
    