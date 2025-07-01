from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
)
from constructs import Construct

class EcrLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.create_lambda("base")
        self.create_lambda("ci")

    def create_lambda(self, repo_group: str):
        function_name = f"EcrPublicLambda-{repo_group}"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="query_ecr_images.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
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
