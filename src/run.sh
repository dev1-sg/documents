#!/usr/bin/env bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cdk bootstrap --qualifier d1sg-ecr
cdk deploy --all --ci --require-approval never
