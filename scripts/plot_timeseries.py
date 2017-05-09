import pickle
import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

"""
This program is used to produce offline time series plot for observations:
Inputs: pickle data produced by plot_data.py
     * var: the variable you want to plot (either temperature, dew_point or speed)
     * station_list: e.g., ['AAAA','BBBB']
     * plot_color: corresponds to station list (must has the same lenth), e.g., ['k--','r.']
     * xtick_interval: how frequent you want to tick the x-axis
     * start/end datetime: YYYYMMDDHHMMSS
     * time_interval: how frequent you want to plot the data
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

if __name__ == '__main__':
    var = 'speed'
    station_list = ['93800_synop','93805_synop','93909_synop','93891_synop','93845_synop','93831_synop','93709_synop']
    plot_color = ['k','k.-','k--','r.','g.','b.','m.','y.']
    xtick_interval = 3
    start_datetime = '20170506010000'
    end_datetime = '20170509000000'
    time_interval = 1
    
    datetime_out_list,datetime_out_list2 = return_timerange(start_datetime,end_datetime,time_interval)
    
    fdata = defaultdict( lambda: defaultdict(lambda: defaultdict( int )))

    pickle_datapath = '/home/szhang/workspace/plot_little_r_ddb/data2/' + var + '.p';
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
    
    for station in station_list:
        plt.plot(fdata[station][var]['value'],plot_color[station_list.index(station)],label=station)
    
    plt.legend()
    plt.ylabel(var)
    plt.xticks(rotation=70)
    plt.xticks(range(0,len(datetime_out_list),xtick_interval), datetime_out_list2[0:len(datetime_out_list):xtick_interval], color='k')
    plt.grid()
    plt.title(var + ', ' + start_datetime + '-' + end_datetime)
    plt.show()
    
                