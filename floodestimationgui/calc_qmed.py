from floodestimation.loaders import load_catchment
from floodestimation import db
from floodestimation.collections import CatchmentCollections
from floodestimation.analysis import QmedAnalysis

db_session = db.Session()

dee_catchment = load_catchment('nith_cds.cd3')
gauged_catchments = CatchmentCollections(db_session)

qmed_analysis = QmedAnalysis(dee_catchment, gauged_catchments)
print(qmed_analysis.qmed())

print(qmed_analysis.methods)

print(qmed_analysis.qmed_all_methods())

print(qmed_analysis.urban_adj_factor())

print(qmed_analysis.find_donor_catchments(5, 200.0))

qmed_analysis.idw_power = 1.5
print(qmed_analysis.idw_power)

donors = qmed_analysis.find_donor_catchments(5, 200.0)



for donor in donors:
  Q = QmedAnalysis(donors[0], gauged_catchments)
  print(donor,qmed_analysis._error_correlation(donor),Q.qmed_all_methods())
db_session.close()
