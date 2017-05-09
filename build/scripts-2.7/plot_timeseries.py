import pickle
import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from pycast.wrf_basemap_params import WRF_BASEMAP_PARAMS
import copy
from plot_obs import data_processing,ddb_process
import os
import numpy
from OBS2r import little_r

"""
This program is used to produce offline time series plot for observations:
     * var: the variable you want to plot (either temperature, dew_point or speed)
     * obs_type: e.g., synop, metar etc.
     * station_list: e.g., ['AAAA','BBBB']
     * plot_color: corresponds to station list (must has the same lenth), e.g., ['k--','r.']
     * xtick_interval: how frequent you want to tick the x-axis
     * start/end datetime: YYYYMMDDHHMMSS
     * time_interval: how frequent you want to plot the data

  Currently we gather all data ant write data into pickle, and 
  then read data from pickle for plotting
"""



def return_timerange(start_datetime_str,end_datetime_str,time_interval):
    start_datetime = datetime.datetime.strptime(start_datetime_str,'%Y%m%d%H%M%S')
    end_datetime = datetime.datetime.strptime(end_datetime_str,'%Y%m%d%H%M%S')
    datetime_out_str = []
    datetime_out_str2 = []
    cdatetime = start_datetime
    while cdatetime <= end_datetime:
        datetime_out_str.append(cdatetime.strftime('%Y%m%d%H%M%S'))
        datetime_out_str2.append(cdatetime.strftime('%y%m%d%H'))
        cdatetime = cdatetime + datetime.timedelta(seconds = time_interval*3600)
    return datetime_out_str,datetime_out_str2

def write_pickle(data,ddir,var_list):
    import pickle

    if os.path.exists(ddir) == False:
        os.makedirs(ddir)
    
    for var in var_list:
        if os.path.exists(ddir + '/' + var + '.p'):
            open_new = False
            sdata = pickle.load(open(ddir + '/' + var + '.p', "rb"))
        else:
            open_new = True
            sdata = []
        if len(data) > 0:
            wanted = numpy.nonzero(data[var] > little_r.LittleRReport.missing)[0]
            z = data[var][wanted]
            for i in range(len(wanted)):
                label = data['id'][wanted[i]]
                obs_v = z[i]
                obs_t = data['datetime'][wanted[i]]
                if ((label,obs_t,obs_v) in sdata) == False:
                    sdata.append((label,obs_t,obs_v))
            pickle.dump(sdata, open(ddir + '/' + var + '.p', "wb"))

def return_data(data_map,start_datetime,end_datetime,observation_type,time_interval,ddir,var_list):
    BASEMAP, params = data_processing.set_basemap(data_map, 'c')
    client = data_processing.get_client_retry()
    first_datetime = datetime.datetime.strptime(start_datetime, "%Y%m%d%H%M%S")
    last_datetime = datetime.datetime.strptime(end_datetime, "%Y%m%d%H%M%S")
    cdatetime = first_datetime
    while cdatetime < last_datetime:
        print '   ---' + cdatetime.strftime('%Y%m%dT%H:%M')
        for c_observation_type in observation_type:
            cdatetime_str = cdatetime.strftime('%y%m%d%H')
            cdatetime_str1 = (cdatetime + datetime.timedelta(seconds=time_interval*3599)).strftime('%y%m%d%H')
            data = ddb_process.get_ddb_row(client, [c_observation_type] ,cdatetime_str, cdatetime_str1, params.urcrnrlat, params.llcrnrlat, params.llcrnrlon, params.urcrnrlon)
            if len(data) == 0:
                print '   * no data available'
            write_pickle(data,ddir,var_list)
        cdatetime = cdatetime + datetime.timedelta(seconds=time_interval*3600)

if __name__ == '__main__':
    var = 'speed'
    obs_type = 'synop'
    station_list = ['93800_synop','93805_synop','93909_synop','93891_synop','93845_synop','93831_synop','93709_synop']
    plot_color = ['k','k.-','k--','r.','g.','b.','m.','y.']
    xtick_interval = 3
    start_datetime = '20170503010000'
    end_datetime = '20170509010000'
    time_interval = 1
    pickle_data_dir = '/home/szhang/workspace/plot_little_r_ddb'
    
    print '1. pickle job'
    return_data('nz4kmN_d2',start_datetime,end_datetime,[obs_type],time_interval,pickle_data_dir,[var]);
    
    print '2. return required datetime'
    datetime_out_list,datetime_out_list2 = return_timerange(start_datetime,end_datetime,time_interval)
    
    
    print '3. sort out data'
    fdata = defaultdict( lambda: defaultdict(lambda: defaultdict( int )))

    pickle_datapath = pickle_data_dir + '/' + var + '.p';
    data = pickle.load(open(pickle_datapath, "rb" ))
    for station in station_list:
        pdata = []
        ptime = []
        for cdate in datetime_out_list:
            mydata = None
            ptime.append(cdate)

            for cdata in data:
                if (cdata[0] == station) and (cdata[1] == cdate):
                    mydata = cdata[2]
            pdata.append(mydata)
                
        fdata[station][var]['value'] = pdata
        fdata[station][var]['time'] = ptime      
    
    print '4. plotting'
    for station in station_list:
        plt.plot(fdata[station][var]['value'],plot_color[station_list.index(station)],label=station)
    
    plt.legend()
    plt.ylabel(var)
    plt.xticks(rotation=70)
    plt.xticks(range(0,len(datetime_out_list),xtick_interval), datetime_out_list2[0:len(datetime_out_list):xtick_interval], color='k')
    plt.grid()
    plt.title(var + ', ' + start_datetime + '-' + end_datetime)
    plt.show()
    
                
