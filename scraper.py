from flask import Flask, Response
import re
import json
import requests
import datetime
from minio import Minio
import minio.error
import logging
import hashlib
import io
import sys

app = Flask(__name__)

# Log only in production mode.
# if not app.debug:
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

# minioClient = Minio('minio.minio.svc:9000',
minioClient = Minio('minio.codeformuenster.org',
                    access_key='minio',
                    secret_key='minio123',
                    secure=True)
                    # secure=False)

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

def minio_put_json(bucket, json_dict, name=None):
    json_bytes = json.dumps(json_dict, sort_keys=True, ensure_ascii=False).encode()
    json_bytesio = io.BytesIO(json_bytes)
    if not name:
        json_hash = hashlib.shake_256(json_bytes).hexdigest(16)
        name = f"{json_hash}.json"
    minioClient.put_object(bucket, name, json_bytesio, json_bytesio.getbuffer().nbytes,
                           content_type='application/json')


def scrape_spaces():
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
        yield geojson


@app.route("/minio")
def minio():
    for space in scrape_spaces():
        try:
            minio_put_json("parkleit", space)
        except minio.error.ResponseError as err:
            app.logger.error(err)
    return "OK", 200


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
