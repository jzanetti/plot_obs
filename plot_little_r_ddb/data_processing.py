import traceback
import matplotlib.colors as mc
from pycast.wrf_basemap_params import WRF_BASEMAP_PARAMS
from OBS2r import little_r
from pylab import *
import ddb_process
import datetime
import copy

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
    data, (first_datetime, last_datetime) = little_r.extract(options.little_r_file, options.start,options.end, bmap=BASEMAP)
    data_plot(BASEMAP,options,data,first_datetime,last_datetime)
    #data = ddb_process.get_ddb_row(data,options.start, options.end, -50.0, -40.0, 170.0, 185.0)

def ddb_plot(options):
    BASEMAP, params = set_basemap(options.map, 'c')
    data = ddb_process.get_ddb_row(options.start, options.end, params.urcrnrlat, params.llcrnrlat, params.llcrnrlon, params.urcrnrlon)
    first_datetime = datetime.datetime.strptime(options.start, "%y%m%d%H")
    last_datetime = datetime.datetime.strptime(options.end, "%y%m%d%H")
    data_plot(BASEMAP,options,data,first_datetime,last_datetime)

def data_plot(BASEMAP,options,data,first_datetime,last_datetime):
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
        figure(fignum)
        if not options.no_scatter:
            wanted = nonzero(data[var] > little_r.LittleRReport.missing)[0]
            if len(wanted) == 0:
                break
            z = data[var][wanted]
    
            x, y = BASEMAP(data['longitude'][wanted], data['latitude'][wanted])
            
            
            try:
                scatter_plot = BASEMAP.scatter(x, y, c=z, edgecolor=None)
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
    
        BASEMAP.drawcoastlines()  # draw coastlines
        BASEMAP.drawparallels(arange(-80., 80, 20), labels=[1, 0, 0, 0])
        BASEMAP.drawmeridians(arange(-180, 180, 20), labels=[0, 0, 0, 1])
    
        if not options.start is None:
            start = datetime.datetime.strptime(options.start, "%y%m%d%H")
        else:
            start = first_datetime
        if not options.end is None:
            end = datetime.datetime.strptime(options.end, "%y%m%d%H")
        else:
            end = last_datetime
        #title('%s, %s: %s - %s' % (args[0], var, start, end))
        title('%s: %s - %s' % (var, start, end))
        figtext(0.5, 0.02, '%d valid %s obs.' % (len(wanted), var),
                verticalalignment='bottom', horizontalalignment='center')
        #savefig('%s_%s.png' % (args[0], var), dpi=options.dpi)
        savefig('%s.png' % (var), dpi=options.dpi)
        plots_to_show = False
    
    if plots_to_show:
        show()
