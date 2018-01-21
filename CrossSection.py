#!/usr/bin/env python

""" Creates and saves plots of vertical cross sections with matplotlib.
"""

import glob
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from netCDF4 import Dataset
from wrf import (getvar, to_np, vertcross, smooth2d, CoordPair, GeoBounds, get_cartopy,
                 latlon_coords)

___author___ = "Preston Wilson, modified from example code on http://wrf-python.readthedocs.io"

dir_list = raw_input("Enter directory to be evaluated: ")  # example: wrf\* for all files in wrf directory on Windows OS
new_dir_list = dir_list.split('\\')
if not os.path.exists('UpdatedPlots_' + new_dir_list[len(new_dir_list) - 2] + '/'):
                os.makedirs('UpdatedPlots_' + new_dir_list[len(new_dir_list) - 2] + '/')
for wrffile in glob.iglob(dir_list):
    if fnmatch.fnmatch(wrffile, '[wrf]*'):
        print "Evaluating file " + wrffile
        ncfile = Dataset(wrffile)

        # Get the WRF variables
        slp = getvar(ncfile, "slp")
        smooth_slp = smooth2d(slp, 3)
        ctt = getvar(ncfile, "ctt")
        z = getvar(ncfile, "z")
        dbz = getvar(ncfile, "dbz")
        Z = 10**(dbz/10.)
        wspd = getvar(ncfile, "wspd_wdir", units="kt")[0,:]

        # Set the start point and end point for the cross section
        start_point = CoordPair(lat=36.99464, lon=-82.37988)
        end_point = CoordPair(lat=35.53535, lon=-81.08899)  # For some reason -81.08899 as the y-endpoint gives an error

        # Compute the vertical cross-section interpolation.  Also, include the lat/lon
        # points along the cross-section in the metadata by setting latlon to True.
        z_cross = vertcross(Z, z, wrfin=ncfile, start_point=start_point, end_point=end_point,
                            latlon=True, meta=True)
        wspd_cross = vertcross(wspd, z, wrfin=ncfile, start_point=start_point, end_point=end_point,
                               latlon=True, meta=True)
        dbz_cross = 10.0 * np.log10(z_cross)

        # Get the lat/lon points
        lats, lons = latlon_coords(slp)

        # Get the cartopy projection object
        cart_proj = get_cartopy(slp)

        # Create a figure that will have 3 subplots
        fig = plt.figure(figsize=(10,7))

        # Initially had 3 suplots, changed so only wind speed is shown
        ax_wspd = fig.add_subplot(1,1,1)

        # Make the pressure contours
        contour_levels = [960, 965, 970, 975, 980, 990]

        # Create the filled cloud top temperature contours
        contour_levels = [-80.0, -70.0, -60, -50, -40, -30, -20, -10, 0, 10]

        # Crop the domain to the region around the hurricane
        hur_bounds = GeoBounds(CoordPair(lat=np.amin(to_np(lats)), lon=-85.0),
                               CoordPair(lat=30.0, lon=-72.0))

        # Make the contour plot for wind speed
        wspd_contours = ax_wspd.contourf(to_np(wspd_cross), cmap=get_cmap("jet"))
        # Add the color bar
        cb_wspd = fig.colorbar(wspd_contours, ax=ax_wspd)
        cb_wspd.ax.tick_params(labelsize=7)

        # Make the contour plot for dbz
        levels = [5 + 5*n for n in range(15)]

        # Set the x-ticks to use latitude and longitude labels
        coord_pairs = to_np(dbz_cross.coords["xy_loc"])
        x_ticks = np.arange(coord_pairs.shape[0])
        x_labels = [pair.latlon_str() for pair in to_np(coord_pairs)]
        ax_wspd.set_xticks(x_ticks[::20])
        ax_wspd.set_xticklabels([], rotation=45)

        # Set the y-ticks to be height
        vert_vals = to_np(dbz_cross.coords["vertical"])

        # My quick attempt at making max height 15000; I think it works, but it messes up the y-axis labels and ticks
        # Commented out for now
        # vert_vals.flatten()
        # vert_vals = [i for i in vert_vals if i < 15000]

        v_ticks = np.arange(vert_vals.shape[0])
        ax_wspd.set_yticks(v_ticks[::20])
        ax_wspd.set_yticklabels(vert_vals[::20], fontsize=7)

        # Set the x-axis and  y-axis labels
        ax_wspd.set_ylabel("Height (m)", fontsize=7)


        try:
            # Add a title
            ax_wspd.set_title("Cross-Section of Wind Speed (kt)", {"fontsize": 8})
            fin_name = wrffile.split('\\')
            plt.savefig('UpdatedPlots_' + new_dir_list[len(new_dir_list) - 2] + '/' +
                        fin_name[len(fin_name) - 1] + '_plot.png')
        except Exception as e:
            print "Error: " + e



