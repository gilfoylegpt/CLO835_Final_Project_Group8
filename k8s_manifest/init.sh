#!/bin/bash

kubectl apply -f namespace.yaml
kubectl create secret docker-registry regcred \
 --docker-server=138098912972.dkr.ecr.us-east-1.amazonaws.com \
 --docker-username=AWS \
 --docker-password=$(aws ecr get-login-password --region us-east-1) \
 -n final
 
