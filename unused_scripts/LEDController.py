'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 31-07-2017
-----
'''

import wx

class LED:
    
    def __init__(self, frame, x, y):
        self.panel = wx.Panel(frame, pos=(x, y), size=(25, 25))
        
        #self.panel.SetDoubleBuffered(True) ######## This should fix flickering
        
    # For custom colour:
    def LEDColour(self, colour): # Saturated Red
        self.colour = colour
        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDColourShow)
        #self.panel.Refresh()
        #self.panel.Update()
    def LEDColourShow(self, event):
        self.dc = wx.PaintDC(event.GetEventObject())
        #self.dc.Clear()
        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
        self.dc.SetBrush(wx.Brush(self.colour, wx.SOLID)) # Fill.
        self.dc.DrawCircle(12, 12, 10)
        
        
        
#    def LEDBlack(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDBlackShow)
#    def LEDBlackShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('BLACK', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDGreen(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDGreenShow)
#    def LEDGreenShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('#228b22', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDOrange(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDOrangeShow)
#    def LEDOrangeShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('#ff7f00', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDRed(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDRedShow)
#    def LEDRedShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('RED', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDBrightGreen(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDBrightGreenShow)
#    def LEDBrightGreenShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('#7cfc00', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDBrightRed(self):
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDBrightRedShow)
#    def LEDBrightRedShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('#ff0000', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)
#        
#    def LEDSatRed(self): # Saturated Red
#        self.panelBind = self.panel.Bind(wx.EVT_PAINT, self.LEDSatRedShow)
#    def LEDSatRedShow(self, event):
#        self.dc = wx.PaintDC(event.GetEventObject())
#        self.dc.Clear()
#        self.dc.SetPen(wx.Pen('BLACK', 2)) # Outline.
#        self.dc.SetBrush(wx.Brush('#b22222', wx.SOLID)) # Fill.
#        self.dc.DrawCircle(12, 12, 10)