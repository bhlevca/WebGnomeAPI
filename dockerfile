FROM pygnome
RUN yum update -y

RUN yum install -y redis

COPY ./ /webgnomeapi/
RUN conda install --file webgnomeapi/conda_requirements.txt \
                  --file webgnomeapi/libgoods/conda_requirements.txt
RUN conda env update -f webgnomeapi/libgoods/model_catalogs/environment.yml

RUN cd wegnome/api/libgoods/model_catalog && pip install -e .
RUN cd webgnomeapi/libgoods && pip install -e .

RUN cd webgnomeapi && pip install -e .
RUN cd webgnomeapi && python setup.py compilejson

RUN mkdir /config
RUN cp /webgnomeapi/config-example.ini /config/config.ini
RUN ln -s /config/config.ini /webgnomeapi/config.ini

EXPOSE 9899
VOLUME /config
VOLUME /webgnomeapi/models
WORKDIR /webgnomeapi/
ENTRYPOINT ["/webgnomeapi/docker_start.sh"] 
