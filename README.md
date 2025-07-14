# Travel Map Visualization

This repo features visualization code for Regional/National travel. Using a base map from a shapefile and geopandas to create a voronoi segmented map, this code can create a timelapse of travels in a geographic region or country from a list of locations. An example can be seen below (national parks visited as of Sep 2024):

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/us_1.png" width="300"/>

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/de_1.png" width="200"/>

These maps are voronoi segmented maps. The this takes given points and maps regions of least distance to them. The need was to better show the extent of travels. Points do not accuratly show the amounbt of distance and size of the area seen. 

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

I drove to most of these parks with my own car (2012 Chevrolet Sonic), sometimes taking a free weekend or holiday to see the sites. I was also able to do this between jobs and committed all of vacation time for 6 years to this pursuit.

Germany cities and sites (Sehenswürdigkeiten):

<img src="https://github.com/cgrundman/np-map-visualization/blob/main/Sehenswuerdigkeiten/de_small.gif" width="350"/>

As a fun fact, the locations seen on this maps are almost exclsivly through public transportation and train travel. This makes seeing these cities and places much more difficult.

## Acknowledgements

Resources:
 - [GeoPandas](https://geopandas.org/en/latest/index.html)
 - [National Parks System](https://www.nps.gov/index.htm)
 - [Google Maps](https://maps.google.com/)

Map Data and Shapefiles:
 - [geoBoundaries](https://www.geoboundaries.org/)

## License

[MIT](https://choosealicense.com/licenses/mit/)
