import sys
sys.path.insert(1, '/home/sbanik@quansight.com/demo-dashboards')

from intake_utils import (
    catalog_init,
    list_catalog,
    view_catalog)

import numpy as np
import pandas as pd
import panel as pn

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
count_widget = pn.widgets.IntSlider(name = 'Specie count', value = 7, start = 1, end = 15)
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
        print("Ready to plot")
        plot_geo = tiles * hd.dynspread(shaded, 
                            threshold=threshold_value, 
                            max_px=magnification_intensity, 
                            shape='circle').opts(
                                xaxis=None, yaxis=None, width=1000, height=600) * (hover_data) * legend
        title = "### 👩🏽‍💻 A demonstrating using datashader, holoviews and bokeh as backend. \
                 **NOTE:** The map takes some time to load completely "
        return pn.Column(title, plot_geo)
    
    def violin_plot(self, dataset):
        key_dimensions   = [('DIAMETER', 'Diameter (inches)')]
        value_dimensions = [('SPECIES', 'Specie name')]
        count_widget = pn.widgets.IntSlider(name = 'Specie count', value = 7, start = 1, end = 15)
        hover = HoverTool(tooltips=[('DIAMETER','$y')])

        @pn.depends(count_widget.param.value)
        def plotting_specie(count_widget):
            df_top_10_raw,df_top_10_processed = self.select_top_n_specie(dataset, count_widget)
            fig = hv.Violin(df_top_10_raw, value_dimensions, key_dimensions).opts(xrotation=45, width=800, height=400, 
                                                                                  violin_fill_color=dim('SPECIES').str(), 
                                                                                  cmap='Set1', tools=[hover])
            return fig

        widgets = pn.WidgetBox(count_widget)
        title = "### 🌱  Violin plot, specie overview based on diameter distribution"
        return pn.Row(title, pn.Column(widgets, 
                                plotting_specie, 
                                sizing_mode='stretch_width'))
    
    def distribution_plot(self, dataset):
        value_dimensions   = [('mean_diameter', 'Mean diameter (measure unit=inches)'), ('specie_count', 'Specie Count')]
        key_dimensions = [('SPECIES', 'SPECIES')]
        df_top_10_raw,df_top_10_processed = self.select_top_n_specie(dataset, 10)
        macro = hv.Table(df_top_10_processed, key_dimensions, value_dimensions)

        plot_each_specie = macro.to.table('specie_count', 'Mean diameter (measure unit=inches)').opts(height=50, width=400)
        hover = HoverTool(tooltips=[('DIAMETER','$x')])
        fig = plot_each_specie + hv.Distribution(
            data=df_top_10_raw,
            kdims=['DIAMETER'],
            vdims=['SPECIES'],
        ).groupby(
            'SPECIES'
        ).opts(tools=[hover])
        
        title = "### 📖 Distribution plot based mean diameter and abundance - Top 10 specie"
        return pn.Row(title, pn.Row(fig, 
                                sizing_mode='stretch_width'))
        
    def diversity_trees_plot(self, dataset):
        raw_df_trees_subset, processed_df_trees_subset= self.select_top_n_specie(dataset, 10)
        raw_df_trees_subset['rounded_diameter'] = raw_df_trees_subset['DIAMETER'].round()

        raw_df_trees_subset = raw_df_trees_subset.drop(['GEOMETRY', 'LATITUDE', 'LONGTITUDE', 'New Georeferenced Column'], axis=1)
        plotable_df_subset = raw_df_trees_subset.loc[raw_df_trees_subset['rounded_diameter']<=40].groupby(
            ['SPECIES']).value_counts(
            'rounded_diameter').reset_index().rename(
            columns={0: 'count_diameter'})
        plot = hv.Bars(plotable_df_subset, kdims=['rounded_diameter', 'SPECIES'], vdims=['count_diameter']).aggregate(function=np.sum).sort()
        hover = HoverTool(tooltips=[('Specie name','@SPECIES'), 
                            ('Diamter value','@rounded_diameter'), 
                            ('Total number of trees', '@count_diameter')])
        fig = plot.opts(width=1200, 
                  height=525,
                  stacked=True,
                  tools=[hover]).relabel("Diversity of diameter values among top 10 species")
        return fig
        