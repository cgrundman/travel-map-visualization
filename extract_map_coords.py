import json

file = 'ir/submaps/reference/geoBoundaries-IRN-ADM1_simplified.geojson'

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)

coords_list = []
for feature in data["features"]:

    coords_list.append({
        "name": feature["properties"]["shapeISO"],
        "coordinates": feature["geometry"]["coordinates"][0]
    })

for state in coords_list:
    print(state['name'])
    min_lat = min(pt[0] for pt in state['coordinates'])
    min_lon = min(pt[1] for pt in state['coordinates'])
    coords = ""
    for i, point in enumerate(state["coordinates"]):
        if i%10==0:
            try:
                string = str(round((point[0]-min_lat), 2)) + "," + str(round((point[1]-min_lon), 2)) + " "
            except:
                print(point)

            coords += string

    filehandler = open(state['name'], 'wt')
    filehandler.write(coords)
