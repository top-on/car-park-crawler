parkleitsystemCrawler
===
Crawls currently available parking spots in the public car parks in Muenster.


Docker instructions
---

Build image:

    $ docker build --tag local/scraper .

Run container:

    $ docker run --rm --env FLASK_DEBUG=1 --publish 5000:5000 local/scraper python scraper.py

Open in webbrowser:

    http://localhost:5000/

You should see something like:

    [{"free_spots": "629", "name": "PH Theater"}, {"free_spots": "131", "name": "PP Hörsterplatz"}, {"free_spots": "318", "name": "PH Alter Steinweg"}, {"free_spots": "0", "name": "Busparkplatz"}, {"free_spots": "0", "name": "PP Schlossplatz Nord"}, {"free_spots": "0", "name": "PP Schlossplatz Süd"}, {"free_spots": "634", "name": "PH Aegidii"}, {"free_spots": "54", "name": "PP Georgskommende"}, {"free_spots": "140", "name": "PH Münster Arkaden"}, {"free_spots": "158", "name": "PH Karstadt"}, {"free_spots": "231", "name": "PH Stubengasse"}, {"free_spots": "186", "name": "PH Bremer Platz"}, {"free_spots": "377", "name": "PH Engelenschanze"}, {"free_spots": "272", "name": "PH Bahnhofstraße"}, {"free_spots": "492", "name": "PH Cineplex"}, {"free_spots": "305", "name": "PH Stadthaus 3"}]
