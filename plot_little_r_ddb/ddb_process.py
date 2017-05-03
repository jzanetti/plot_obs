from OBS2r import ddb, s3_download
from AMPSAws import utils, connections
import time
import datetime
from collections import defaultdict
import numpy

FIELDS_TO_GET = ['obs_id', 'report_type_geohash','datetime',
                 'latitude','longitude','pressure','pressureReducedToMeanSeaLevel',
                 'airTemperature','dewPointTemperature','windDirection','windSpeed']
def get_client_retry():
    """ Indefinitely try to get an Amazon client. """
    #may need backoff algorithm??
    conv = utils.get_conventions('research')
    keys_path = conv['research']['kelburn']['path_to_iam_keys']
    try:
        client = connections.get_client(
            'dynamodb', status='research', region_name='us-west-2',
            role_name='amps-research-observer', keys_path=keys_path)
    except:
        time.sleep(10)
        client = get_client_retry()
    return client

def get_ddb_row(valid_from,valid_to,north,south,west,east):
    ddb_row_out = {}
    table_name = "research_observations_recent"
    ddbrow_list = []
    client = get_client_retry()
    valid_from = datetime.datetime.strptime(valid_from, "%y%m%d%H")
    valid_to = datetime.datetime.strptime(valid_to, "%y%m%d%H")
    
    for data_type in ['synop']:
        ddb.return_obsdata_from_query(client,FIELDS_TO_GET, ddbrow_list,
                                      data_type, table_name,
                                      valid_from, valid_to,
                                      north, south, west, east)
 
    ddb_var_table = [('airTemperature','temperature'),
               ('dewpointTemperature','dew_point'),
               ('windDirection','direction'),
               ('windSpeed','speed')]
    
    ddb_row_out = defaultdict(list)

    for ddbrow in ddbrow_list:
        ddbrow = s3_download.row_postprocess(ddbrow)
            
        for ddb_var, req_key in ddb_var_table:
            
            if (ddb_var in ddbrow.keys()) == False:
                ddb_row_out[req_key].append(-888888.0)
            else:
                ddb_row_out[req_key].append(float(ddbrow[ddb_var]))
                                        
        ddb_row_out['latitude'].append(float(ddbrow['latitude']))
        ddb_row_out['longitude'].append(float(ddbrow['longitude']))
    
    ddb_row_out = dict(ddb_row_out)
    ddb_row_out2 = {}
    
    for ck in ddb_row_out.keys():
        p = ddb_row_out[ck];
        ddb_row_out2[ck] = numpy.asarray(p)
    
    
    return ddb_row_out2
    
    
