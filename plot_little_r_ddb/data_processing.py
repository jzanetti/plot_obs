import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as mc
from pycast.wrf_basemap_params import WRF_BASEMAP_PARAMS
from OBS2r import little_r
from pylab import *
import ddb_process
import datetime
import copy
from AMPSAws import utils, connections
import os
import numpy

def return_req_data(data,r_obstype):
    req_i = []
    for i in range(len(data['id'])):
        if r_obstype in data['id'][i]:
            req_i.append(i)
    
    req_data = {}
    for ckey in data.keys():
        req_data[ckey] = numpy.asarray([data[ckey][j] for j in req_i], dtype=data[ckey].dtype)
            
    return req_data

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

def set_basemap(map_key, resolution=None):
    """if map_key can be found in WRF_BASEMAP_PARAMS, return corresponding
    basemap.  Otherwise raise an Exception"""
    if map_key in WRF_BASEMAP_PARAMS:
        params = copy.deepcopy(WRF_BASEMAP_PARAMS[map_key])
        params.resolution = resolution
        return params.to_basemap(), params
    else:
        raise Exception(
            'the specified -/--map option (%s) does not ' % map_key +
            'correspond to an item in wrf_basemap_params.WRF_BASEMAP_PARAMS'
        )

def little_r_plot(options):
    BASEMAP, _ = set_basemap(options.map, 'c')
    first_datetime = datetime.datetime.strptime(options.start, "%y%m%d%H")
    last_datetime = datetime.datetime.strptime(options.end, "%y%m%d%H")
    
    cdatetime = first_datetime
    while cdatetime < last_datetime:
        print cdatetime
        for c_observation_type in options.observation_type:
            cdatetime_str = cdatetime.strftime('%y%m%d%H')
            cdatetime_str1 = (cdatetime + datetime.timedelta(seconds=options.interval*3599)).strftime('%y%m%d%H')
            data, (first_datetime2, last_datetime2) = little_r.extract(options.little_r_file, cdatetime_str,cdatetime_str1, bmap=BASEMAP)
            data = return_req_data(data,c_observation_type)
            data_plot(BASEMAP,c_observation_type,options,data,cdatetime,cdatetime + datetime.timedelta(seconds=options.interval*3599))
        cdatetime = cdatetime + datetime.timedelta(seconds=options.interval*3600)

def ddb_plot(options):
    BASEMAP, params = set_basemap(options.map, 'c')
    client = get_client_retry()
    
    first_datetime = datetime.datetime.strptime(options.start, "%y%m%d%H")
    last_datetime = datetime.datetime.strptime(options.end, "%y%m%d%H")
    
    cdatetime = first_datetime
    while cdatetime < last_datetime:
        print cdatetime
        for c_observation_type in options.observation_type:
            cdatetime_str = cdatetime.strftime('%y%m%d%H')
            cdatetime_str1 = (cdatetime + datetime.timedelta(seconds=options.interval*3599)).strftime('%y%m%d%H')
            data = ddb_process.get_ddb_row(client, [c_observation_type] ,cdatetime_str, cdatetime_str1, params.urcrnrlat, params.llcrnrlat, params.llcrnrlon, params.urcrnrlon)
            data_plot(BASEMAP,c_observation_type, options,data,cdatetime,cdatetime + datetime.timedelta(seconds=options.interval*3599))
        cdatetime = cdatetime + datetime.timedelta(seconds=options.interval*3600)

def data_plot(BASEMAP,c_observation_type, options,data,first_datetime,last_datetime):
    fignum = 1
    if options.do_quivers or options.do_barbs:
        wind_wanted = nonzero(
            (data['speed'] > little_r.LittleRReport.missing) *
            (data['direction'] > little_r.LittleRReport.missing))[0]
        u = -data['speed'][wind_wanted] * \
            sin(pi * data['direction'][wind_wanted] / 180)
        v = -data['speed'][wind_wanted] * \
            cos(pi * data['direction'][wind_wanted] / 180)
        x_q, y_q = BASEMAP(data['longitude'][wind_wanted],
                           data['latitude'][wind_wanted])
        cdict = {'red':  ((0., 0.6, 0.6), (0.1, 0., 0.), (0.2, 0., 0.), (0.3, 0., 0.),
                          (0.4, 0., 1.), (0.5, 1., 1.), (0.6,
                                                         1., 1.), (0.7, 1., 0.8),
                          (0.8, 0.2, 0.8), (0.9, 0.6, 0.6), (1., 0.2, 0.2)),
                 'green':  ((0., 0.6, 0.6), (0.1, 0., 1.), (0.2, 0.5, 0.5), (0.3, 0., 1.),
                            (0.4, 0.4, 1), (0.5, 0.8,
                                            0.6), (0.6, 0., 0.), (0.7, 0., 0.4),
                            (0.8, 0.2, 0.), (0.9, 0., 0.), (1., 0.2, 0.2)),
                 'blue':  ((0., 0.6, 0.6), (0.1, 0., 1.), (0.2, 1., 1.), (0.3, 1., 0.2),
                           (0.4, 0., 0.), (0.5, 0.2, 0.), (0.6,
                                                           0., 0.2), (0.7, 0., 0.2),
                           (0.8, 0., 0.8), (0.9, 0., 0.), (1., 0.2, 0.2))
                 }
        my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict)
    
    plots_to_show = False
    
    for var in options.variables:
        figure(fignum,figsize=(15,15))
        if not options.no_scatter:
            if len(data) > 0:
                wanted = nonzero(data[var] > little_r.LittleRReport.missing)[0]
                if len(wanted) == 0:
                    z = []
                    x = []
                    y = []
                else:
                    z = data[var][wanted]
                    x, y = BASEMAP(data['longitude'][wanted], data['latitude'][wanted])
            else:
                z = []
                x = []
                y = []
                wanted = []
                
            try:
                scatter_plot = BASEMAP.scatter(x, y, c=z, cmap=cm.jet, edgecolor=None)
                cb = colorbar(scatter_plot)
            except:
                traceback.print_exc()
        
        if options.do_quivers:
            quiver_plot = quiver(x_q, y_q, u, v, data[var][wind_wanted],
                                     scale=options.scale, cmap=my_cmap,
                                     norm=mc.Normalize(vmin=0, vmax=50))
        
        if options.do_barbs:
            barb_plot = barbs(x_q, y_q, u, v, data[var][wind_wanted], cmap=my_cmap,
                                  norm=mc.Normalize(vmin=0, vmax=50), length=5,
                                  linewidth=0.3)
        
        if options.show_ids:
            shownids = []
            for i in range(len(wanted)):
                label = data['id'][wanted[i]]
                if not label in shownids:
                    shownids.append(label)
                    text(x[i], y[i], label, verticalalignment='bottom')
        if options.show_values:
            for i in range(len(wanted)):
                text(x[i], y[i], '%.1f' % z[i], verticalalignment='top')
        
        if options.no_scatter:
            wanted = wind_wanted
            if options.do_quivers:
                cb = colorbar(quiver_plot, ticks=range(0, 51, 5))
            if options.do_barbs:
                cb = colorbar(barb_plot, ticks=range(0, 51, 5))
        
        if var == 'dew_point' or var == 'temperature':
            clim(265,290)
        elif var == 'speed':
            clim(0,25.0)
        
        BASEMAP.drawcoastlines()  # draw coastlines
        BASEMAP.drawparallels(arange(-80., 80, 20), labels=[1, 0, 0, 0])
        BASEMAP.drawmeridians(arange(-180, 180, 20), labels=[0, 0, 0, 1])
            
        fig_dir = options.image_directory + '/' + var + '/' + c_observation_type
        if os.path.exists(fig_dir) == False:
            os.makedirs(fig_dir)
            
        title('%s, %s (%s): %s - %s' % (var, c_observation_type, str(len(wanted)), first_datetime, last_datetime))
        #figtext(0.5, 0.02, '%d valid %s obs.' % (len(wanted), var),
        #                verticalalignment='bottom', horizontalalignment='center')
        savefig(fig_dir + '/' + '%s_%s_%s.png' % (var,first_datetime.strftime('%Y%m%dT%H%M'),last_datetime.strftime('%Y%m%dT%H%M')),bbox_inches='tight',)
        close()
        plots_to_show = False
    
    if plots_to_show:
        show()
