FROM python:3.6.3

ENV SHELL="/bin/bash"

RUN apt-get update && \
    apt-get install -y git \
                       python3-pip \
                       wget

RUN wget -O- https://api.github.com/repos/dssg/obscuritext/tarball/7890e9a1bcb7b611b2ea0f00786237dfafa6b0fb | \
    tar -zxvf -

WORKDIR /dssg-obscuritext-7890e9a

RUN pip3 install -r requirements.txt
