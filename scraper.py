from flask import Flask, Response
import re
import json
import requests
import datetime

app = Flask(__name__)

import logging

# Log only in production mode.
# if not app.debug:
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

# FIXME use default-dict

default = {
  "type": "Feature",
  "properties": {
    "amenity": "parking",
    "name": "",
    "free": 0
  }
}

with open("osm_feature_lookup.json") as f:
    osm_feature_lookup = json.load(f)

@app.route("/")
def scrape():

    def geojson_lines():
        r = requests.get('http://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
        pattern = '(?P<name>[\w\s]+)</a>\s+</td>\s+<td class="freeCount\"\>(?P<free>[\d]+)\<\/td\>'

        for match in re.finditer(pattern, r.text):
            (name, free) = match.groups()

            geojson = osm_feature_lookup.get(name, default)

            geojson['properties'].update({
                'name': name,
                'timestamp': datetime.datetime.utcnow().isoformat("T") + "Z",
                'free': int(free)
            })

            # FIXME add `coordinates_point` derived from geo_shape if missing

            yield json.dumps(geojson, ensure_ascii=False) + '\n'

    app.logger.info("Sending out scraped data as geojson..")
    return Response(geojson_lines(), mimetype='application/json')

@app.route("/healthz")
def healthz():
    return "OK"
    # return Response(status=200)
    # return Response(status=204)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
