#!/bin/bash

redis-server --daemonize yes
/opt/conda/bin/pserve /webgnomeapi/config.ini
