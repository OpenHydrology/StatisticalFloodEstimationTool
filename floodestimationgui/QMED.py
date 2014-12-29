'''
Created on 27 Apr 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Tab for calculating QMED

    Statistical Flood Estimation Tool
    Copyright (C) 2014  Neil Nutt, neilnutt[at]googlemail[dot]com
    https://github.com/OpenHydrology/StatisticalFloodEstimationTool

    This program is free software; you can redistribute it and/or modify
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
import wx,os,sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import config
from floodestimation.loaders import load_catchment
from floodestimation import db
from floodestimation.collections import CatchmentCollections
from floodestimation.analysis import QmedAnalysis
from AMAX import AmaxFrame
from floodestimation import parsers


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,size=(750,100), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class Fpanel(wx.Panel):
    def __init__(self, parent,p):
      wx.Panel.__init__(self, parent)
      self.p=p
      
      db_session = db.Session()
      self.gauged_catchments = CatchmentCollections(db_session)
      self.qmed_analysis = QmedAnalysis(config.target_catchment, self.gauged_catchments)
      db_session.close()
      
      self.qmed_method = 'best'
      self.donor_search_criteria_refreshed = True
      
      self.adoptedQmed = '-'
      
      self.calc_obs_amax_btn = wx.Button(self, -1, ' AMAX SERIES ')
      self.calc_obs_amax_btn.Bind(wx.EVT_BUTTON,self.amax_area)
      self.calc_obs_pot_btn = wx.Button(self, -1, ' POT SERIES ')
      self.calc_obs_pot_btn.Bind(wx.EVT_BUTTON,self.pot_area)
      self.refresh_calcs_btn = wx.Button(self, -1, ' REFRESH CALCS ')  
      
      self.qmed_notes = wx.TextCtrl(self, -1, "Notes on QMED", size=(350,150),style=wx.TE_MULTILINE)
      
      self.qmed_2008_label = wx.StaticText(self, -1, "QMED CDS 2008")
      self.qmed_1999_label = wx.StaticText(self, -1, "QMED CDS 1999")
      self.qmed_area_label = wx.StaticText(self, -1, "QMED AREA")
      self.qmed_amax_label = wx.StaticText(self, -1, "QMED AMAX")
      self.qmed_pot_label = wx.StaticText(self, -1, "QMED POT")
      self.qmed_width_label = wx.StaticText(self, -1, "QMED Channel width")
      self.user_qmed_label = wx.StaticText(self, -1, "User QMED")
      self.selected_unadj_qmed_label = wx.StaticText(self, -1, "Selected rural QMED")
      self.station_search_distance_label = wx.StaticText(self, -1, "Station search distance")
      self.station_search_limit_label = wx.StaticText(self, -1, "Station search limit")
      self.idw_label = wx.StaticText(self, -1, "IDW")
      self.selected_unadj_qmed = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      
      self.qmed_cds2008 = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.qmed_cds1999 = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.qmed_areaOnly = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.qmed_obs_amax = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.qmed_obs_pot = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.qmed_geom = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY) 
      self.qmed_user = wx.TextCtrl(self, -1, "-") 
      
      self.rb1 = wx.RadioButton(self, -1, '', style=wx.RB_GROUP)
      self.rb2 = wx.RadioButton(self, -1, '')
      self.rb3 = wx.RadioButton(self, -1, '')
      self.rb4 = wx.RadioButton(self, -1, '')
      self.rb5 = wx.RadioButton(self, -1, '')
      self.rb6 = wx.RadioButton(self, -1, '')
      self.rb7 = wx.RadioButton(self, -1, '')
      
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb1.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb2.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb3.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb4.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb5.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb6.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb7.GetId())

      self.station_search_distance = wx.TextCtrl(self, -1, "500.0")
      self.station_limit = wx.TextCtrl(self, -1, "5")
      self.idw_weight = wx.TextCtrl(self, -1, "3")
      
      self.station_search_distance.Bind(wx.EVT_TEXT, self.UpdateDonorCriteria)
      self.station_limit.Bind(wx.EVT_TEXT, self.UpdateDonorCriteria)
      
      #self.calcQMeds()
      
      self.distance_decay_update= wx.RadioButton(self, -1, "Decaying with distance", style=wx.RB_GROUP)
      self.direct_transfer_update  = wx.RadioButton(self, -1, 'Equal weighting')
      self.dont_update  = wx.RadioButton(self, -1, "Don't update")
      
      #self.Bind(wx.EVT_RADIOBUTTON, self.SetUpdate, id=self.dont_update.GetId())
      #self.Bind(wx.EVT_RADIOBUTTON, self.SetUpdate, id=self.distance_decay_update.GetId())
      #self.Bind(wx.EVT_RADIOBUTTON, self.SetUpdate, id=self.direct_transfer_update.GetId())
      
      self.local_qmed_adjustment_label = wx.StaticText(self, -1, "Local QMED adjustment")
      self.locally_adjusted_qmed_label = wx.StaticText(self, -1, "Locally adjusted QMED")
      self.locally_adjusted_qmed = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.local_qmed_adjustment = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      
      self.update_for_urb_chk = wx.CheckBox(self,-1,'Update for urbanisation')
      self.update_for_urb_chk.Bind(wx.EVT_CHECKBOX, self.SetUrbanChk, id=self.update_for_urb_chk.GetId())
      
      self.urban_expansion_factor_label = wx.StaticText(self, -1, "Urban expansion factor")
      self.adjusted_urbext_label = wx.StaticText(self, -1, "Adjusted URBEXT")
      self.urban_adjustment_factor_label = wx.StaticText(self, -1, "Urban adjustment factor")
      
      self.urban_expansion_factor = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.adjusted_urbext = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.urban_adjustment_factor = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      
      self.adopted_qmed_label = wx.StaticText(self, -1, "Adopted QMED")
      self.adopted_qmed = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      
      sizer = wx.GridBagSizer(vgap=5, hgap=10)
      sizer.Add(self.calc_obs_amax_btn, pos=(7,3))
      sizer.Add(self.calc_obs_pot_btn, pos=(7,4))
      
      sizer.Add(self.refresh_calcs_btn,pos=(0,3))
      sizer.Add(self.qmed_notes, pos=(1,3), span=(5,3))
      
      sizer.Add(self.qmed_2008_label,pos=(0,0))
      sizer.Add(self.qmed_1999_label,pos=(1,0))
      sizer.Add(self.qmed_area_label,pos=(2,0))
      sizer.Add(self.qmed_amax_label,pos=(3,0))
      sizer.Add(self.qmed_pot_label,pos=(4,0))
      sizer.Add(self.qmed_width_label,pos=(5,0))
      sizer.Add(self.user_qmed_label,pos=(6,0))
      sizer.Add(self.selected_unadj_qmed_label,pos=(7,0))
      
      sizer.Add(self.qmed_cds2008, pos=(0,1))
      sizer.Add(self.qmed_cds1999, pos=(1,1))
      sizer.Add(self.qmed_areaOnly, pos=(2,1))
      sizer.Add(self.qmed_obs_amax, pos=(3,1))
      sizer.Add(self.qmed_obs_pot, pos=(4,1))
      sizer.Add(self.qmed_geom, pos=(5,1))
      sizer.Add(self.qmed_user, pos=(6,1))
      sizer.Add(self.selected_unadj_qmed, pos=(7,1))
      
      sizer.Add(self.rb1, pos=(0,2))
      sizer.Add(self.rb2, pos=(1,2))
      sizer.Add(self.rb3, pos=(2,2))
      sizer.Add(self.rb4, pos=(3,2))
      sizer.Add(self.rb5, pos=(4,2))
      sizer.Add(self.rb6, pos=(5,2))
      sizer.Add(self.rb7, pos=(6,2))
      
      self.table = wx.Panel(self, -1)
      self.list = CheckListCtrl(self.table)
      self.list.InsertColumn(0, 'STATION')
      self.list.InsertColumn(1, 'DISTANCE')
      self.list.InsertColumn(2, 'ADJUSTMENT FACTOR')
      self.list.InsertColumn(3, 'ERROR CORRELATION')
      self.list.InsertColumn(4, 'WEIGHT')
      self.list.SetColumnWidth(0, 250)
      self.list.SetColumnWidth(1, 100)
      self.list.SetColumnWidth(2, 100)
      self.list.SetColumnWidth(3, 100)
      self.list.SetColumnWidth(4, 100)
      
      sizer.Add(self.table, pos=(9,0),span=(1,6),flag=wx.EXPAND)
      sizer.Add(self.station_search_distance_label, pos=(10,0),span=(1,1))
      sizer.Add(self.station_search_distance, pos=(10,1),span=(1,1))
      sizer.Add(self.station_search_limit_label, pos=(10,2),span=(1,1))
      sizer.Add(self.station_limit, pos=(10,3),span=(1,1))
      sizer.Add(self.idw_label, pos=(10,4),span=(1,1))
      sizer.Add(self.idw_weight, pos=(10,5),span=(1,1))      
      sizer.Add(self.dont_update, pos=(11,0),span=(1,2))
      sizer.Add(self.distance_decay_update, pos=(12,0),span=(1,2))
      sizer.Add(self.direct_transfer_update, pos=(13,0),span=(1,2))
      
      sizer.Add(self.local_qmed_adjustment_label, pos=(12,2),span=(1,1))
      sizer.Add(self.local_qmed_adjustment, pos=(12,3),span=(1,1))
      sizer.Add(self.locally_adjusted_qmed_label, pos=(13,2),span=(1,1))
      sizer.Add(self.locally_adjusted_qmed, pos=(13,3),span=(1,1))
      
      sizer.Add(self.update_for_urb_chk,pos=(15,0),span=(1,1))
      sizer.Add(self.urban_expansion_factor,pos=(16,1),span=(1,1))
      sizer.Add(self.adjusted_urbext,pos=(17,1),span=(1,1))
      sizer.Add(self.urban_adjustment_factor,pos=(18,1),span=(1,1))
      sizer.Add(self.urban_expansion_factor_label,pos=(16,0),span=(1,1))
      sizer.Add(self.adjusted_urbext_label,pos=(17,0),span=(1,1))
      sizer.Add(self.urban_adjustment_factor_label,pos=(18,0),span=(1,1))
      
      sizer.Add(self.adopted_qmed_label, pos=(18,4),span=(1,1))
      sizer.Add(self.adopted_qmed, pos=(18,5),span=(1,1))
      
      #  Assign actions to buttons
      self.refresh_calcs_btn.Bind(wx.EVT_BUTTON, self.onRefresh)
      
      border = wx.BoxSizer()
      border.Add(sizer, 0, wx.ALL, 20)
      self.SetSizerAndFit(border)
      self.Fit()

    def SetUpdateMethod(self,event):
      
      self.updateMethod()
      self.refreshDonors()
      
    def updateMethod(self):
      self.donor_search_criteria_refreshed = True
      if self.distance_decay_update.GetValue():
        config.analysis.qmed_analysis.donor_weighting = 'idw'
      elif self.direct_transfer_update.GetValue():
        config.analysis.qmed_analysis.donor_weighting = 'equal'
      elif self.dont_update.GetValue():
        self.search_limit = 0
        self.station_limit.SetValue(str(0))
    
    def SetUrbanChk(self,event):
      self.updateUrbanisation()
      
    def updateUrbanisation(self):
      self.update_for_urbanisation = bool(self.update_for_urb_chk.GetValue())
      if self.update_for_urbanisation:
        self.keep_rural = False
      else:
        self.keep_rural = True
      self.calcQMeds()
      
      
    def SetVal(self, event):
      if bool(self.rb1.GetValue()) == True:
        self.qmed_method = 'descriptors'
      if bool(self.rb2.GetValue()) == True:
        self.qmed_method = 'descriptors_1999'
      if bool(self.rb3.GetValue()) == True:
        self.qmed_method = 'area'
      if bool(self.rb4.GetValue()) == True:
        self.qmed_method = 'amax_records'
      if bool(self.rb5.GetValue()) == True:
        self.qmed_method = 'pot_records'
      if bool(self.rb6.GetValue()) == True:
        self.qmed_method = 'channel_width'
      if bool(self.rb7.GetValue()) == True:
        self.qmed_method = 'user'
        config.analysis.qmed_analysis.adopted_qmed_value =  float(self.qmed_user.GetValue())
        
      if self.qmed_method == 'descriptors' or self.qmed_method == 'descriptors_1999':
        self.selected_unadj_qmed.SetLabel(str(config.analysis.qmed_analysis.qmed(method=self.qmed_method,as_rural=True,donor_catchments=[])))
      elif self.qmed_method== 'pot_records'or self.qmed_method == 'amax_records':
        self.selected_unadj_qmed.SetLabel(str(config.analysis.qmed_analysis.qmed(method=self.qmed_method)))
      elif self.qmed_method=='user':
        self.selected_unadj_qmed.SetLabel(self.qmed_user.GetValue())
        
      self.Refresh()
      self.Update()
      
    def onRefresh(self,event):
      self.updateUrbanisation()
      self.calcQMeds()
      self.updateMethod()
      if self.donor_search_criteria_refreshed:
        self.refreshDonors()
      self.identifyAdoptedDonors()
      self.refreshUrbanisation()
      self.updateAdopted()

    def refreshUrbanisation(self):
      self.urban_adjustment_factor.SetLabel(str(config.analysis.qmed_analysis.urban_adj_factor()))
      #self.urban_adjustment_factor.SetLabel(str(config.analysis.qmed_analysis._pruaf()))
      self.urban_expansion_factor.SetLabel(str('Not calculated'))
      

    def calcQMeds(self):
      config.analysis.run_qmed_analysis()
      
      qmedDict = config.analysis.results['qmed_all_methods']
      
      self.qmed_cds1999.SetLabel(str(config.analysis.qmed_analysis.qmed('descriptors_1999',as_rural=True,donor_catchments=[])))
      self.qmed_cds2008.SetLabel(str(config.analysis.qmed_analysis.qmed('descriptors',as_rural=True,donor_catchments=[])))
      self.qmed_obs_amax.SetLabel(str(qmedDict['amax_records']))
      self.qmed_obs_pot.SetLabel(str(qmedDict['pot_records']))
      self.qmed_areaOnly.SetLabel(str(config.analysis.qmed_analysis.qmed('area')))
      self.qmed_geom.SetLabel(str(qmedDict['channel_width']))

      self.Refresh()
      self.Update()    
    
    def refreshDonors(self):
      self.search_limit = int(self.station_limit.GetValue())
      self.search_distance = float(self.station_search_distance.GetValue())
      config.analysis.qmed_analysis.idw_power = float(self.idw_weight.GetValue())
      
      self.suggested_donors = config.analysis.qmed_analysis.find_donor_catchments(self.search_limit, self.search_distance)
      
      donors_details=list()
      weights = config.analysis.qmed_analysis._donor_weights(self.suggested_donors)
      
      self.list.BestSize
      self.list.DeleteAllItems()
      
      i = 0
      for donor in self.suggested_donors:
        donors_details.append([donor,donor.dist,config.analysis.qmed_analysis._donor_adj_factor(donor),config.analysis.qmed_analysis._error_correlation(donor),weights[i]])       
        i=i+1
     
      for donor in donors_details[::-1]:
        index = self.list.InsertStringItem(0, str(donor[0]))
        self.list.SetItem(index, 1, str(donor[1]))
        self.list.SetItem(index, 2, str(donor[2]))
        self.list.SetItem(index, 3, str(donor[3]))
        self.list.SetItem(index, 4, str(donor[4]))
        self.list.CheckItem(index,check=True)                            
    
      self.adopted_donors = self.suggested_donors  # Adopted donors to in the future be based on which ones are selected.  Everytime the search criteria or cds are refreshed the selected list would be reset
      self.donor_search_criteria_refreshed = False
    
    def identifyAdoptedDonors(self):
      self.adopted_donors = []
      for i in range(self.list.GetItemCount()):
        if self.list.IsChecked(i):
          checked_item = self.list.GetItemText(i,col=0)
          for site in self.suggested_donors:
            if str(site) == checked_item:
              self.adopted_donors.append(site)   
    
    def UpdateDonorCriteria(self,event):
      self.donor_search_criteria_refreshed = True
      
    def updateAdopted(self):
      if self.qmed_method == 'amax_records' or self.qmed_method == 'pot_records':
        locally_adjusted_qmed = config.analysis.qmed_analysis.qmed(method=self.qmed_method)
        unadjusted_qmed = locally_adjusted_qmed
        self.adopted_qmed.SetLabel(str(config.analysis.qmed_analysis.qmed(method=self.qmed_method)))      
      elif self.qmed_method == 'descriptors' or self.qmed_method == 'descriptors_1999':
        unadjusted_qmed = config.analysis.qmed_analysis.qmed(method=self.qmed_method,as_rural=self.keep_rural,donor_catchments=[])
        locally_adjusted_qmed = config.analysis.qmed_analysis.qmed(method=self.qmed_method,as_rural=self.keep_rural,donor_catchments=self.adopted_donors)
        self.adopted_qmed.SetLabel(str(config.analysis.qmed_analysis.qmed(method=self.qmed_method,as_rural=self.keep_rural,donor_catchments=self.adopted_donors)))
      elif self.qmed_method == 'user':
        unadjusted_qmed = float(self.qmed_user.GetValue())
        locally_adjusted_qmed = unadjusted_qmed
        self.adopted_qmed.SetLabel(str(unadjusted_qmed))
      else:
        unadjusted_qmed = config.analysis.qmed_analysis.qmed(method=self.qmed_method)
        locally_adjusted_qmed = config.analysis.qmed_analysis.qmed(method=self.qmed_method)
        self.adopted_qmed.SetLabel(str(config.analysis.qmed_analysis.qmed(method=self.qmed_method)))  

      adjustment = locally_adjusted_qmed/unadjusted_qmed
      self.locally_adjusted_qmed.SetValue(str(locally_adjusted_qmed))
      self.local_qmed_adjustment.SetValue(str(adjustment))
      
      config.analysis.qmed_analysis.adopted_qmed_value = float(self.adopted_qmed.GetValue())

    def amax_area(self,event):
      AmaxFrame(self).Show()
      
    def pot_area(self,event):
      loadBox = wx.FileDialog(self,"Load POT file", "", "", "Peaks over threshold file (*.pt;*.csv)|*.pt;*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
      
      if loadBox.ShowModal() == wx.ID_OK:
        config.analysis.catchment.pot_records = []
        filePath = loadBox.GetPath()
        config.analysis.catchment.pot_records = parsers.PotParser().parse(filePath)
      loadBox.Destroy()