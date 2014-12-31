# -*- coding: utf-8 -*-

# Copyright (c) 2014  Neil Nutt <neilnutt@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Current package imports
import floodestimation,wx,wx.adv
import os
import FrontPage,CatchmentDescriptors,QMED
import config as c


from floodestimation.loaders import load_catchment
from floodestimation import db
from floodestimation.collections import CatchmentCollections
from floodestimation.analysis import QmedAnalysis, GrowthCurveAnalysis
from floodestimation.entities import Catchment, Descriptors

from project_file import save_project, load_project

class Analysis(object):
    def __init__(self):
        self.name = None
        self.catchment = Catchment("River Town", "River Burn")
        self.db_session = db.Session()
        self.gauged_catchments = CatchmentCollections(self.db_session)
        self.qmed = None

    def finish(self):
        self.db_session.close()

#    def run(self):
#        try:
 #           self.run_qmed_analysis()
  #          self.run_growthcurve()
   #     finally:
    #        self.finish()

    def run_qmed_analysis(self):
        self.qmed_analysis = QmedAnalysis(self.catchment, self.gauged_catchments)
        self.results = self.qmed_analysis.results_log
        self.results['qmed_all_methods'] = self.qmed_analysis.qmed_all_methods()
        

    def run_growthcurve(self):
        results = {}

        analysis = GrowthCurveAnalysis(self.catchment, self.gauged_catchments, results_log=results)
        gc = analysis.growth_curve()

        aeps = [0.5, 0.2, 0.1, 0.05, 0.03333, 0.02, 0.01333, 0.01, 0.005, 0.002, 0.001]
        growth_factors = gc(aeps)
        flows = growth_factors * self.qmed

        results['aeps'] = aeps
        results['growth_factors'] = growth_factors
        results['flows'] = flows
        self.results['gc'] = results


class MainFrame(wx.Frame):
  def __init__(self,parent):
      super(MainFrame, self).__init__(parent,title="Statistical Flood Estimation Tool",size=(600,600))

      # --- initialize other settings
      self.dirName = ""
      self.fileName = ""
      self.windowName = 'Main Window'
      self.SetName(self.windowName)
      
      c.analysis = Analysis()
      
      self.InitUI()
      self.Centre()
      self.Show()


  def InitUI(self):
        self.panel = wx.Panel(self,-1)
      
        menubar = wx.MenuBar()

        #  Defining the file menu
        fileMenu = wx.Menu()
        mN = wx.MenuItem(fileMenu, wx.ID_NEW, '&New\tCtrl+N')
        mO = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Open\tCtrl+O')
        mSA = wx.MenuItem(fileMenu, wx.ID_SAVEAS, '&Save as\tCtrl+ALT+S')
        mS = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.Append(mN)
        fileMenu.Append(mO)
        fileMenu.Append(mS)
        fileMenu.Append(mSA)
        fileMenu.AppendSeparator()
        mQ = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        fileMenu.Append(mQ)
        self.Bind(wx.EVT_MENU, self.OnNew, mN)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, mO)
        self.Bind(wx.EVT_MENU, self.OnFileSave, mS)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, mSA)
        self.Bind(wx.EVT_MENU, self.OnQuit, mQ)
 
        
        # Defining the help menu
        helpMenu = wx.Menu()
        mAbout = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About')
        helpMenu.Append(mAbout)
        self.Bind(wx.EVT_MENU, self.OnAbout, mAbout)
         
        # Applying menus to the menu bar
        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu,'&Help')


        self.SetMenuBar(menubar)


        # Here we create a notebook on the panel
        nb = wx.Notebook(self.panel)

        # create the page windows as children of the notebook
        self.page1 = FrontPage.Fpanel(nb,self)
        self.page2 = CatchmentDescriptors.Fpanel(nb,self.page1)
        self.page3 = QMED.Fpanel(nb,self.page2)
        #self.page4 = GrowthCurve.PoolingPanel(nb,self.page2,self.page3)
        #self.page4 = GrowthCurve.MainPanel(nb,self.page2,self.page3)
        #self.page5 = Summary.Fpanel(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(self.page1, "Overview")
        nb.AddPage(self.page2, "CDS")
        nb.AddPage(self.page3, "QMED")
        #nb.AddPage(self.page4, "FGC")
        #nb.AddPage(self.page5, "Summary")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        

        self.panel.Layout()
        self.Layout()
        self.Refresh()
    
  def OnPageChanging(self,e):
      #self.Refresh()
      #self.Update()
      e.Skip()
      
  def OnPageChanged(self,e):
      #self.page2.title_label.SetLabel(str(self.page1.title.GetValue()))
      #self.Refresh()
      #self.Update()
      e.Skip() 
        

  def OnAbout(self, e):
        
        description = """        The Statistical Flood Estimation Tool is a means of implementing current statistical
        procedures for estimating the magnitude of flood flows in the United Kingdom using the methods 
        detailed in the Flood Estimation Handbook and subsequent updates.  It has been developed by the not
        for profit Open Hydrology (OH) community of software developers.  The software makes extensive use 
        of the floodestimation library which is also developed by OH.
        
        This is an early development version, it is intended that additional features will be implemented in 
        the coming months and years.
        
        
"""

        licence = """The Statistical Flood Estimation Tool is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

The Statistical Flood Estimation Tool is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA

EXCEPTION CLAUSE:

A. Organisations (commercial, academic, educational, private individual or
  any other body) must publicly state via this software project's website
  that they have undertaken a validation process of this software prior to 
  its use.  In submitting their public declaration, organisations should 
  provide details of the findings of their review including any caveats or
  exclusions of use.  Organisations must record errors or bugs they find within
  the project's online issue tracking system within its GitHub repository. 
  This exclusion of use permits reasonable use of the software by organisations
  for testing and validation.
  
  Software project website:
  https://github.com/OpenHydrology/StatisticalFloodEstimationTool/wiki


"""

        info = wx.adv.AboutDialogInfo()

        info.SetIcon(wx.Icon('..\\art\\OH.darkgrey.250x250.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Statistical Flood Estimation Tool')
        info.SetVersion('Pre-release 0.0.2')
        info.SetDescription(description)
        info.SetCopyright('(C) 2015 Open Hydrology developer community')
        info.SetWebSite('https://github.com/OpenHydrology/StatisticalFloodEstimationTool')
        info.SetLicence(licence)
        info.AddDeveloper('Neil Nutt - Project Founder - neilnutt[at]googlemail[dot]com')
        info.AddDeveloper('\nFlorenz Hollebrandse - Developer - f.a.p.hollebrandse[at]protonmail[dot]ch')
        info.AddDeveloper('\nMichael Spencer - Communications - spencer.mike.r[at]gmail[dot]com')

        wx.adv.AboutBox(info)

  def OnPreferences(self,e):
      '''
      Load up preferences screen
      '''
      import Preferences
      
      Preferences.PreferencesFrame(self).Show()

      self.Refresh()
      self.Update()   


  def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Project directory (*.ini)|*.ini;*.hyd|Project archive|*.ini;*.hyd", wx.FD_OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
        filePath=os.path.join(self.dirName,self.fileName)
        load_project(filePath,self)


        dlg.Destroy()

#---------------------------------------
  def OnFileSave(self, e):
        """ File|Save event - Just Save it if it's got a name. """

        if (self.fileName != "") and (self.dirName != ""):
          saveFile = os.path.join(self.dirName,self.fileName)
          save_project(self,c.analysis.catchment,saveFile)

        else:
            ### - If no name yet, then use the OnFileSaveAs to get name/directory
            return self.OnFileSaveAs(e)

#---------------------------------------
  def OnFileSaveAs(self, e):
        """ File|SaveAs event - Prompt for File Name. """
        ret = False
        dlg = wx.FileDialog(self, "Save As", self.dirName, self.fileName,
                           "Files (*.hyd)|*.hyd|All Files|*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            ### - Use the OnFileSave to save the file
            if self.OnFileSave(e):
                self.SetTitle(self.fileName)
                ret = True
        dlg.Destroy()
        return ret

  def OnNew(self,e):
      pass

  
        
  def OnQuit(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()



if __name__ == "__main__":
    app = wx.App(redirect=False)
    #app = wx.App(redirect=True,filename='error_log.txt')
    MainFrame(None).Show()
    app.MainLoop()
