from aws_cdk import App
from cdk.api_gateway_stack import ApiGatewayStack
from cdk.ecr_lambda_stack import EcrImageListStack
from cdk.gh_lambda_stack import GitHubRepoListStack

app = App()

api_stack = ApiGatewayStack(app, "ApiGatewayStack")

EcrImageListStack(
    app, "EcrImageListStack",
    rest_api=api_stack.rest_api,
    images_resource=api_stack.images_resource
)

GitHubRepoListStack(
    app, "GitHubRepoListStack",
    rest_api=api_stack.rest_api,
    repos_resource=api_stack.repos_resource
)

app.synth()
