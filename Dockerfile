FROM python:3.6-alpine
RUN apk --no-cache add tini

# RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

# ENTRYPOINT ["/tini", "--"]
CMD ["/sbin/tini", "--", "python", "scraper.py"]
EXPOSE 5000
