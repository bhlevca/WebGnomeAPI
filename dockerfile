FROM gitlab.orr.noaa.gov:5002/pygnome:latest
RUN yum update -y

RUN yum install -y redis

COPY ./ /webgnomeapi/
RUN cd webgnomeapi && pip install -r requirements.txt
RUN cd webgnomeapi && pip install -e .
RUN cd webgnomeapi && python setup.py compilejson

RUN mkdir /config
RUN cp /webgnomeapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /webgnomeapi/config.ini

EXPOSE 9899
VOLUME /config
VOLUME /webgnomeapi/model
WORKDIR /webgnomeapi/
ENTRYPOINT ["/webgnomeapi/docker_start.sh"] 
