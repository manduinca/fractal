Introducción
============
El sistema consta de tres módulos: Asistencias, pagos y notas.

Build
=====
El sistema corre bajo un ambiente docker. Para correrlo ejecutar:
```
docker-compose up -d
```
Luego, el sistema se encuentra disponible en http://localhost:8000/


Modelo
======
Para obtener una versión gráfica del modelo, ejecutar:
```
docker exec -it fractal-django /bin/bash
python manage.py graph_models -a > model.dot
exit
dot -Tpng model.dot -o model.png
```
Para ello se necesita tener instalado GraphViz en el ambiente local, 
instalarlo con `sudo apt install python-pydot python-pydot-ng graphviz` 

Tests
=====
Para correr los tests, ejecutar:
```
docker exec -it fractal-django /bin/bash
python manage.py test
```

Tareas
======
Para ver las tareas pendientes ver el archivo tasks
