FROM pygnome

ARG CI_COMMIT_BRANCH
RUN set

RUN yum update -y \
    && yum install -y redis

RUN ls .
COPY ./ /webgnomeapi/

RUN conda install mamba

RUN ls webgnomeapi
RUN ls webgnomeapi/libgoods
RUN ls webgnomeapi/model_catalogs

RUN mamba install -y \
       --file webgnomeapi/conda_requirements.txt \
       --file webgnomeapi/libgoods/conda_requirements.txt \
       --file webgnomeapi/model_catalogs/conda-requirements.txt

RUN pip install -r webgnomeapi/model_catalogs/pip-requirements.txt

RUN cd webgnomeapi/model_catalogs && pip install .
RUN cd webgnomeapi/libgoods && pip install .
RUN cd webgnomeapi && pip install .

RUN cd webgnomeapi && python setup.py compilejson

RUN mkdir /config
RUN cp /webgnomeapi/gnome-deploy/config/webgnomeapi/config.ini /config/config.ini
RUN ln -s /config/config.ini /webgnomeapi/config.ini

EXPOSE 9899
VOLUME /config
VOLUME /models
WORKDIR /webgnomeapi/
ENTRYPOINT ["/webgnomeapi/docker_start.sh"]
