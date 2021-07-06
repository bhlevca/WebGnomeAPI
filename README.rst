###########
WebGnomeAPI
###########

A web service that interfaces with py_gnome

Installing / Running
====================

webgnomeapi is a python package. To run it you need to install the dependencies, install the package, then run it:

Dependencies
------------

The webgnomeAPI is pretty worthless without py_gnome, and py_gnome is easiest to get going with conda and conda-forge.

conda
.....

If you are using a conda based system you can install most of the dependencies with conda. This requires the conda-forge channel)::

    conda config --add channels conda-forge

(You probably already did that for py_gnome)

Install the requirements::

  conda install --file conda_requirements.txt

Not quite everything is available as conda packages, so you need to install a few more with pip::

    pip install -r pip_requirements.txt

Should do it.

To run the API, you also need a redis server. If you have one installed from a another source, that will work fine. If not, then you can use conda to get it::

  conda install redis


pip
...

In theory, you can install everything webgnomeapi needs with pip, except py_gnome and its dependencies. You can give that a try with::

    pip install -r conda_requirements.txt -r pip_requirements.txt

Installing the server
---------------------

Installing the server from code can be done the usual way for a python package::

  pip install -e ./

or::

  python setup.py develop


Testing the Server
------------------

In order to run webgnomeapi, you need a redis server running first. redis can be installed with conda on OS-X (and probably Windows and Linux -- if you test it and it works, please update this doc.). Once installed, you should be able to run a redis server with::

  redis-server

Once redis is running, you should be able to run the tests with::

  pytest webgnome_api/tests


Running the Server
------------------

First start up a Redis server with::

  redis-server

webgnomeapi is a Pyramid application that can be run with the paste uwsgi server::

  pserve config-example.ini


Deployment Issues
=================

websockets
----------

Even after configuring apache’s mod_proxy websocket tunnel as others online have reported working, I was unable to make a websocket connection.

Server logs reported something that seemed like the gevent server was assuming a socket was created and initialized before it actually was, as though upgrade requests were not getting through.
More investigation is needed.

This issue coupled with the requirement of https means that the python server itself needs to handle the ssl encryption and be given direct access to the web through a port of ip of it's own.

Socket.IO
---------

Due to the fact that we're using version 0.9 of the socket.io package running the application under a directory (such as gnome.orr.noaa.gov/gnomeapi) does not work.
It will assume gnome.orr.noaa.gov/socket.io still and there is no way to adjust this without modifying the library.

In addition if the client is running on a port for some reason, localhost:8080 for example. It will project this port on to its destination server,
``https://gnome.orr.noaa.gov/gnomeapi`` will become ``https://gnome.orr.noaa.gov:8080/socket.io/``.
The current solution to this last bit is to always provide a port to the client's configuration even if it's redundant ... ``https://gnome.orr.noaa.gov:443/gnomeapi``


Until we upgrade gevent we're stuck with 0.9 and this issue.
