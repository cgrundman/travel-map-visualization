import json

IR_FILE = 'ir/submaps/reference/geoBoundaries-IRN-ADM1_simplified.geojson'

file = IR_FILE

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

    coords = ""
    if len(state['coordinates']) < 10:
        points = state['coordinates'][0]
    else:
        points = state['coordinates']
    min_lat = min(pt[0] for pt in points)
    min_lon = min(pt[1] for pt in points)
    for i, point in enumerate(points):

        if i%10==0:
            string = str(round((point[0]-min_lat), 2)) + "," + str(round((point[1]-min_lon), 2)) + " "

            coords += string

    filehandler = open(state['name'], 'wt')
    filehandler.write(coords)
