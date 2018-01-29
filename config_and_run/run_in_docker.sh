#!/bin/bash

CSV_NAME=$1
CONFIG_NAME=obscuritext_configs

# Copies csv file and config files into docker
docker cp $CSV_NAME.csv e37dba6a70c3:/obscuritext-develop/$CSV_NAME.csv
docker cp $CONFIG_NAME.cfg e37dba6a70c3:/obscuritext-develop/$CONFIG_NAME.cfg

docker exec -it e37dba6a70c3 sh -c "python3 text_obscure.py"
docker cp e37dba6a70c3:/obscuritext-develop/obscured_$CSV_NAME ./obscured_$CSV_NAME
