from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigw,
    Duration,
)
from constructs import Construct

class EcrPublicListStack(Stack):
    def __init__(self, scope: Construct, id: str, *, rest_api: apigw.RestApi, images_resource: apigw.Resource, **kwargs):
        super().__init__(scope, id, **kwargs)

        base_lambda = self.create_ecr_lambda("base")
        ci_lambda = self.create_ecr_lambda("ci")

        base = images_resource.add_resource("base")
        base.add_method("GET", apigw.LambdaIntegration(base_lambda))

        ci = images_resource.add_resource("ci")
        ci.add_method("GET", apigw.LambdaIntegration(ci_lambda))

    def create_ecr_lambda(self, repo_group: str) -> _lambda.Function:
        function_name = f"EcrPublicListRepos-{repo_group}"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/ecr_list_images"),
            environment={
                "AWS_ECR_PUBLIC_ALIAS": "dev1-sg",
                "AWS_ECR_PUBLIC_REGION": "us-east-1",
                "AWS_ECR_PUBLIC_REPOSITORY_GROUP": repo_group,
            },
            timeout=Duration.seconds(30),
        )

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "ecr-public:DescribeRepositories",
                "ecr-public:DescribeImages",
            ],
            resources=["*"],
        ))

        return lambda_fn
