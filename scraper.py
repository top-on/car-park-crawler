from flask import Flask, Response
import re
import json
import requests
import datetime
from minio import Minio
import minio.error
import logging
import hashlib

app = Flask(__name__)

# Log only in production mode.
# if not app.debug:
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

minioClient = Minio('minio.minio.svc:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)

try:
        minioClient.make_bucket("parkleit")
except minio.error.BucketAlreadyOwnedByYou as err:
        pass
except minio.error.BucketAlreadyExists as err:
        pass
except minio.error.ResponseError as err:
        app.logger.error(err)
        raise

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

            try:
                hashid = hashlib.md5(json.dumps(geojson, sort_keys=True)).hexdigest()
                minioClient.put_object('parkleit', hashid, geojson,
                                       len(geojson), content_type='application/json')
            except minio.error.ResponseError as err:
                app.logger.error(err)

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
