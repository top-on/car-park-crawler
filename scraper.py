from flask import Flask, Response
import re, json, requests, datetime

app = Flask(__name__)

# FIXME use default-dict

default = {
  "type": "Feature",
  "properties": {
    "amenity": "parking",
    "name": "",
    "free": 0
  }
}

osm_feature_lookup = {
    "PH Theater": {
      "type": "Feature",
      "id": "node/68293849",
      "properties": {
        "@id": "node/68293849",
        "amenity": "parking",
        "capacity": "793",
        "capacity:disabled": "10",
        "capacity:women": "46",
        "name": "Theaterparkhaus",
        "parking": "underground",
        "toilets:wheelchair": "yes",
        "website": "http://www.stadt-muenster.de/tiefbauamt/parkleitsystem/parkhaeuser/detailansicht/parkhaus/1.html"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [
          7.6265355,
          51.9660696
        ]
      }
    }
}

@app.route("/")
def scrape():

    def json_lines():
        r = requests.get('http://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
        pattern = '(?P<name>[\w\s]+)</a>\s+</td>\s+<td class="freeCount\"\>(?P<free>[\d]+)\<\/td\>'
        for match in re.finditer(pattern, r.text):
            yield json.dumps(match.groupdict(), ensure_ascii=False) + '\n'

    def geojson_lines():
        r = requests.get('http://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
        pattern = '(?P<name>[\w\s]+)</a>\s+</td>\s+<td class="freeCount\"\>(?P<free>[\d]+)\<\/td\>'

        for match in re.finditer(pattern, r.text):
            (name, free) = match.groups()

            if name in osm_feature_lookup:
                geojson = osm_feature_lookup[name]
            else:
                geojson = default
                geojson['properties'].update({'name': name})

            geojson['properties'].update({
                'timestamp': datetime.datetime.utcnow().isoformat("T") + "Z",
                'free': free
            })
            yield json.dumps(geojson, ensure_ascii=False) + '\n'

    return Response(geojson_lines(), mimetype='text/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
