import wx

########################################################################
class MyPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        txt = wx.TextCtrl(self)
        radio1 = wx.RadioButton( self, -1, " Radio1 ")
        radio1.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
        self.hiddenText = wx.TextCtrl(self)
        self.hiddenText.Hide()

        self.checkBtn = wx.CheckBox(self)
        self.checkBtn.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        self.hiddenText2 = wx.TextCtrl(self)
        self.hiddenText2.Hide()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txt, 0, wx.ALL, 5)
        sizer.Add(radio1, 0, wx.ALL, 5)
        sizer.Add(self.hiddenText, 0, wx.ALL, 5)
        sizer.Add(self.checkBtn, 0, wx.ALL, 5)
        sizer.Add(self.hiddenText2, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    #----------------------------------------------------------------------
    def onRadioButton(self, event):
        """"""
        print "in onRadioButton"
        self.hiddenText.Show()
        self.Layout()

    #----------------------------------------------------------------------
    def onCheckBox(self, event):
        """"""
        print "in onCheckBox"
        state = event.IsChecked()
        if state:
            self.hiddenText2.Show()
        else:
            self.hiddenText2.Hide()
        self.Layout()


########################################################################
class MyFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Radios and Text")
        panel = MyPanel(self)
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    f = MyFrame()
    app.MainLoop()