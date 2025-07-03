#!/usr/bin/env python3
import aws_cdk as cdk
from cdk.stack import EcrLambdaStack

app = cdk.App()
EcrLambdaStack(app, "EcrLambdaStack")
app.synth()
