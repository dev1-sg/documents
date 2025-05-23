#!/usr/bin/env bash

aws ecr-public describe-repositories \
  --region "us-east-1" \
  --query "repositories[].repositoryUri" \
  --output text | tr '\t' '\n' | sed 's/$/:latest/'
