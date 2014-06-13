#!/bin/sh

uwsgi -s /tmp/m2mmanager.sock -H $WORKON_HOME/m2m-manager -w wsgi:app
