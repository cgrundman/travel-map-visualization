# Travel Map Visualization

This repo features visualization code for travel. Using a collection of submaps and meta data, plots are created with location goals. THe submaps are colored based on "completion" and the points are highlighted in 3 modes: unvisited, active (latest data), and visited. Examples of images can be seen below:

<table style="width:100%; table-layout:fixed;">
  <tr>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/us_1.png" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/us_3.png">Full Image</a></b>
    </td>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/de_1.png" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/de_4.png">Full Image</a></b>
    </td>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/eu_1.png" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/plots/eu_6.png">Full Image</a></b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/us_1.gif" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/us_3.gif">Full gif</a></b>
    </td>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/de_1.gif" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/de_4.gif">Full gif</a></b>
    </td>
    <td align="center">
      <img src="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/eu_1.gif" height="200"/>
      <br><b><a href="https://github.com/cgrundman/travel-map-visualization/blob/main/gifs/eu_6.gif">Full gif</a></b>
    </td>
  </tr>
</table>

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

## Acknowledgements

Resources:
 - [GeoPandas](https://geopandas.org/en/latest/index.html)
 - [National Parks System](https://www.nps.gov/index.htm)
 - [Google Maps](https://maps.google.com/)

Map Data and Shapefiles:
 - [geoBoundaries](https://www.geoboundaries.org/)

## License

[MIT](https://choosealicense.com/licenses/mit/)
