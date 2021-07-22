

import geopandas as gpd

import pandas as pd
import cartopy
import cartopy.feature as cf

from cartopy import crs as ccrs

import os
from datetime import datetime
import numpy as np

import matplotlib.pyplot as plt



def hex_to_RGB(hex):
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]

def RGB_to_hex(RGB):
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                        "{0:x}".format(v) for v in RGB])


def color_scale(from_hex, to_hex, n=10):
    
    from_rgb = hex_to_RGB(from_hex)
    to_rgb = hex_to_RGB(to_hex)
    
    result = [from_hex]

    for i in range(1, n):
        new_color = [
            int(from_rgb[j] + (float(i)/(n-1))*(to_rgb[j]-from_rgb[j]))
            for j in range(3)
        ]

        result.append( RGB_to_hex(new_color))

    return result


def color_for_age(age, color_scale, none_color):
    if np.isnan(age):
        return none_color
    
    for (a_limit, rgb) in color_scale[::-1]:
        if age >= a_limit:
            return rgb 


def generate_map(gdf, filename, bg_color, color_scale, none_color):
    
    ax = plt.figure(figsize = ( 65, 45 ))
    plt.axis('off')
    ax.set_facecolor(bg_color)

    for (raw_shape, age) in gdf.loc[:,['geometry', 'AGE']].values:

        x = raw_shape.exterior.coords.xy[0]
        y = raw_shape.exterior.coords.xy[1]
        plt.fill(x, y, c=color_for_age(age, color_scale, none_color))

        for interior in raw_shape.interiors:
            x = [k[0] for k in interior.coords[:]]
            y = [k[1] for k in interior.coords[:]]
            plt.fill(x, y, c=bg_color)


    plt.savefig(filename,  bbox_inches='tight', facecolor=bg_color, edgecolor='none')
    plt.close()
    return


def build_age(x):
    
    if x is None:
        return None
    
    return datetime.now().year - int(x[:4])




shapefile = 'extracts/PARIS2/PARIS.shp'

paris = gpd.read_file(shapefile)
paris['AGE'] = paris.loc[ :, 'DATE_APP'].apply(build_age)

### Quansight colors

# --- V4 ---
# Two themes : dark and light
# color scale used for the "V4" images. it appears the colors used are not exactly the ones from the branding colors.
qs_colors = [ "#613EA3","#673EA1","#6D3D9F","#733D9E","#793D9C","#7F3C9A","#863C98","#8C3B96","#923B94","#983B93","#9E3A91","#A43A8F",    
                "#A34788","#A25481","#A1617A","#A06E73","#9F7B6C","#9E8864","#9D955D","#9CA256","#9BAF4F","#9ABC48","#99C941",][::-1]

# color to use when the age of the building is unknown.
none_color_light = '#D8D8D8'
none_color_dark = '#272727'


# --- V5 ---
# three themes : dark, light, purple

# Primary colors, according to the palette V1 :
violet = "#452392"
plum = "#A43A8F"
green = "#99C941"

qs_colors = color_scale(violet,plum) + color_scale(plum,green)[1:]
qs_colors = qs_colors[::-1]

# Cut in bins
bins = pd.qcut(paris['AGE'], q=len(qs_colors)+1, duplicates='drop', retbins=True)

color_scale_light = list(zip(bins[1], qs_colors))
color_scale_dark = list(zip(bins[1], qs_colors[::-1]))

# none colors for V5 :
none_color_light = '#CECECE'
none_color_dark = '#959DA5'
none_color_purple = '#26086B'


print("go")

# dark    
generate_map(paris, 'paris_v5-3_dark.png', 'k', color_scale_dark, none_color_dark)
print("dark done")

# light
generate_map(paris, 'paris_v5-3_light.png', 'white', color_scale_light, none_color_light )
print("light done")

# violet background, with shades from green to plum then plum to very light shade of violet
color_scale_purple = color_scale(green,plum) + color_scale(plum,"#D8C9FB")[1:] #   #D8C9FB = "very light shade of violet"
color_scale_purple = list(zip(bins[1], color_scale_purple))

generate_map(paris, 'paris_v5-3_purple.png', violet, color_scale_purple, none_color_purple )
print("purple done")


# violet background, with shades from plum to green 
color_scale_plumgreen = color_scale(plum,green, 19) 
color_scale_plumgreen = list(zip(bins[1], color_scale_plumgreen))

generate_map(paris, 'paris_v5-3_plumgreen.png', violet, color_scale_plumgreen, none_color_dark )
print("purple done")
exit()