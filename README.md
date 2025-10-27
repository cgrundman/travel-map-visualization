# Travel Map Visualization

This repo features visualization code for travel. Using a collection of submaps and meta data, plots are created with location goals. THe submaps are colored based on "completion" and the points are highlighted in 3 modes: unvisited, active (latest data), and visited. Examples of images can be seen below:

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/us_1.png" height="200"/> <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/de_1.png" height="200"/> <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/eu_1.png" height="200"/>

All visited locations have data data included. For all dates present in the location files, an image is plotted. These images are then compiled into a gif.

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

US National Parks:

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/us_1.gif" height="200"/>

[Full-size gif](https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/us_3.gif)

Germany cities and sites:

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/de_1.gif" height="200"/>

[Full-size gif](https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/de_4.gif)

European cities and sites:

<img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/eu_1.gif" height="200"/>

[Full-size gif](https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/eu_5.gif)

## Acknowledgements

Resources:
 - [GeoPandas](https://geopandas.org/en/latest/index.html)
 - [National Parks System](https://www.nps.gov/index.htm)
 - [Google Maps](https://maps.google.com/)

Map Data and Shapefiles:
 - [geoBoundaries](https://www.geoboundaries.org/)

## License

[MIT](https://choosealicense.com/licenses/mit/)
