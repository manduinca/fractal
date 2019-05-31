#!/bin/bash

tar_file="fractal-django.tar.gz"
USER="www_fractal"
HOST="fractal.edu.pe"

tar cvf ${tar_file} fractal_django

scp ${tar_file} ${USER}@${HOST}:

ssh ${USER}@${HOST}

docker stop nginx-fractal-django2 fractal-django2 fractaldjango2_db_1
rm -rf fractal_django

tar xvf ~/${tar_file}
cp producion_settings.py settings.py

rm -rf asistencias/migrations

docker-compose up
