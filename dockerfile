FROM pygnome

RUN yum update -y \
    && yum install -y redis


COPY ./ /webgnomeapi/

RUN conda install mamba

RUN mamba install -y \
       --file webgnomeapi/conda_requirements.txt \
       --file webgnomeapi/LibGOODS/conda_requirements.txt \
       --file webgnomeapi/model_catalogs/conda-requirements.txt

RUN pip install -r webgnomeapi/model_catalogs/pip-requirements.txt

RUN cd webgnomeapi/model_catalogs && pip install .
RUN cd webgnomeapi/LibGOODS && pip install .


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