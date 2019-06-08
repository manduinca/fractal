#!/bin/bash

tar_file="fractal-django.tar.gz"
USER="www_fractal"
HOST="fractal.edu.pe"

# First run tests inside docker!
python manage.py test
#python manage.py test billing
#billing.tests.BillingTest.test_status_warning

tar cvf ${tar_file} fractal_django

scp ${tar_file} ${USER}@${HOST}:

ssh ${USER}@${HOST}

docker stop nginx-fractal-django2 fractal-django2 fractaldjango2_db_1
rm -rf fractal_django

tar xvf ~/${tar_file}
cp producion_settings.py settings.py

rm -rf asistencias/migrations

docker-compose up --build
