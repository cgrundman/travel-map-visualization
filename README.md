# Travel Map Visualization

This repo features visualization code for Regional/National travel. Using a base map from a shapefile and geopandas to create a voronoi segmented map, this code can create a timelapse of travels in a geographic region or country from a list of locations. An example can be seen below (national parks visited as of Sep 2024):

<img src="https://github.com/cgrundman/np-map-visualization/blob/main/National_Parks/national_parks.png" width="300"/>

<img src="https://github.com/cgrundman/np-map-visualization/blob/main/Sehenswuerdigkeiten/de_sites.png" width="200"/>

## Run Locally

Clone the project

```bash
  git clone https://github.com/cgrundman/np-map-visualization
```

Go to the project directory

```bash
  cd local/path/np-map-visualization
```

Install libraries

```bash
  pip install -r requirements.txt
```

## Demo

The following are limited gifs made with [ezgif.com](https://ezgif.com/maker). Full gifs can be seen in the subdirectories.

US National Parks:

<img src="https://github.com/cgrundman/np-map-visualization/blob/main/National_Parks/nps_small.gif" width="500"/>

Germany cities and sites (sehenswürdigkeiten):

<img src="https://github.com/cgrundman/np-map-visualization/blob/main/Sehenswuerdigkeiten/de_small.gif" width="350"/>

## Acknowledgements

Resources:
 - [wellsr.com](https://wellsr.com/python/python-voronoi-diagram-with-geopandas-and-geoplot/)
 - [GeoPandas](https://geopandas.org/en/latest/index.html)
 - [National Parks System](https://www.nps.gov/index.htm)
 - [Google Maps](https://maps.google.com/)

Map Data and Shapefiles:
 - [census.gov](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html)
 - [European Environment Agency](https://www.eea.europa.eu/data-and-maps/data/eea-reference-grids-2/gis-files/germany-shapefile)

## License

[MIT](https://choosealicense.com/licenses/mit/)
