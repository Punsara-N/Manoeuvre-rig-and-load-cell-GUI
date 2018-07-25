class Class1:
    
    A = 1
    
    def __init__(self):
        print self.A
        self.Class2(self)
        print self.A
    
    class Class2:

        def __init__(self, B):         
            print 'hello'
            B.A = 2
            
Class1()
        
        
