import sys
sys.path.insert(1, '/home/sbanik@quansight.com/demo-dashboards')

from intake_utils import (
    catalog_init,
    list_catalog,
    view_catalog)

import numpy as np
import pandas as pd

import geoviews as gv
import matplotlib.pyplot as plt
import holoviews as hv
from holoviews import opts,dim
from bokeh.models import HoverTool

import datashader as ds
import colorcet as cc
import holoviews.operation.datashader as hd
from datashader.utils import lnglat_to_meters as webm
from datashader import transfer_functions as tf
from holoviews.element.tiles import StamenTerrainRetina, StamenTonerRetina

hv.extension('bokeh', logo=False)

"""
Static variables for plotting
"""
austin_coordinates = ((-97.91,  -97.52), (30.17, 30.37))
plot_width  = int(950)
plot_height = int(plot_width//1.2)
tile_selection = StamenTerrainRetina() 
color_scheme = cc.glasbey_bw_minc_20_maxl_70 
magnification_intensity = 5
threshold_value = 1

class austin_trees:

    def __init__(self):
        catalog = catalog_init()
        self.df_austin_trees = catalog.austin_trees.read()

    def pre_processing(self):
        """
        STEPS:
        ------
            - Converting specie names into lower case
            - Second step to check if the specie name has a char `,` present
            - Specie name is split by `,`(if present) reversed and joined via space to retain its validity
            - Strip any extra spaces
            - Removing redundancy
            - Checking unique specie count
        """
        self.df_austin_trees['SPECIES'] = [x.lower() for x in self.df_austin_trees.SPECIES.astype(str)]
        self.df_austin_trees['SPECIES'] = [str(" ".join(reversed(x.split(","))).strip()) if ',' in x else x for x in self.df_austin_trees.SPECIES]
        deduping_specie = ['southern live oak', 'live (southern) oak']
        self.df_austin_trees.loc[self.df_austin_trees['SPECIES'].isin(deduping_specie), 'SPECIES'] = 'southern live oak'
        unique_specie_count = len(self.df_austin_trees['SPECIES'].unique())
        print("Unique specie count =", unique_specie_count)
        return self.df_austin_trees

    def post_processing(self, dataset):
        """Aggregation on raw dataset"""
        df_macro = dataset.groupby('SPECIES') \
                .agg({'SPECIES':'count', 'DIAMETER':'mean'}) \
                .rename(columns={'SPECIES':'specie_count','DIAMETER':'mean_diameter'}) \
                .reset_index()\
                .sort_values(by=['specie_count','mean_diameter'], ascending=False)
        return df_macro 
    
    def select_top_n_specie(self, dataset, count):
        """selecting subset of dataset based on top 'n' specie count"""
        if count > 0:
            df_macro = self.post_processing(dataset)
            specie_name_list = df_macro[:int(count)].SPECIES.to_list()
            print("Specie count selected =", len(specie_name_list))
            df_raw_subset = dataset.query('SPECIES in @specie_name_list')
            df_processed_subset = self.post_processing(df_raw_subset)
            print(df_processed_subset.info())
            return df_raw_subset, df_processed_subset
        else:
            print("Select specie count greater than 0")

    def geo_plot_ready_data(self, dataset):
        """Data interpolations to plotting a map using lat/lon"""
        raw_df_trees_geo, processed_df_trees_geo = self.select_top_n_specie(dataset, 10)
        raw_df_trees_geo = raw_df_trees_geo[['LONGTITUDE','LATITUDE', 'SPECIES', 'DIAMETER']]
        raw_df_trees_geo.loc[:, 'lon'], raw_df_trees_geo.loc[:, 'lat'] = webm(raw_df_trees_geo['LONGTITUDE'],raw_df_trees_geo['LATITUDE'])
        raw_df_trees_geo["SPECIES"]=raw_df_trees_geo["SPECIES"].astype("category")
        print("Sneak peek into plot ready data \n", '*'*30, '\n', raw_df_trees_geo.head(1))
        return raw_df_trees_geo

    
    def geo_plot(self, raw_df_trees_geo):
        cats = list(raw_df_trees_geo.SPECIES.unique())
        colors    = color_scheme
        color_key = {cat: tuple(int(e*255.) for e in colors[i]) for i, cat in enumerate(cats)}
        legend    = hv.NdOverlay({k: hv.Points([0,0], label=str(k)).opts(
                                                color=cc.rgb_to_hex(*v), size=0, apply_ranges=False) 
                                for k, v in color_key.items()}, 'SPECIES')


        x_range_w ,y_range_w = webm(*austin_coordinates)    
        tiles = tile_selection.redim.range(x=tuple(x_range_w), y=tuple(y_range_w))
        shaded = hd.datashade(hv.Points(raw_df_trees_geo, ['lon', 'lat'], 
                                        x_range=x_range_w, y_range=y_range_w, 
                                        plot_height=plot_height, plot_width=plot_width), 
                                        color_key=color_key,
                                        aggregator=ds.count_cat('SPECIES'))
        ropts = dict(tools=['hover'])
        hover_data = shaded.opts(**ropts)

        tiles * hd.dynspread(shaded, 
                            threshold=threshold_value, 
                            max_px=magnification_intensity, 
                            shape='circle').opts(
                                xaxis=None, yaxis=None, width=plot_width, height=plot_height) * (hover_data) * legend
    