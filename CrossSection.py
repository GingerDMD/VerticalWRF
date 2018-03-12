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
    print wrffile
    # checks for files that contain the string expression; if no error but  not creating plots, consider changing this
    # necessary check because if non-WRF files are present in the directory, it will try to plot them and break
    if fnmatch.fnmatch(wrffile, '*[wrf]*'):
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
        end_point = CoordPair(lat=35.53535, lon=-81.08899)
        end_point_zoom = CoordPair(lat=35.53535, lon=-81.08899)

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

        fig = plt.figure(figsize=(10, 10))

        ax_wspd = fig.add_subplot(2, 1, 1)
        ax_wspd_zoom = fig.add_subplot(2, 1, 2)

        # Make the contour plot for wind speed
        wspd_contours = ax_wspd.contourf(to_np(wspd_cross), cmap=get_cmap("jet"), levels=np.linspace(0, 64, 512))
        wspd_contours_zoom = ax_wspd_zoom.contourf(to_np(wspd_cross), cmap=get_cmap("hot"), levels=np.linspace(0, 64, 512))

        # Add the color bar
        cb_wspd = fig.colorbar(wspd_contours, ax=ax_wspd)
        cb_wspd_zoom = fig.colorbar(wspd_contours_zoom, ax=ax_wspd_zoom)

        # cb_wspd.locator = tick_locator
        cb_wspd.ax.tick_params(labelsize=7)
        cb_wspd_zoom.ax.tick_params(labelsize=7)

        # Make the contour plot for dbz
        levels = [5 + 5*n for n in range(15)]

        # Set the x-ticks to use latitude and longitude labels
        coord_pairs = to_np(dbz_cross.coords["xy_loc"])
        x_ticks = np.arange(coord_pairs.shape[0])
        x_labels = [pair.latlon_str() for pair in to_np(coord_pairs)]

        ax_wspd.set_xticks(x_ticks[::30])
        ax_wspd.set_xticklabels(x_labels[::30], fontsize=7, rotation=15)
        ax_wspd_zoom.set_xticks(x_ticks[::30])
        ax_wspd_zoom.set_xticklabels(x_labels[::30], fontsize=7, rotation=15)

        # Set the y-ticks to be height
        vert_vals = to_np(dbz_cross.coords["vertical"]).astype(int)
        print dbz_cross.coords["vertical"]

        v_ticks = np.arange(vert_vals.shape[0])
        v_ticks_zoom = np.arange(vert_vals.shape[0])
        ax_wspd.set_yticks(v_ticks[::10])  # every 10 ax_wspd values serve as tick mark
        ax_wspd.set_yticklabels(vert_vals[::10], fontsize=7)
        ax_wspd_zoom.set_yticks(v_ticks[::10])
        ax_wspd_zoom.set_yticklabels(vert_vals[::10], fontsize=7)

        # Set the x-axis and  y-axis labels
        ax_wspd.set_ylabel("Height (m)", fontsize=7)
        ax_wspd_zoom.set_ylabel("Height (m)", fontsize=7)

        try:
            # Add a title
            ax_wspd.set_title("Cross-Section of Wind Speed (kt)\n"
                              "SP: lat=36.99464, lon=-82.37988\n"
                              "EP: lat=35.53535, lon=-81.08899", {"fontsize": 10})
            # ax_wspd_zoom.set_title("Zoomed Cross-Section of Lower Elevation Wind Speed", {"fontsize": 8})
            fin_name = wrffile.split('\\')
            # plt.show()
            plt.savefig('UpdatedPlots_' + new_dir_list[len(new_dir_list) - 2] + '/' +
                        fin_name[len(fin_name) - 1] + '_plot.png')
        except Exception as e:
            print "Error: " + str(e)



