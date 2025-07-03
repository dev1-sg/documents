from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigw,
    Duration,
)
from constructs import Construct

class EcrImageList(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        base_lambda = self.create_lambda("base")
        ci_lambda = self.create_lambda("ci")

        api = apigw.RestApi(
            self, "EcrApi",
            rest_api_name="Ecr Image API",
            description="Routes for ECR Public Lambda functions"
        )

        images = api.root.add_resource("images")

        base = images.add_resource("base")
        base.add_method("GET", apigw.LambdaIntegration(base_lambda))

        ci = images.add_resource("ci")
        ci.add_method("GET", apigw.LambdaIntegration(ci_lambda))

    def create_lambda(self, repo_group: str) -> _lambda.Function:
        function_name = f"EcrPublicLambda-{repo_group}"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions"),
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
                "ecr-public:DescribeImages"
            ],
            resources=["*"]
        ))

        return lambda_fn
