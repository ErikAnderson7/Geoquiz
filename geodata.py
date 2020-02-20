import pandas
import geopandas

def openSHPFile():
    path = "data/countries.shp"
    countries_df = geopandas.read_file(path)
    return countries_df

def printCountriesDF(gdf):
    print(gdf.show())

def gdfToGeoJSON(gdf):
    return gdf.to_json()

def gdfRowToSVG(row):
    orig_svg = row.geometry.svg()
    rd = row.to_dict()
    del rd['geometry']

    to_add = []
    for key, val in rd.items():
        rdata = 'data-{}="{}"'.format(key, val)
        to_add.append(rdata)
    return '<g {}>'.format(' '.join(to_add)) + orig_svg[3:]


def getSVG(gdf):
    rows = []
    for i, row in gdf.iterrows():
        p = gdfRowToSVG(row)
        rows.append(p)
    return rows
