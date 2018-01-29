FROM python:3.6.3

ENV SHELL="/bin/bash"

RUN apt-get update && \
    apt-get install -y git \
                       wget \
                       python3-pip \
                       vim

RUN wget https://github.com/dssg/obscuritext/archive/develop.tar.gz && \
    tar zxvf develop.tar.gz

WORKDIR /obscuritext-develop

RUN pip3 install -r requirements.txt
