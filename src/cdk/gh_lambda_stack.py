from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Duration,
)
from constructs import Construct

class GitHubPublicListStack(Stack):
    def __init__(self, scope: Construct, id: str, *, rest_api: apigw.RestApi, repos_resource: apigw.Resource, **kwargs):
        super().__init__(scope, id, **kwargs)

        function_name = "GitHubPublicListRepos"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/gh_list_repos"),
            environment={
                "GITHUB_ORG": "dev1-sg",
            },
            timeout=Duration.seconds(30),
        )

        gh_resource = repos_resource.add_resource("repos")
        gh_resource.add_method("GET", apigw.LambdaIntegration(lambda_fn))
