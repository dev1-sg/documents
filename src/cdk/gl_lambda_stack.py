import os
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Duration,
)
from constructs import Construct

class GitLabPublicListStack(Stack):
    def __init__(self, scope: Construct, id: str, *, rest_api: apigw.RestApi, snippets_resource: apigw.Resource, **kwargs):
        super().__init__(scope, id, **kwargs)

        function_name = "GitLabPublicListSnippets"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/gl_list_snippets"),
            environment={
                "GITLAB_PROJECT": "dev1-sg/public/bash-scripts",
                "GITLAB_TOKEN": os.environ.get("GITLAB_TOKEN", ""),
            },
            timeout=Duration.seconds(30),
        )

        gl_resource = snippets_resource.add_resource("snippets")
        gl_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))
