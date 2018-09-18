###########
WebGnomeAPI
###########

A web service that interfaces with py_gnome

Installing / Running
====================

webgnomeapi is a python package. To run it you need to install the depedencies, install the package, then run it:

Depedencies
-----------

**pip** You can pip install everything webgnomeapi needs (except py_gnome) with pip::

    pip install -r requirements.txt

**conda** If you are using a conda based system you can install most of the dependencies with conda (this requires the conda-forge channel)::

  conda install --file conda_requirements.txt

But not quite everytihng is avaialable as conda packages, so yoou need to install a few more with pip::

    pip install -r requirements.txt

Should do it.

Installing the server
---------------------

Installing can abe done the usual way for a python package::

  pip install ./

Testing the Server
------------------

In order to run webgnomeapi, you need a redis server running first. redis can be installed with conda on OS-X (and probably Windows and Linux -- if you test it and it works, please update this doc.). ONce installed, you should be able to run a redis serve with::

  redis-server

Once redis is running, you should be able to run the tests with::

  py.test webgnome_api/tests


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

Even after configuring apache’s mod_proxy websocket tunnel as others online have reported working I was unable to make a websocket connection.

Server logs reported something that seemed like the gevent server was asuming a socket was created and initialized before it actually was. as though upgrade requests were not getting through. More investiation is needed.

This issue coupled with the requirement of https means that the python server itself needs to handle the ssl encryption and be given direct access to the web through a port of ip of it's own.

Socket.IO
---------

Due to the fact that we're using version 0.9 of the socket.io package running the application under a directory (such as gnome.orr.noaa.gov/gnomeapi) does not work.
It will asume gnome.orr.noaa.gov/socket.io still and there is no way to adjust this without modifying the library.

In addition if the client is running on a port for some reason, localhost:8080 for example. It will project this port on to its destination server, https://gnome.orr.noaa.gov/gnomeapi will become https://gnome.orr.noaa.gov:8080/socket.io/. The current solution to this last bit is to always provide a port to the client's configuration even if it's redundant... https://gnome.orr.noaa.gov:443/gnomeapi

Until we upgrade gevent we're stuck with 0.9 and this issue.
