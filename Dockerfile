FROM python:3.5
ENV PYTHONUNBUFFERED 1  
RUN mkdir /config  
COPY /config/requirements.pip /config/  
RUN pip install -r /config/requirements.pip  
RUN mkdir /fractal-django;  
WORKDIR /fractal-django  

