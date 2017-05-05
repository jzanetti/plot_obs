from OBS2r import ddb, s3_download
import time
import datetime
from collections import defaultdict
import numpy

FIELDS_TO_GET = ['obs_id', 'report_type_geohash','datetime',
                 'latitude','longitude','pressure','pressureReducedToMeanSeaLevel',
                 'airTemperature','dewPointTemperature','dewpointTemperature','windDirection','windSpeed']

def get_ddb_row(client,obs_type,valid_from,valid_to,north,south,west,east):
    ddb_row_out = {}
    table_name = "research_observations_recent"
    ddbrow_list = []
    valid_from = datetime.datetime.strptime(valid_from, "%y%m%d%H")
    valid_to = datetime.datetime.strptime(valid_to, "%y%m%d%H")
    
    obs_length = {}
    
    for data_type in obs_type:
        ddb.return_obsdata_from_query(client,FIELDS_TO_GET, ddbrow_list,
                                      data_type, table_name,
                                      valid_from, valid_to,
                                      north, south, west, east)
        
    ddb_var_table = [('airTemperature','temperature'),
               ('dewPointTemperature','dew_point'),
               ('windDirection','direction'),
               ('windSpeed','speed')]
    
    ddb_row_out = defaultdict(list)

    for ddbrow in ddbrow_list:
        ddbrow = s3_download.row_postprocess(ddbrow)
        ddbrow_keys = [str(r) for r in ddbrow.keys()]
        for ddb_var, req_key in ddb_var_table:
            if (ddb_var.upper() in map(str.upper, ddbrow_keys)) == False:
                ddb_row_out[req_key].append(-888888.0)
            else:
                for ckey in ddbrow.keys():
                    if ckey.upper() == ddb_var.upper():
                        ddb_row_out[req_key].append(float(ddbrow[ckey]))
                
                                        
        ddb_row_out['latitude'].append(float(ddbrow['latitude']))
        ddb_row_out['longitude'].append(float(ddbrow['longitude']))
    
    ddb_row_out = dict(ddb_row_out)
    ddb_row_out2 = {}
    
    for ck in ddb_row_out.keys():
        p = ddb_row_out[ck];
        ddb_row_out2[ck] = numpy.asarray(p)
    
    
    return ddb_row_out2
    
    
