#!/bin/bash


USER="www_fractal"
HOST="fractal.edu.pe"
REMOTE_PATH=fractal-django2/fractal-django/

# Access to remote server
ssh ${USER}@${HOST}

# Access to docker container
docker exec -it fractal-django2 /bin/bash
python manage.py dumpdata > latest_db.json
exit

# Back to local
exit

scp ${USER}@{HOST}:${REMOTE_PATH}/latest_db.json latest_db.json


docker exec -it fractal-django /bin/bash
python manage.py flush
python manage.py loaddata latest_db.json

