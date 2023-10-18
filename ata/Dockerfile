FROM python:3.11-bullseye
WORKDIR .
RUN apt-get update && apt-get install -y -q mc
# apt-utils tzdata curl sed jq postgresql-client unzip
# postgresql-client
# RUN apt-get update && apt-get install -y -q curl sed jq
# RUN dpkg-reconfigure --frontend noninteractive tzdata
COPY ./opt/main.py /opt
COPY ./opt/request.sql /opt
COPY ./opt/PyYAML-6.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl /opt
RUN pip3 install /opt/PyYAML-6.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
COPY ./opt/psycopg2-2.9.7.tar.gz /opt
RUN pip3 install /opt/psycopg2-2.9.7.tar.gz