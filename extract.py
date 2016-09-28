# SCRAPE MUENSTER PARKLEITSYSTEM AND RETRIEVE FREE SPOTS

def getFreeSpots():
    # GET HTML
    import urllib.request
    import re

    opener = urllib.request.FancyURLopener({})
    url = "http://www.stadt-muenster.de/tiefbauamt/parkleitsystem/"
    f = opener.open(url)
    content = f.read()

    # APPLY REGEX
    regex = '([\w\s]+)</a>\s+</td>\s+<td class="freeCount\"\>([\d]+)\<\/td\>'
    results = re.compile( regex, re.M | re.U ).findall( content.decode('utf-8') )

    return results

# CONVERT LIST TO JSON
def getJson():
    results = getFreeSpots()
    names = [x[0] for x in results]
    free_spots = [x[1] for x in results]
    final = [{'name': name, 'free_spots': free_spots} for name, free_spots in zip(names, free_spots)]
    import json
    j = json.dumps(final, ensure_ascii=False)
    return j

print(getJson())
