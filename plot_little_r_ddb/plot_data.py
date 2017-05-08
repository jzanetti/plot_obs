#!/home/szhang/Programs/anaconda2/envs/obs2aws-dev/bin/python

from optparse import OptionParser
import data_processing

"""PLottong the observation distribution for little_r and dynamodb"""

def base_parser():
    """Enables options common to obs2littl_r.py and plot_little_r.py"""
    parser = OptionParser()
    parser.add_option('-l', '--little_r', dest='little_r',
                        help="plot from little_r",
                        action='store_true')
    parser.add_option('-b', '--ddb', dest='ddb',
                        help="plot from ddb",
                        action='store_true')
    parser.add_option(
        "-s", "--start", type="string", dest="start",
        help="start of desired time window YYMMDDHH (compulsory)")
    parser.add_option("-e", "--end", type="string", dest="end",
                      help="end of desired time window YYMMDDHH (optional)")
    parser.add_option(
        "-w", "--interval", type="float", dest="interval",
        help="interval of output (in hrs)")
    parser.add_option(
        "-o", '--observation_type', type="string", dest='observation_type',
        help="observation type to plot (any valid little_r data record field)",
        action='append', default=[])
    parser.add_option(
        "-v", '--variable', type="string", dest='variables',
        help="variable to plot (any valid little_r data record field)",
        action='append', default=[])
    parser.add_option(
        "-m", "--map", type="string", dest="map",
        help=" string corresponding to a predefined domain in " +
        "pycast.wrf_basemap_params (.i.e nz12kmN_d1).  This " +
        "determines the valid spatial range of observations.")
    return parser

if __name__ == '__main__':
    parser = base_parser()
    parser.add_option('-f', '--little_r_file', type=str,
                        help="little_r file")
    parser.add_option('-p', '--image_directory', type=str,
                        help="image_directory")
    parser.add_option(
        "--scale", type="float", dest="scale",
        help="scale argument for quiver function (default None(autoscaling))")
    parser.add_option('-q', '--quiver', help='Add wind quivers',
                      action="store_true", dest='do_quivers')
    parser.add_option('-r', '--barb', help='Add wind barbs', action="store_true",
                      dest='do_barbs')
    parser.add_option('-c', '--cylindrical',
                      help='Use a cylindrical equidistant projection',
                      action="store_true", dest='do_cylin')
    parser.add_option('-i', '--id', help='draw station id labels',
                      action="store_true", dest='show_ids')
    parser.add_option('-t', '--text-values', help='draw text values',
                      action="store_true", dest='show_values')
    parser.add_option('-n', '--no-scatter', help='do not draw the scatter plot',
                      action="store_true", dest='no_scatter')
    parser.add_option("-d", "--dpi", type="int", dest="dpi",
                      help="dpi for output image", default=100)
    parser.add_option('--interactive', dest='interactive', action="store_true",
                      help="show plots in interactive windows")
    
    #(options, args)  = parser.parse_args(['-l','-f','/home/szhang/workspace/obs2r_debug/all.little_r',\
    #                                      '-p','/home/szhang/workspace/plot_little_r_ddb/figure_little_r',\
    #                                      '-o','synop' , '-o', 'metar', \
    #                                      '-v','temperature', \
    #                                      '-s', '17042823', '-e', '17042901', '-w', '1',\
    #                                      '-m' 'nz4kmN_d2','--id'])
    #(options, args) = parser.parse_args(['-b','-p','/home/szhang/workspace/plot_little_r_ddb/figure2', \
    #                                     '-o','metar','-o','synop','-o', 'ship','-o','buoy',\
    #                                     '-v','dew_point', '-v','temperature', '-v', 'speed',\
    #                                     '-s', '17050609', '-e', '17050710', '-w', '3',\
    #                                     '-m' 'nz4kmN_d2','--id'])
    
    (options, args) = parser.parse_args()
    if options.little_r == True:
        data_processing.little_r_plot(options)
    elif options.ddb == True:
        data_processing.ddb_plot(options)
    else:
        print '** For little_r plot: python plot_data.py -l -f all.little_r -p figure_dir -o synop -o metar -v temperature -s 17042823 -e 17050201 -w 1 -m nz4kmN_d2 --id'
        print '** For ddb plot:      python plot_data.py -b -p figure_dir -o metar -o synop -o ship -o buoy -v dew_point -v temperature -v speed -s 17050609 -e 17050710 -w 3 -m nz4kmN_d2 --id'
    
    print 'done'

