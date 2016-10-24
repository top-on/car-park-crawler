from flask import Flask, Response
import re, json, requests

app = Flask(__name__)

@app.route("/")
def scrape():

    def json_lines():
        r = requests.get('http://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
        pattern = '(?P<name>[\w\s]+)</a>\s+</td>\s+<td class="freeCount\"\>(?P<free>[\d]+)\<\/td\>'
        for m in re.finditer(pattern, r.text):
            yield json.dumps(m.groupdict(), ensure_ascii=False) + '\n'

    return Response(json_lines(), mimetype='text/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
