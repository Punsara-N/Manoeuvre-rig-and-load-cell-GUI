import wx

class LED(wx.Panel):
    
    def __init__(self, parent):
        
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.colour = wx.Colour(0,0,0)

    def on_paint(self, event):
        
        w,h = self.GetSize()
        self.dc = wx.PaintDC(self)
        self.dc.Clear()
        #self.PrepareDC(self.dc)
        self.dc.SetPen(wx.Pen(wx.BLACK, 1))
        self.dc.SetBrush(wx.Brush(self.colour))
        self.dc.DrawCircle(w/2,h/2,12)