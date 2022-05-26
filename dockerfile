FROM pygnome

RUN yum update -y \
    && yum install -y redis


COPY ./ /webgnomeapi/

RUN conda install \
       --file webgnomeapi/conda_requirements.txt
#       --file webgnomeapi/libgoods/conda_requirements.txt \
#       --file webgnomeapi/libgoods/model_catalogs/conda_requirements.txt

# RUN pip install -r webgnomeapi/libgoods/model_catalogs/pip_requirements.txt

# RUN cd webgnomeapi/libgoods/model_catalogs && pip install .

RUN cd webgnomeapi/libgoods && pip install .

RUN cd webgnomeapi && pip install .

RUN cd webgnomeapi && python setup.py compilejson

RUN mkdir /config
RUN cp /webgnomeapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /webgnomeapi/config.ini

EXPOSE 9899
VOLUME /config
VOLUME /webgnomeapi/models
WORKDIR /webgnomeapi/
ENTRYPOINT ["/webgnomeapi/docker_start.sh"] 
