# Data 


Data are organized in 3 directories 

### `raw/`

- NG.txt : 
    - Natural Gas Annual Supply & Disposition by US State
    - Source and details about format : https://www.eia.gov/opendata/bulkfiles.php
    - It's a tree-like structure that has been flattened. 
    - The main dataset we use is built into directory `etl/`


### `geo/`

- `States_shapefile/` : 
    - Shapefile for the US, to plot chloropleth based on the states
    - Source and details about format : https://hub.arcgis.com/datasets/1b02c87f62d24508970dc1a6df80c98e_0/data?geometry=87.641%2C29.346%2C27.172%2C67.392




### `etl/`

Data extracted from `raw/NG.txt` to build multiple datasets, organized by categories.

To build them, run :
```
python scripts/etl.py
```



