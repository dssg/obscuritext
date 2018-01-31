FROM python:3.6.3

ENV SHELL="/bin/bash"

RUN apt-get update && \
    apt-get install -y git \
                       python3-pip \
                       wget

RUN wget -O- https://api.github.com/repos/dssg/obscuritext/tarball/b818152e99679fbb0830fe20223f1a9f29ea1d88 | \
    tar -zxvf -

WORKDIR /dssg-obscuritext-b818152

RUN pip3 install -r requirements.txt
