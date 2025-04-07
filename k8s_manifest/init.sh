#!/bin/bash

kubectl apply -f namespace.yaml
kubectl create secret docker-registry regcred \
 --docker-server=138098912972.dkr.ecr.us-east-1.amazonaws.com \
 --docker-username=AWS \
 --docker-password=$(aws ecr get-login-password --region us-east-1) \
 -n final
 
 kubectl apply -f configmap.yaml
 kubectl apply -f mysql-secret.yaml 
 kubectl apply -f mysql-pvc.yaml
 kubectl apply -f serviceaccount.yaml
 kubectl apply -f mysql-deployment.yaml
 kubectl apply -f mysql-service.yaml
 kubectl apply -f app-deployment.yaml
 kubectl apply -f app-service.yaml
 