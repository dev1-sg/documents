#!/usr/bin/env python3
import aws_cdk as cdk
from ecr_lambda.ecr_lambda_stack import EcrLambdaStack

app = cdk.App()
EcrLambdaStack(app, "EcrLambdaStack")
app.synth()
