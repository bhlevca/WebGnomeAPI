WebGnomeAPI
===========

A web service that interfaces with py_gnome


### Deployment Issues

#### websockets
even after configuring apache’s mod_proxy websocket tunnel as others online have reported working I was unable to make a websocket connection.

server logs reported something that seemed like the gevent server was asuming a socket was created and initialized before it actually was. as though upgrade requests were not getting through. More investiation is needed.

This issue coupled with the requirement of https means that the python server itself needs to handle the ssl encryption and be given direct access to the web through a port of ip of it's own.

### Socket.IO
Due to the fact that we're using version 0.9 of the socket.io package running the application under a directory (such as gnome.orr.noaa.gov/gnomeapi) does not work.
It will asume gnome.orr.noaa.gov/socket.io still and there is no way to adjust this without modifying the library.
In addition if the client is running on a port for some reason, localhost:8080 for example. It will project this port on to it's destination server, https://gnome.orr.noaa.gov/gnomeapi will become https://gnome.orr.noaa.gov:8080/socket.io/. The current solution to this last bit is to always provide a port to the client's configuration even if it's redundant... https://gnome.orr.noaa.gov:443/gnomeapi

Until we upgrade gevent we're stuck with 0.9 and this issue.
