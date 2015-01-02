'''
Created on 7 May 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Used to calculate QMED from flow data
Called from within the QMED tab

    Statistical Flood Estimation Tool
    Copyright (C) 2014  Neil Nutt, neilnutt[at]googlemail[dot]com
    https://github.com/OpenHydrology/StatisticalFloodEstimationTool

    This program is free software; you can redistribute it and/or modif
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import wx
import numpy as np
import config
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from floodestimation import parsers

from floodestimation.entities import AmaxRecord
from datetime import date

class AmaxFrame(wx.Frame):
  def __init__(self, parent):
    super(AmaxFrame, self).__init__(parent,title="Amax series",size=(500,500))
    
    self.InitUI(parent)
    self.Layout()
    self.Refresh()
    self.Centre()
    self.Show()
    
  def InitUI(self,parent):
    self.panel = wx.Panel(self,-1)
    self.p = parent
    self.temporary_amax_records = config.analysis.catchment.amax_records
    
    self.table = wx.Panel(self, -1)
    self.list = CheckListCtrl(self.table)
    self.list.InsertColumn(0, 'YEAR')
    self.list.InsertColumn(1, 'STAGE')
    self.list.InsertColumn(2, 'FLOW')
    self.list.InsertColumn(3, 'FLAG')
    self.list.SetColumnWidth(0, 100)
    self.list.SetColumnWidth(1, 100)
    self.list.SetColumnWidth(2, 100)
    self.list.SetColumnWidth(3, 100)
    
    for amax_record in self.temporary_amax_records:
      index = self.list.InsertStringItem(0, str(amax_record.date))
      self.list.SetItem(index, 1, str(amax_record.stage))
      self.list.SetItem(index, 2, str(amax_record.flow))
      self.list.SetItem(index, 3, str(amax_record.flag))
      self.list.CheckItem(index,check=True)  
    
    
    self.load_amax_file_btn = wx.Button(self.panel, -1, ' Load AMAX FILE ')
    self.manual_amax_edit_btn = wx.Button(self.panel, -1, ' Manual AMAX Entry ')
    self.cancel_btn = wx.Button(self.panel, -1, ' Cancel ')
    self.apply_btn = wx.Button(self.panel, -1, ' Apply ')
    
    self.load_amax_file_btn.Bind(wx.EVT_BUTTON,self.loadAmaxEvent)
    self.manual_amax_edit_btn.Bind(wx.EVT_BUTTON,self.manualAmaxEvent)
    self.cancel_btn.Bind(wx.EVT_BUTTON,self.cancelEvent)
    self.apply_btn.Bind(wx.EVT_BUTTON,self.applyEvent)
    
    sizer = wx.GridBagSizer(vgap=5, hgap=10)
    sizer.Add(self.table, pos=(0,0),span=(1,4),flag=wx.EXPAND)
    sizer.Add(self.load_amax_file_btn,pos=(1,0))
    sizer.Add(self.manual_amax_edit_btn,pos=(1,1))
    sizer.Add(self.cancel_btn,pos=(1,2))
    sizer.Add(self.apply_btn,pos=(1,3))
    
    border = wx.BoxSizer()
    border.Add(sizer, 0, wx.ALL, 20)
    self.panel.SetSizerAndFit(border)
    self.panel.Fit()
        
    self.panel.Layout()
    self.panel.Refresh()
    self.panel.Update()
    
    self.Refresh()
    self.Update()
  
  def manualAmaxEvent(self,event):
    AmaxManual(self)
  
  def cancelEvent(self,event):
    self.Destroy()
    
  def applyEvent(self,event):
    config.analysis.catchment.amax_records = self.temporary_amax_records
    self.Destroy()
  
  def loadAmaxEvent(self,event):
      loadBox = wx.FileDialog(self,"Load amax file", "", "", "Annual maxima file (*.am;*.csv)|*.am;*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
      
      if loadBox.ShowModal() == wx.ID_OK:
        self.temporary_amax_records = []
        filePath = loadBox.GetPath()
        self.temporary_amax_records = parsers.AmaxParser().parse(filePath)
      loadBox.Destroy()
      
      self.refreshAmaxTable()
  
  def refreshAmaxTable(self):    
      self.list.DeleteAllItems()
      for amax_record in self.temporary_amax_records:
        index = self.list.InsertStringItem(0, str(amax_record.date))
        self.list.SetItem(index, 1, str(amax_record.stage))
        self.list.SetItem(index, 2, str(amax_record.flow))
        self.list.SetItem(index, 3, str(amax_record.flag))
        self.list.CheckItem(index,check=True)  
      
      self.Refresh()
      self.Update()

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,size=(450,400), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class AmaxManual(wx.Frame):
    def __init__(self, parent):
      super(AmaxManual, self).__init__(parent,title="Amax series",size=(500,500))
      
      self.InitUI(parent)
      self.Layout()
      self.Refresh()
      self.Centre()
      self.Show()
      
    def InitUI(self,parent):
        self.panel = wx.Panel(self,-1)
        self.p = parent
        
        
        self.delimitor_label = wx.StaticText(self.panel, -1, "Delimitor")
        self.delimitor = wx.TextCtrl(self.panel, -1, ",")
        self.date_column_label = wx.StaticText(self.panel, -1, "Date in column")
        self.date_column = wx.TextCtrl(self.panel, -1, "1")
        self.flow_data_column_label = wx.StaticText(self.panel, -1, "Flow data in column")
        self.flow_data_column = wx.TextCtrl(self.panel, -1, "2")
        self.stage_data_column_label = wx.StaticText(self.panel, -1, "Stage data in column")
        self.stage_data_column = wx.TextCtrl(self.panel, -1, "3")
        self.data_series_entry = wx.TextCtrl(self.panel, -1, "Data series entry, paste or load series", size=(450,300),style=wx.TE_MULTILINE)
        
        self.load_flow_btn = wx.Button(self.panel, -1, ' Load AM series ')
        self.cancel_flow_btn = wx.Button(self.panel, -1, ' Cancel ')
        self.save_flow_btn = wx.Button(self.panel, -1, ' Apply ')
        self.load_flow_btn.Bind(wx.EVT_BUTTON, self.OnLoadFlowSeries)
        self.cancel_flow_btn.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.save_flow_btn.Bind(wx.EVT_BUTTON, self.OnSave)   
        
        sizer = wx.GridBagSizer(vgap=10, hgap=10)
        sizer.Add(self.delimitor_label, pos=(0, 0), span=(1,1))
        sizer.Add(self.delimitor, pos=(1, 0), span=(1,1))
        sizer.Add(self.date_column_label, pos=(0, 1), span=(1,1))
        sizer.Add(self.date_column, pos=(1, 1), span=(1,1))
        sizer.Add(self.flow_data_column_label, pos=(0, 2), span=(1,1))
        sizer.Add(self.flow_data_column, pos=(1, 2), span=(1,1))
        sizer.Add(self.stage_data_column_label, pos=(0, 3), span=(1,1))
        sizer.Add(self.stage_data_column, pos=(1, 3), span=(1,1))
        sizer.Add(self.data_series_entry, pos=(3, 0), span=(1,4))
        
        sizer.Add(self.load_flow_btn, pos=(4, 0), span=(1,1))
        sizer.Add(self.cancel_flow_btn, pos=(4, 2), span=(1,1))
        sizer.Add(self.save_flow_btn, pos=(4, 3), span=(1,1))
      
        
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        self.panel.SetSizerAndFit(border)
        self.panel.Fit()
        
        self.panel.Layout()
        self.panel.Refresh()
    
    def OnLoadFlowSeries(self,event):
      loadBox = wx.FileDialog(self, "Open flow series file", "", "","", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
      
      #self.title_label.SetLabel(str(self.p.title.GetValue()))
      if loadBox.ShowModal() == wx.ID_OK:
        filePath = loadBox.GetPath()
        f = open(filePath,'r')
        lines = f.readlines()
        self.data_series_entry.SetValue('')
        for line in lines:
          self.data_series_entry.AppendText(str(line))
        
    
    def OnCancel(self,event):
      self.Destroy()
    
    def OnSave(self,event):
      self.p.temporary_amax_records = []
      user_enterer_data_series = self.data_series_entry.GetValue()
      date_column = int(self.date_column.GetValue())-1
      stage_column = int(self.stage_data_column.GetValue())-1
      separator = self.delimitor.GetValue()
      flow_column = int(self.flow_data_column.GetValue())-1
      lines = user_enterer_data_series.split('\n')
      year = 1900
      for line in lines:
        data_entry = line.split(separator)
        year = year +1
        
        stage_value = -9999.9
        flow_value = -9999.9
        
        if len(data_entry) > flow_column:
          flow_value=float(data_entry[flow_column])
        if len(data_entry) > stage_column:
          stage_value = float(data_entry[stage_column])
          
        record = AmaxRecord(date=date(year,1,1), flow=flow_value, stage=stage_value)
        self.p.temporary_amax_records.append(record)
        
      self.p.refreshAmaxTable()
      self.Destroy()
    
if __name__ == "__main__":
    app = wx.App(redirect=False)
    #app = wx.App(redirect=True,filename='error_log.txt')
    AmaxFrame(None).Show()
    app.MainLoop()