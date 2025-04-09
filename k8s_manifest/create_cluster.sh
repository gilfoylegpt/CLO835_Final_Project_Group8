#!/bin/bash

eksctl create cluster -f eks_config.yaml 
aws eks update-kubeconfig --name clo835  --region us-east-1
eksctl create addon --name aws-ebs-csi-driver --cluster clo835 --service-account-role-arn arn:aws:iam::138098912972:role/LabRole --force
# eksctl utils associate-iam-oidc-provider --region us-east-1 --cluster clo835 --approve