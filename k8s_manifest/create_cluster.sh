#!/bin/bash

eksctl create cluster -f eks_config.yaml 
aws eks update-kubeconfig --name clo835  --region us-east-1
