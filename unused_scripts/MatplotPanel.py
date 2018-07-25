'''
-------------------------------------------------------------------------------------------------
This code is part of the python code written to communicate with the Wireless F/T system made by
ATI Industrial Automation. The original source code is written in java and can be found at
"http://www.ati-ia.com/Products/ft/software/wirelessFT_software.aspx". This code has been
transtaled to python to be used with Fly In Wind Tunnel (FIWT) code made to operate the manoeuvre
rig.

Python version 2.7.10
Python code written by: Punsara Navaratna, University of Bristol
Date: 01-08-2017
-------------------------------------------------------------------------------------------------
'''

import wx
import numpy 
import matplotlib

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as NavigationToolbar

class MatplotPanel:

    def __init__(self, panel, plotType):     
        
        if plotType == 'Force':
            self.figure = Figure(figsize=(5, 2), dpi=100, tight_layout=True)
            self.axes = self.figure.add_subplot(111)
            self.axes.set_ylabel('Force (N)')
            self.canvas = FigureCanvas(panel, -1, self.figure)
        elif plotType == 'Torque':
            self.figure = Figure(figsize=(5, 2), dpi=100, tight_layout=True)
            self.axes = self.figure.add_subplot(111)
            self.canvas = FigureCanvas(panel, -1, self.figure)

        self.drawSin()
        
    def drawSin(self):

        x = numpy.arange(0.0,10,0.1)
        y = numpy.sin(x)

        self.axes.clear()
        self.axes.plot(x, y)