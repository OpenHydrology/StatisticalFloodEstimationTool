# Copyright (c) 2014  Neil Nutt <neilnutt[at]googlemail.com>
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

from floodestimation import parsers
from floodestimation.entities import Catchment, Descriptors
from floodestimation.loaders import load_catchment
from configobj import ConfigObj
import os.path
from os import environ,rename,unlink
import shutil
from time import ctime
import config

'''
EXAMPLE USAGE:

from floodestimation.entities import Catchment, Descriptors
import project_file

catchment = Catchment("River Town", "River Burn")
catchment.descriptors = Descriptors(dtm_area=10, bfihost=0.50, sprhost=50, saar=1000, farl=1, urbext=0)
catchment.channel_width=2.0


filename = "C:/Temp/rtown study.zip"

gui_data_obj = gui_data.Store() # A gui_data_obj will hold all modeller notes and decisions etc
# The following would be set by the gui
gui_data_obj.catchment_description = 'A ficticious catchment far far away.'
gui_data_obj.cds_comments['saar']='Manually adjusted using gauge data.'
gui_data_obj.cds_comments['dtm_area']='Based on a wild guess.'

project_file.save_project(catchment,filename,gui_data_obj)
loaded_catchment,gui_data_obj = project_file.load_project(filename)
'''


def save_project(self,catchment_obj,project_filename,makeArchive):
  '''
  Saves the contents of the catchment object and gui object to a project archive
  :param catchment,filename
  :type catchment object,string,gui data object
  :return: None
  :rtype: None  
  '''
  fname = os.path.basename(project_filename).split('.')[0]
  tempdir = os.path.join(os.path.split(project_filename)[0],fname)
  
  if os.path.isdir(tempdir) is False:
    os.makedirs(tempdir)
  else:
    print("Temp directory exists, exiting")
    
  
  config = ConfigObj()
  config.filename = os.path.join(tempdir,fname+".ini")
  
  config['Version'] = '0.0.2'
  config['Date saved'] = ctime()
  config['User']= environ['USERNAME']
  config['Catchment_name'] = catchment_obj
  
  config['File paths']={}
  config['File paths']['ini_file'] = fname+".ini"
  cdsFile = os.path.join(tempdir,fname+".cd3")
  config['File paths']['cds_file'] = fname+".cd3"
  write_cds_file(catchment_obj,cdsFile)
  
  if len(catchment_obj.amax_records) != 0:
    amFile = os.path.join(tempdir,fname+".am")
    config['File paths']['am_file'] = fname+".am"
    write_am_file(catchment_obj,amFile)
  else:
    config['File paths']['am_file']=None
  
  if catchment_obj is None:
    config['File paths']['pot_file'] = fname+".pt"
  else:
    config['File paths']['pot_file'] = None
  config['File paths']['markdown_analysis_report']=None
  config['File paths']['checksum'] = None
  
  config['Supplementary information']={}
  config['Supplementary information']['purpose']=str(self.page1.purpose.GetValue())
  config['Supplementary information']['authors_notes']=str(self.page1.author_notes.GetValue())
  config['Supplementary information']['author_signature']=str(self.page1.author_signature.GetValue())
  config['Supplementary information']['checkers_notes']=str(self.page1.checkers_notes.GetValue())
  config['Supplementary information']['checker_signature']=str(self.page1.checker_signature.GetValue())
  config['Supplementary information']['cds_notes'] = self.page2.cds_notes.GetValue()


  config['Analysis']={}
  config['Analysis']['qmed']={}
  config['Analysis']['qmed']['comment']=self.page3.qmed_notes.GetValue()
  config['Analysis']['qmed']['user_supplied_qmed'] = self.page3.qmed_user.GetValue()
  config['Analysis']['qmed']['estimate_method']=self.page3.qmed_method
  config['Analysis']['qmed']['donor_station_limit']=self.page3.station_limit.GetValue()
  config['Analysis']['qmed']['donor_search_limit']=self.page3.station_search_distance.GetValue()
  config['Analysis']['qmed']['donor_method']='default'
  config['Analysis']['qmed']['idw_weight']=self.page3.idw_weight.GetValue()  
  config['Analysis']['qmed']['donors']=self.page3.adopted_donors
  config['Analysis']['qmed']['keep_rural']=self.page3.keep_rural
  config['Analysis']['qmed']['urban_method']='default'
  
  config['Analysis']['fgc']={}
  config['Analysis']['fgc']['comment']=''
  config['Analysis']['fgc']['adopted']='fgc1'
  config['Analysis']['fgc']['fgc1']={}
  config['Analysis']['fgc']['fgc1']['comment']=''
  config['Analysis']['fgc']['fgc1']['method']='pooling'
  config['Analysis']['fgc']['fgc1']['pooling_group']=[1001,1002]
  config['Analysis']['fgc']['fgc1']['weighting_method']='default'
  config['Analysis']['fgc']['fgc2']={}
  config['Analysis']['fgc']['fgc2']['comment']=''
  config['Analysis']['fgc']['fgc2']['method']='fssr14'
  config['Analysis']['fgc']['fgc2']['hydrological_region']=1

  config.write()

  if makeArchive:
    zipToArchive(tempdir,project_filename)

def zipToArchive(tempdir,project_filename):
  if os.path.isfile(project_filename):
    os.unlink(project_filename)
  shutil.make_archive(tempdir,"zip",tempdir)
  shutil.rmtree(tempdir)
  if tempdir+'.zip' != project_filename:
    os.rename(tempdir+'.zip', project_filename)

def write_cds_file(catchment_obj,fname):
  '''
  '''
  cds = catchment_obj.descriptors
  boolean_map = {}
  boolean_map[True]='YES'
  boolean_map[False]='NO'
  boolean_map[None]='NA'
  
  f = open(fname,'w')
  f.write('[FILE FORMAT]\nTYPE,CD3\nVERSION,3.0\n[END]\n')
  f.write('[STATION NUMBER]\n'+str(catchment_obj.id)+'\n[END]\n')
  f.write('[CDS DETAILS]\nNAME,'+str(catchment_obj.watercourse)+'\nLOCATION,'+str(catchment_obj.location))
  f.write('\nNOMINAL AREA,'+str(catchment_obj.area)+'\nNOMINAL NGR,'+str(catchment_obj.point_x)+','+str(catchment_obj.point_y)+'\n[END]\n')
  
  f.write('[DESCRIPTORS]\n')
  f.write('IHDTM NGR,'+str(catchment_obj.country).upper()+','+str(cds.ihdtm_ngr_x)+','+str(cds.ihdtm_ngr_y)+'\n')
  f.write('CENTROID NGR,'+str(catchment_obj.country).upper()+','+str(cds.centroid_ngr_x)+','+str(cds.centroid_ngr_y)+'\n')
  f.write('DTM AREA,'+str(cds.dtm_area)+'\n')
  f.write('ALTBAR,'+str(cds.altbar)+'\n')
  f.write('ASPBAR,'+str(cds.aspbar)+'\n')
  f.write('BFIHOST,'+str(cds.bfihost)+'\n')
  f.write('CHANNEL WIDTH,'+str(catchment_obj.channel_width)+'\n')
  f.write('DPLBAR,'+str(cds.dplbar)+'\n')
  f.write('DPSBAR,'+str(cds.dpsbar)+'\n')
  f.write('FARL,'+str(cds.farl)+'\n')
  f.write('FPEXT,'+str(cds.fpext)+'\n')
  f.write('LDP,'+str(cds.ldp)+'\n')
  f.write('PROPWET,'+str(cds.propwet)+'\n')
  f.write('RMED-1H,'+str(cds.rmed_1h)+'\n')
  f.write('RMED-1D,'+str(cds.rmed_1d)+'\n')
  f.write('RMED-2D,'+str(cds.rmed_2d)+'\n')
  f.write('SAAR,'+str(cds.saar)+'\n')
  f.write('SAAR4170,'+str(cds.saar4170)+'\n')
  f.write('SPRHOST,'+str(cds.sprhost)+'\n')
  f.write('URBCONC1990,'+str(cds.urbconc1990)+'\n')
  f.write('URBEXT1990,'+str(cds.urbext1990)+'\n')
  f.write('URBLOC1990,'+str(cds.urbloc1990)+'\n')
  f.write('URBCONC2000,'+str(cds.urbconc2000)+'\n')
  f.write('URBEXT2000,'+str(cds.urbext2000)+'\n')
  f.write('URBLOC2000,'+str(cds.urbloc2000)+'\n')
  f.write('[END]\n')
  
  f.write('[SUITABILITY]\n')
  f.write('QMED,'+boolean_map[catchment_obj.is_suitable_for_qmed]+'\n')
  f.write('POOLING,'+boolean_map[catchment_obj.is_suitable_for_pooling]+'\n')
  f.write('[END]\n')
  
  f.write('[COMMENTS]\n')
  for comment in catchment_obj.comments:
    f.write(str(comment.title).upper()+',')
    f.write(str(comment.content)+'\n')
  f.write('[END]\n')
  
  f.close()
  
  f = open(fname,'r')
  lines = f.read()
  f.close()
  lines = lines.replace(',None\n',',-9.999\n')
  f = open(fname,'w')
  f.write(lines)
  f.close()
  
  
def write_am_file(catchment_obj,fname):
  f = open(fname,'w')
  
  month_lookup = dict()
  month_lookup[1]='Jan'
  month_lookup[10]='Oct'
  
  f.write('[STATION NUMBER]\n')
  f.write(str(catchment_obj.id)+'\n')
  f.write('[END]\n')
  f.write('[AM Details]\n')
  f.write('Year Type,Water Year,'+month_lookup[catchment_obj.amax_records[0].WATER_YEAR_FIRST_MONTH]+'\n')
  f.write('[END]\n')
  
  
  rejected_yrs = ''
  for amax_record in catchment_obj.amax_records:
    if amax_record.flag == 2:
      rejected_yrs = rejected_yrs +str(amax_record.water_year)+','+str(amax_record.water_year)+','
  if rejected_yrs.endswith(','):
    f.write('[AM Rejected]\n')
    rejected_yrs=rejected_yrs[:-1]
    f.write(rejected_yrs+'\n')
    f.write('[END]\n')
    
  f.write('[AM Values]\n')
  
  for amax_record in catchment_obj.amax_records:
    entry = amax_record.date.strftime('%d %b %Y')+', '+str(amax_record.flow)+', '+str(amax_record.stage)+'\n'
    f.write(entry)
  f.write('[END]\n')
  f.close()

def load_project(filename,self):
  '''
  Loads the contents of a project archive to a catchment object
  :param filename
  :type string
  :return: catchment
  :rtype: catchment object  
  '''
  
  
  if filename.endswith('.hyd'):
    directory = os.path.join(os.path.dirname(filename),os.path.basename(filename.split('.')[0]))
    header_fname = os.path.join(directory,os.path.basename(filename.split('.')[0]))
    shutil.unpack_archive(filename, directory, "zip")

    inifname = header_fname+".ini"

  else:
    inifname = filename[:-4]+'.ini'
    directory = os.path.split(filename)[0]

  inif = ConfigObj(inifname)
  cdsfname = os.path.join(directory,inif['File paths']['cds_file'])
  
  self.page2.inside_load=True
  self.page2.syncCdsTab(cdsfname)
  self.page2.inside_load=False
  
  self.page1.purpose.SetValue(inif['Supplementary information']['purpose'])
  self.page1.author_notes.SetValue(inif['Supplementary information']['authors_notes'])
  self.page1.checkers_notes.SetValue(inif['Supplementary information']['checkers_notes'])
  self.page1.author_signature.SetValue(inif['Supplementary information']['author_signature'])
  self.page1.checker_signature.SetValue(inif['Supplementary information']['checker_signature'])
  self.page2.cds_notes.SetValue(inif['Supplementary information']['cds_notes'])
  
  self.page3.qmed_notes.SetValue(inif['Analysis']['qmed']['comment'])
  self.page3.qmed_user.SetValue(inif['Analysis']['qmed']['user_supplied_qmed'])
  self.page3.qmed_method = inif['Analysis']['qmed']['estimate_method']
  self.page3.station_limit.SetValue(inif['Analysis']['qmed']['donor_station_limit'])
  self.page3.station_search_distance.SetValue(inif['Analysis']['qmed']['donor_search_limit'])
  self.page3.idw_weight.SetValue(inif['Analysis']['qmed']['idw_weight'])
  if inif['Analysis']['qmed']['keep_rural'].lower() == 'true':                                            
    self.page3.keep_rural= True
    self.page3.update_for_urb_chk.SetValue(False)
    self.page3.update_for_urbanisation = False
  else:
    self.page3.keep_rural= False
    self.page3.update_for_urb_chk.SetValue(True)
    self.page3.update_for_urbanisation = True


  
  if filename.endswith('.hyd'):  
    shutil.rmtree(directory)

