FROM ubuntu:18.04
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

WORKDIR /app
COPY . /app

RUN apt-get update && apt install -y python3 python3-pip chromium-chromedriver
RUN pip3 install pip-tools
RUN pip-compile requirements.in
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt stopwords
