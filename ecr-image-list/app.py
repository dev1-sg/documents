#!/usr/bin/env python3
import aws_cdk as cdk
from cdk.stack import EcrImageList

app = cdk.App()
EcrImageList(app, "EcrImageList")
app.synth()
