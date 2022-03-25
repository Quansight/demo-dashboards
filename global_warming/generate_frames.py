import os
import pandas as pd
import numpy as np
import math

import holoviews as hv
hv.extension('bokeh')

# pip install selenium
# conda install -c conda-forge firefox geckodriver

from bokeh.io import export_svgs



# https://stackoverflow.com/questions/4349375/algorithm-to-solve-the-points-of-a-evenly-distributed-even-gaps-spiral

def spiral_points(nbr_points, length, angle_factor = 1):
    xs = [] 
    ys = []
    angle = 0
    for i in range(nbr_points):
        radius = math.sqrt( i + 1 )
        angle += math.asin(1 / radius ) * angle_factor

        x = math.cos(angle) * radius * length 
        y = math.sin(angle) * radius * length 

        xs.append(x)
        ys.append(y)
    return xs, ys

def temperature_points(temperatures, base_length, angle_factor = 1):
    xs = [] 
    ys = []
    angle = 0
    for i in range(len(temperatures)):
        radius = math.sqrt( i + 1 )
        angle += math.asin(1 / radius ) * angle_factor

        x = math.cos(angle) * radius * (base_length + temperatures[i] / base_length)
        y = math.sin(angle) * radius * (base_length + temperatures[i] / base_length)

        xs.append(x)
        ys.append(y)
    return xs, ys



# based on : https://bsouthga.dev/posts/color-gradients-with-python
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




def get_df_viz():

    df = pd.read_csv("data/kaggle/GlobalLandTemperaturesByCountry_withContinents.csv")

    df = df.reset_index(drop=True).sort_values(['Country', 'year', 'month'])

    avg_temps = {}

    # mean on the 30 first years of data for each country
    for c, c_data in df[  ~(df['AverageTemperature'].isna())  ].groupby("Country") :
        avg_temps[c]  = np.mean(c_data['AverageTemperature'][30*12:])


    # mean over the years, for each country
    df_viz_raw = {"country":[], "continent":[], "year":[], "avg_temp_diff":[]}
    for (country, continent, year), c_data in df[  ~(df['AverageTemperature'].isna())  ].groupby(["Country", "continent", "year"]) :
        
        df_viz_raw['country'].append(  country  )
        df_viz_raw['continent'].append(  continent  )
        df_viz_raw['year'].append(  year  )
        df_viz_raw['avg_temp_diff'].append(  np.mean(c_data['AverageTemperature']) - avg_temps[country]  )

    df_viz = pd.DataFrame(data=df_viz_raw)


    # Exclude all rows for which we don't have any data for 1900, but we have data for the last year

    countries_1900 =  df_viz.loc[ (df_viz['year'] == 1900 ), "country"  ]

    yearmax_filter = df_viz['year'] == 2000
    in_1900_filter = df_viz['country'].isin(countries_1900)

    excluded_countries = df_viz.loc[ (yearmax_filter) & ~(in_1900_filter) , "country" ]

    df_viz = df_viz[ ~(df_viz['country'].isin(excluded_countries)) ]

    return df_viz




def generate_static_plots(plot_data, colormaps, size, output_path ):

    os.makedirs(output_path, exist_ok=True)

    max_diff = max( abs(min(plot_data)), abs(max(plot_data)) )
    max_diff = math.ceil(max_diff)

    xs, ys = spiral_points(len(plot_data)  , max_diff, angle_factor=0.80)
    txs, tys = temperature_points(plot_data, max_diff    , angle_factor=0.80)                 
    txs2, tys2 = temperature_points(plot_data[1:], max_diff    , angle_factor=0.80)                 

    polygons = []
    for i in range(0, len(plot_data)-1):
        
        new_poly = [(xs[i],ys[i]), 
                    (txs2[i], tys2[i]), 
                    (txs[i+1], tys[i+1]), 
                    (xs[i+1],ys[i+1])
                ]
        
        polygons.append(  {('x', 'y'):new_poly, "temp":plot_data[i+1]})
        
    for cmap_name, cmap in colormaps.items():
        plot = hv.Polygons( polygons, vdims='temp' ).opts( 
                                color="temp", 
                                cmap=cmap,
                                xlim=(-55, 55), 
                                ylim=(-55, 55),
                                clim=(-max_diff, max_diff),
                                width=size, 
                                height=size,
                                bgcolor="black",
                                xaxis=None,
                                yaxis=None)

        p =  hv.render(plot, backend='bokeh')
        p.output_backend = "svg"
        export_svgs(p, filename=f"{output_path}/plot_{cmap_name}.svg")



def generate_growing_spiral(plot_data, colormaps, size, output_path):

    os.makedirs(output_path, exist_ok=True)

    max_diff = max( abs(min(plot_data)), abs(max(plot_data)) )
    max_diff = math.ceil(max_diff)

    xs, ys = spiral_points(len(plot_data)  , max_diff, angle_factor=0.80)
    txs, tys = temperature_points(plot_data, max_diff    , angle_factor=0.80)                 
    txs2, tys2 = temperature_points(plot_data[1:], max_diff    , angle_factor=0.80)                 

    print(f"generating frames ", end="")
    polygons = []
    for i in range(len(plot_data)-1):
        
        new_poly = [(xs[i],ys[i]), 
                    (txs2[i], tys2[i]), 
                    (txs[i+1], tys[i+1]), 
                    (xs[i+1],ys[i+1])
                ]
        
        polygons.append(  {('x', 'y'):new_poly, "temp":list(plot_data)[i+1]})
        
        print(f" #{i:03d}", end="\t")
        for cmap_name, cmap in colormaps.items():
            
            os.makedirs(f"{output_path}/{cmap_name}", exist_ok=True)

            print(f"{cmap_name[0]},", end=" ")
            plot = hv.Polygons( polygons, vdims='temp' )                     .opts( color="temp",
                                cmap=cmap,
                                xlim=(-55, 55), 
                                ylim=(-55, 55),
                                clim=(-max_diff, max_diff),
                                width=size, 
                                height=size,
                                bgcolor="black",
                                xaxis=None,
                                yaxis=None)

            p =  hv.render(plot, backend='bokeh')
            p.output_backend = "svg"
            filepath = f"{output_path}/{cmap_name}/plot_{cmap_name}_frame_{i:03d}.svg"
            export_svgs(p, filename=filepath)
        print("\t", end="", flush=True)
    print("done")


def temperature_points2(temperatures,
                        base_length,
                        angle_factor = 1,
                        length_ratio=1, 
                        max_length_ratio=1
                       ):
    """
    Updated version of temperature_points function, with 3 new parameters and a new returned value:
        - length_ratio=1 : How much to keep of the distance from the spiral to the temperature point.
            1 (default) : 100%
            0.5 : 50%
            0 : 0%
            By generating data with a growing length_ratio from 0 to 1, all polygon will grow together from 0 to 1, 
            the longer ones growing faster than the smaller ones.

        - max_length_ratio=1 : Max ratio to keep of the distance from the spiral to the temperature point.
            1 (default) : 100%
            0.5 : 50%
            0 : 0%
            By generating data with a growing max_length_ratio from 0 to 1, all polygon will grow together from 0 to 1,
            the smaller ones being fully shown before the longer ones
            
        Returns : 
            xs : x-coordinates of the polygons, according to each temperature, around the spiral for the given parameters
            ys : y-coordinates of the polygons, according to each temperature, around the spiral for the given parameters
            vals : values for the given polygen, capped or scaled according to `length_ratio` and `max_length_ratio` parameters

    """
    xs = [] 
    ys = []
    vals = []
    angle = 0
    for i in range(len(temperatures)):
        radius = math.sqrt( i + 1 )
        angle += math.asin(1 / radius ) * angle_factor

        # base
        #x = math.cos(angle) * radius * (base_length + temperatures[i] / base_length)
        #y = math.sin(angle) * radius * (base_length + temperatures[i] / base_length)

        # works for proportionnal
        #x = math.cos(angle) *  radius * (base_length + temperatures[i] / base_length * length_ratio)
        #y = math.sin(angle) * radius * (base_length + temperatures[i] / base_length * length_ratio)

        if abs(temperatures[i] * length_ratio) > max_length_ratio * base_length:
            factor = base_length + max_length_ratio * ( 1 if temperatures[i] > 0 else -1)
            vals.append( temperatures[i] * max_length_ratio )
        else:
            factor = base_length + temperatures[i] / base_length * length_ratio
            vals.append( temperatures[i]  * length_ratio )


        x = math.cos(angle) * radius * factor
        y = math.sin(angle) * radius * factor


        xs.append(x)
        ys.append(y)
    return xs, ys, vals



def generate_proportional_growing_lengths(plot_data, colormaps, size, output_path, total_frame_count):

    os.makedirs(output_path, exist_ok=True)

    max_diff = max( abs(min(plot_data)), abs(max(plot_data)) )
    max_diff = math.ceil(max_diff)


    xs, ys = spiral_points(len(plot_data)  , max_diff, angle_factor=0.80)
    for nbr_frame in range(total_frame_count):

        print(f"frame : {nbr_frame}\t total frame count : {total_frame_count} \t ratio : {nbr_frame/(total_frame_count-1)}", flush=True)
        txs, tys, _ = temperature_points2(plot_data, 
                                        max_diff, 
                                        angle_factor=0.80, 
                                        length_ratio=nbr_frame/(total_frame_count-1))                 
        txs2, tys2, temps = temperature_points2(plot_data[1:], 
                                        max_diff, 
                                        angle_factor=0.80, 
                                        length_ratio=nbr_frame/(total_frame_count-1))                 

        polygons = []
        for i in range(len(plot_data)-1):

            new_poly = [(xs[i],ys[i]), 
                        (txs2[i], tys2[i]), 
                        (txs[i+1], tys[i+1]), 
                        (xs[i+1],ys[i+1])
                    ]

            polygons.append(  {('x', 'y'):new_poly, "temp":temps[i]})

        print(f"generating frames #{nbr_frame:03d}", end="\t")
        for cmap_name, cmap in colormaps.items():

            os.makedirs(f"{output_path}/{cmap_name}", exist_ok=True)

            print(f"{cmap_name[0]},", end=" ")
            plot = hv.Polygons( polygons, vdims='temp' ).opts( color="temp",
                                cmap=cmap,
                                xlim=(-55, 55), 
                                ylim=(-55, 55),
                                clim=(-max_diff, max_diff),
                                width=size, 
                                height=size,
                                bgcolor="black",
                                xaxis=None,
                                yaxis=None)

            p =  hv.render(plot, backend='bokeh')
            p.output_backend = "svg"
            filepath = f"{output_path}/{cmap_name}/plot_{cmap_name}_frame_{nbr_frame:03d}.svg"
            export_svgs(p, filename=filepath)
            print("\t", end="")
        print("done")


def generate_uniform_growing_lengths(plot_data, colormaps, size, output_path, total_frame_count):

    os.makedirs(output_path, exist_ok=True)

    max_diff = max( abs(min(plot_data)), abs(max(plot_data)) )
    max_diff = math.ceil(max_diff)


    xs, ys = spiral_points(len(plot_data)  , max_diff, angle_factor=0.80)
    for nbr_frame in range(total_frame_count):

        print(f"frame : {nbr_frame}\t total frame count : {total_frame_count} \t ratio : {nbr_frame/(total_frame_count-1)}", flush=True)
        txs, tys, _ = temperature_points2(plot_data, 
                                        max_diff , 
                                        angle_factor=0.80, 
                                        max_length_ratio = nbr_frame/(total_frame_count-1))                 
        txs2, tys2, temps = temperature_points2(plot_data[1:],
                                         max_diff  , 
                                         angle_factor=0.80, 
                                         max_length_ratio = nbr_frame/(total_frame_count-1))                 

        polygons = []
        for i in range(len(plot_data)-1):

            new_poly = [(xs[i],ys[i]), 
                        (txs2[i], tys2[i]), 
                        (txs[i+1], tys[i+1]), 
                        (xs[i+1],ys[i+1])
                    ]

            polygons.append(  {('x', 'y'):new_poly, "temp":temps[i]})

        print(f"generating frames #{nbr_frame:03d}", end="\t")
        for cmap_name, cmap in colormaps.items():

            os.makedirs(f"{output_path}/{cmap_name}", exist_ok=True)

            print(f"{cmap_name[0]},", end=" ")
            plot = hv.Polygons( polygons, vdims='temp' ).opts( color="temp",
                                cmap=cmap,
                                xlim=(-55, 55), 
                                ylim=(-55, 55),
                                clim=(-max_diff, max_diff),
                                width=size, 
                                height=size,
                                bgcolor="black",
                                xaxis=None,
                                yaxis=None)

            p =  hv.render(plot, backend='bokeh')
            p.output_backend = "svg"
            filepath = f"{output_path}/{cmap_name}/plot_{cmap_name}_frame_{nbr_frame:03d}.svg"
            export_svgs(p, filename=filepath)
            print("\t", end="")
        print("done")




def main():

    #generate_static_plots
    df_viz = get_df_viz()


    # Primary colors, according to the palette V1 :
    violet = "#452392"
    plum = "#A43A8F"
    green = "#99C941"

    length = 12
    colors_violet = color_scale(violet,"#FFFFFF", 12)
    colors_plum = color_scale(plum,"#FFFFFF", 12)
    colors_green = color_scale(green,"#FFFFFF", 12)


    colormaps = { 'plum' : colors_plum[::-1],
                  'violet' : colors_violet[::-1],
                  'green' : colors_green[::-1]
            }

    countries = ["Greenland", "United States"]
    

    for country in countries :
        print(f'Generating plots for {country}', flush=True)
        plot_data = df_viz[ df_viz['country'] == country ]
        plot_data = list(plot_data.avg_temp_diff)
        
        generate_static_plots(plot_data,colormaps, 800,  f"output/static/{country}/" )
        generate_growing_spiral(plot_data, colormaps, 800, f"output/growing_spiral/{country}/")

        # 50 frames : 2 seconds with 25 fps
        total_frame_count = 50
        generate_proportional_growing_lengths(plot_data, colormaps, 800, f"output/proportional_growing_lengths/{country}/", total_frame_count)
        generate_uniform_growing_lengths(plot_data, colormaps, 800, f"output/uniform_growing_lengths/{country}/", total_frame_count)

        


        
if __name__ == "__main__":
    main()

exit()








# for i in range(len(data)-1):
#   print(f"""<g clip-path="url(#_clipPath_frame_{i:03d})">
#   <image x="0" y="0" width="800" height="800" href="../frames_green/plot_green_frame_{i:03d}.svg" />
# </g>""")











