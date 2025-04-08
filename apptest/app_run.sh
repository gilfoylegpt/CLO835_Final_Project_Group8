#!/bin/bash

export DBHOST=172.17.0.2
export DBPORT=3306
export DBUSER=root
export DATABASE=employees
export DBPWD=pw
export APP_COLOR=blue
docker run -d --name app -p 8080:81 -e DBHOST=$DBHOST -e DBPORT=$DBPORT -e DBUSER=$DBUSER -e DATABASE=$DATABASE -e DBPWD=$DBPWD -e APP_COLOR=$APP_COLOR clo835-project-app:v1.0

