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
import random
import time

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab

class GraphPanel:
    
    def __init__(self, mainFrame, panel):
        self.panel = panel
        self.mainFrame = mainFrame
        self.dataFX = [0.0]
        self.dataFY = [0.0]
        self.dataFZ = [0.0]
        self.dataTX = [0.0]
        self.dataTY = [0.0]
        self.dataTZ = [0.0]
        self.t_start = time.time()
        self.t_array = [0.0]
        
        self.biasFlag = False
        
        self.redraw_timer = wx.Timer(self.mainFrame)
        self.mainFrame.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        refreshRate = 30.0 # 30 Hz
        self.redraw_timer.Start(1.0/refreshRate * 1000)
        
        self.paused = False
        
        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        
        self.xmin_control_force = BoundControlBox(self.panel, -1, "X min", 0, pos= (500,0))
        self.xmax_control_force = BoundControlBox(self.panel, -1, "X max", 50, pos= (620,0))
        self.ymin_control_force = BoundControlBox(self.panel, -1, "Y min", 0, pos= (500,110))
        self.ymax_control_force = BoundControlBox(self.panel, -1, "Y max", 100, pos= (620,110))
        
        self.xmin_control_moment = BoundControlBox(self.panel, -1, "X min", 0, pos= (500,300))
        self.xmax_control_moment = BoundControlBox(self.panel, -1, "X max", 50, pos= (620,300))
        self.ymin_control_moment = BoundControlBox(self.panel, -1, "Y min", 0, pos= (500,410))
        self.ymax_control_moment = BoundControlBox(self.panel, -1, "Y max", 100, pos= (620,410))
        
        self.pause_button = wx.Button(self.panel, -1, "Pause", pos=(510,570))
        self.mainFrame.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.mainFrame.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.cb_grid = wx.CheckBox(self.panel, -1, "Show Grid", style=wx.ALIGN_RIGHT, pos=(510,545))
        self.mainFrame.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, "Show X labels", style=wx.ALIGN_RIGHT, pos=(510,520))
        self.mainFrame.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)
        
        # Button for handling bias and un-bias.
        self.biasUnbiasButton = wx.Button(self.panel, -1, "Bias", pos=(610,570))
        self.mainFrame.Bind(wx.EVT_BUTTON, self.biasUnbiasButtonPressed, self.biasUnbiasButton)
        
    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((5.0, 6.0), dpi=self.dpi)

        self.axesForces = self.fig.add_subplot(211)
        self.axesForces.set_axis_bgcolor('black')
        #self.axes.set_title('Forces', size=12) ######################### Set title of top axes to transducer name and serial number
        #ylabelForcesString = self.mainFrame.screenController.panel.FUnitsHeading
        self.axesForces.set_ylabel('Forces (N)', size=12) ##################### Set axes label to what is received from load cell
        
        pylab.setp(self.axesForces.get_xticklabels(), fontsize=10)
        pylab.setp(self.axesForces.get_yticklabels(), fontsize=10)
        
        self.axesMoments = self.fig.add_subplot(212)
        self.axesMoments.set_axis_bgcolor('black')
        #ylabelMomentsString = self.mainFrame.screenController.panel.TUnitsHeading
        self.axesMoments.set_ylabel('Moments (Nm)', size=12) ################## Set axes label to what is received from load cell
        self.axesMoments.set_xlabel('Time (s)', size=12)
        
        pylab.setp(self.axesMoments.get_xticklabels(), fontsize=10)
        pylab.setp(self.axesMoments.get_yticklabels(), fontsize=10)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
#        self.plot_data_FX = self.axesForces.plot(self.dataFX, 0, linewidth=1, color=(1, 0, 0))[0]
#        self.plot_data_FY = self.axesForces.plot(self.dataFY, 0, linewidth=1, color=(0, 1, 0))[0]
#        self.plot_data_FZ = self.axesForces.plot(self.dataFZ, 0, linewidth=1, color=(0, 0, 1))[0]
#        
#        self.plot_data_TX = self.axesMoments.plot(self.dataTX, 0, linewidth=1, color=(1, 0, 0))[0]
#        self.plot_data_TY = self.axesMoments.plot(self.dataTY, 0, linewidth=1, color=(0, 1, 0))[0]
#        self.plot_data_TZ = self.axesMoments.plot(self.dataTZ, 0, linewidth=1, color=(0, 0, 1))[0]
        self.plot_data_FX = self.axesForces.plot([0], 0, linewidth=1, color=(1, 0, 0))[0]
        self.plot_data_FY = self.axesForces.plot([0], 0, linewidth=1, color=(0, 1, 0))[0]
        self.plot_data_FZ = self.axesForces.plot([0], 0, linewidth=1, color=(0, 0, 1))[0]
        
        self.plot_data_TX = self.axesMoments.plot([0], 0, linewidth=1, color=(1, 0, 0))[0]
        self.plot_data_TY = self.axesMoments.plot([0], 0, linewidth=1, color=(0, 1, 0))[0]
        self.plot_data_TZ = self.axesMoments.plot([0], 0, linewidth=1, color=(0, 0, 1))[0]
            
    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        self.t = time.time() - self.t_start
    
        if not self.paused:
            #self.mainFrame.data.append(self.mainFrame.datagen.next())
            
            try:
#                stringForces,stringMoments = self.mainFrame.screenController.panel.updatePlot()
#                FX = float(stringForces.split('\n\n')[0].strip())
#                FY = float(stringForces.split('\n\n')[1].strip())
#                FZ = float(stringForces.split('\n\n')[2].strip())
#                TX = float(stringMoments.split('\n\n')[0].strip())
#                TY = float(stringMoments.split('\n\n')[1].strip())
#                TZ = float(stringMoments.split('\n\n')[2].strip())
                FX = 0.00
                FY = 0.50
                FZ = 0.75
                TX = 0.00
                TY = 0.50
                TZ = 0.75
                self.dataFX.append(FX)
                self.dataFY.append(FY)
                self.dataFZ.append(FZ)
                self.dataTX.append(TX)
                self.dataTY.append(TY)
                self.dataTZ.append(TZ)
                self.t = time.time() - self.t_start
                self.t_array.append(self.t)
                
                #print self.mainFrame.data
            
            except:
                pass
        
        self.draw_plot()
        
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
        
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
        
    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control_force.is_auto():
            xmax_force = self.t if self.t > 20 else 20
        else:
            xmax_force = float(self.xmax_control_force.manual_value())
            
        if self.xmin_control_force.is_auto():            
            xmin_force = xmax_force - 20
        else:
            xmin_force = float(self.xmin_control_force.manual_value())
        
        if self.xmax_control_moment.is_auto():
            xmax_moment = self.t if self.t > 20 else 20
        else:
            xmax_moment = float(self.xmax_control_moment.manual_value())
            
        if self.xmin_control_moment.is_auto():            
            xmin_moment = xmax_moment - 20
        else:
            xmin_moment = float(self.xmin_control_moment.manual_value())
        

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        if self.ymin_control_force.is_auto():
            ymin_force = round(min([min(self.dataFX), min(self.dataFY), min(self.dataFZ)]), 0)
        else:
            ymin_force = float(self.ymin_control_force.manual_value())
        
        if self.ymax_control_force.is_auto():
            ymax_force = round(max([max(self.dataFX), max(self.dataFY), max(self.dataFZ)]), 0)
        else:
            ymax_force = float(self.ymax_control_force.manual_value())
        
        if self.ymin_control_moment.is_auto():
            ymin_moment = round(min([min(self.dataTX), min(self.dataTY), min(self.dataTZ)]), 0)
        else:
            ymin_moment = float(self.ymin_control_moment.manual_value())
        
        if self.ymax_control_moment.is_auto():
            ymax_moment = round(max([max(self.dataTX), max(self.dataTY), max(self.dataTZ)]), 0)
        else:
            ymax_moment = float(self.ymax_control_moment.manual_value())

        self.axesForces.set_xbound(lower=xmin_force, upper=xmax_force)
        self.axesForces.set_ybound(lower=ymin_force, upper=ymax_force)
        
        self.axesMoments.set_xbound(lower=xmin_moment, upper=xmax_moment)
        self.axesMoments.set_ybound(lower=ymin_moment, upper=ymax_moment)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axesForces.grid(True, color='gray')
        else:
            self.axesForces.grid(False)
            
        if self.cb_grid.IsChecked():
            self.axesMoments.grid(True, color='gray')
        else:
            self.axesMoments.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axesForces.get_xticklabels(), visible=self.cb_xlab.IsChecked())
        pylab.setp(self.axesMoments.get_xticklabels(), visible=self.cb_xlab.IsChecked())
        
#        self.plot_data_FX.set_xdata(np.arange(len(self.dataFX)))
#        self.plot_data_FX.set_ydata(np.array(self.dataFX))
#        
#        self.plot_data_FY.set_xdata(np.arange(len(self.dataFY)))
#        self.plot_data_FY.set_ydata(np.array(self.dataFY))
#        
#        self.plot_data_FZ.set_xdata(np.arange(len(self.dataFZ)))
#        self.plot_data_FZ.set_ydata(np.array(self.dataFZ))
#        
#        self.plot_data_TX.set_xdata(np.arange(len(self.dataTX)))
#        self.plot_data_TX.set_ydata(np.array(self.dataTX))
#        
#        self.plot_data_TY.set_xdata(np.arange(len(self.dataTY)))
#        self.plot_data_TY.set_ydata(np.array(self.dataTY))
#        
#        self.plot_data_TZ.set_xdata(np.arange(len(self.dataTZ)))
#        self.plot_data_TZ.set_ydata(np.array(self.dataTZ))
        
        self.plot_data_FX.set_xdata(np.array(self.t_array))
        self.plot_data_FX.set_ydata(np.array(self.dataFX))
        
        self.plot_data_FY.set_xdata(np.array(self.t_array))
        self.plot_data_FY.set_ydata(np.array(self.dataFY))
        
        self.plot_data_FZ.set_xdata(np.array(self.t_array))
        self.plot_data_FZ.set_ydata(np.array(self.dataFZ))
        
        self.plot_data_TX.set_xdata(np.array(self.t_array))
        self.plot_data_TX.set_ydata(np.array(self.dataTX))
        
        self.plot_data_TY.set_xdata(np.array(self.t_array))
        self.plot_data_TY.set_ydata(np.array(self.dataTY))
        
        self.plot_data_TZ.set_xdata(np.array(self.t_array))
        self.plot_data_TZ.set_ydata(np.array(self.dataTZ))
        
        self.canvas.draw()
        
    def biasUnbiasButtonPressed(self, event):
        try:
            if not self.biasFlag:    # If un-baised
                self.mainFrame.screenController.m_model.biasSensor(0) # 0 means first transducer
                self.biasUnbiasButton.SetLabel('Un-bias')
                self.biasFlag = True
            else:
                self.mainFrame.screenController.m_model.unbiasSensor(0) # 0 means first transducer
                self.biasUnbiasButton.SetLabel('Bias')
                self.biasFlag = False
        except Exception as e:
            print e
            self.mainFrame.disconnect()
        
        

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval, pos):
        wx.Panel.__init__(self, parent, ID, pos)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value
        
class mainFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Test frame for graph', size = (1000,1000))
        
        self.datagen = DataGen()
        self.data = [0]
        self.dataFY = [0]
        
        self.panel2 = wx.Panel(self, pos=(0,700), size=(500,200))
        
        self.panel = wx.Panel(self, pos=(0,0), size=(800,600))
        self.GraphPanel = GraphPanel(self, self.panel)
        
        self.Show()
        
class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init
        
    def next(self):
        self._recalc_data()
        return self.data
    
    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8: 
            # attraction to the initial value
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta
        
  
def main():
    app = wx.App()
    mainFrame()
    app.MainLoop()
    print 'Done'      
        
if __name__ == '__main__':
    main()    