#!/bin/bash

export DBHOST=172.17.0.2
export DBPORT=3306
export DBUSER=root
export DATABASE=employees
export DBPWD=pw
export APP_COLOR=blue
export DEVELOPER_NAME_1=Sandesh
export DEVELOPER_NAME_2=Haojie
export BACKGROUND_IMAGE_LOCATION=s3://projectclo835group8/background.jpg
docker run -d --name app -p 8080:81  -v ~/.aws:/root/.aws -e DBHOST=$DBHOST -e DBPORT=$DBPORT -e DBUSER=$DBUSER -e DATABASE=$DATABASE -e DBPWD=$DBPWD \
-e APP_COLOR=$APP_COLOR -e DEVELOPER_NAME_1=$DEVELOPER_NAME_1 -e DEVELOPER_NAME_2=$DEVELOPER_NAME_2 \
-e BACKGROUND_IMAGE_LOCATION=$BACKGROUND_IMAGE_LOCATION clo835-project-app:v1.0

