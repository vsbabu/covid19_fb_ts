import numpy as np
import pandas as pd
import calmap
from matplotlib import pyplot as plt

import sys
import argparse

argparser = argparse.ArgumentParser(description="Reads dt,value without header from stdin and prints a weekly folded html with anomalies", add_help=True)
argparser.add_argument("--time_format", "-t", help="Strftime pattern to parse (%y%m%d)")
argparser.add_argument("--output_prefix", "-o", help="Output prefix for graphs")

args = argparser.parse_args()

if not args.time_format:
    args.time_format = "%y%m%d"

df = pd.read_csv(sys.stdin, sep=",", header=None, squeeze=True)

df.columns = ['ds', 'active', 'confirmed', 'recovered', 'deceased']
# let us set ds as datetime index
df["ds"] = pd.to_datetime(df.ds, format=args.time_format)
df = df.set_index("ds")

## -- now comes the main part of making visualizations
ax= {}; fig = {} #each plot is a different figure - keep those and axes separately

# if you have more kinds of data, get more colormaps from
# https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
cmaps = """Blues Oranges Greens Reds""".split()

# I want to print 2019 and 2020 data only and for 3 categories one below the other
# to see how this year is trending compared to last.
for i, yr in enumerate([2020]):
    for j,cat in enumerate("active confirmed recovered deceased".split()):
        #we take the events as a series; and fill dates for which
        #there is no data available with 0
        #events = df[df.cat == cat].y.resample("D").asfreq().fillna(0)
        events = df[cat].resample("D").asfreq().fillna(0)
        # make the plot and set title
        k = "{0}_{1}".format(yr, cat)
        fig[k], ax[k] = plt.subplots(1, 1, figsize = (10, 2)) #tweak figsize x,y
        calmap.yearplot(events, year=yr, cmap=cmaps[j],
                  daylabels='MTWTFSS',linewidth=1,  ax=ax[k])
        fig[k].suptitle(cat) 
        #up to here is enough to plot in Jupyter notebook
        #I wanted to save the plot as pngs too so that those can be
        #embedded in an html page/email -- the next line saves those
        if not args.output_prefix:
            plt.savefig("./{0}_{1}_{2}.png".format(i,j,k))
        else:
            plt.savefig("./{0}_{1}_{2}_{3}.png".format(args.output_prefix,i,j,k))
