import wx
import numpy 
import matplotlib

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as NavigationToolbar

class MatplotPanel:

    def __init__(self, panel):     

        #self.sizer = wx.BoxSizer(wx.VERTICAL)
        #panel.SetSizer(self.sizer)
        
        self.figure = Figure()
        self.axes1 = self.figure.add_subplot(121)
        self.axes2 = self.figure.add_subplot(122)
        self.canvas = FigureCanvas(panel, -1, self.figure)
        #self.toolbar = NavigationToolbar(self.canvas)

        #self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        #self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        self.drawSin()

        x = numpy.arange(0.0,10,0.1)
        y = numpy.sin(x)

        self.axes1.clear()
        self.axes1.plot(x, y)
        
    def drawSin(self):

        x = numpy.arange(0.0,10,0.1)
        y = numpy.sin(x)

        self.axes1.clear()
        self.axes1.plot(x, y)
        
class MatplotPanel2:
    
    def __init__(self, panel):
        self.figure = Figure(figsize=(5, 5), dpi=100, tight_layout=True)
        self.axes1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(panel, -1, self.figure)
        self.axes1.set_xlabel('common xlabel')
        
        self.drawSin()
        
    def drawSin(self):

        x = numpy.arange(0.0,10,0.1)
        y = numpy.sin(x)

        self.axes1.clear()
        self.axes1.plot(x, y)
        
        
class TestFrame(wx.Frame):
    def __init__(self,parent,title):
#        wx.Frame.__init__(self,parent,title=title,size=(500,500))
#        self.sp = wx.SplitterWindow(self)
#        self.p1 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
#        self.p2 = MatplotPanel(self.sp)
#        self.sp.SplitVertically(self.p1,self.p2,100)
#        self.statusbar = self.CreateStatusBar()
#        self.statusbar.SetStatusText('Oi')
        wx.Frame.__init__(self,parent,title=title,size=(1000,500))
        panel1 = wx.Panel(self, pos=(0,0), size=(500, 500))
        self.p1 = MatplotPanel2(panel1)
        #panel2 = wx.Panel(self, pos=(500,0), size=(500, 500))
        #self.p2 = MatplotPanel2(panel2)
        
        self.Show()

#class MatplotPanel(wx.Panel):
#    def __init__(self, parent):
#        wx.Panel.__init__(self, parent,-1,size=(50,50))
#
#        self.figure = Figure()
#        self.axes = self.figure.add_subplot(111)
#        t = numpy.arange(0.0,10,1.0)
#        s = [0,1,0,1,0,2,1,2,1,0]
#        self.y_max = 1.0
#        self.axes.plot(t,s)
#        self.canvas = FigureCanvas(self,-1,self.figure)

if __name__ == '__main__':
    #app = wx.App(redirect=False)
    app = wx.App()
    frame = TestFrame(None, 'Hello World!')
    app.MainLoop()