from aws_cdk import App
from cdk.api_gateway_stack import ApiGatewayStack
from cdk.api_gateway_stack import ApiGatewayListStack
from cdk.ecr_lambda_stack import EcrPublicListStack
from cdk.gh_lambda_stack import GitHubPublicListStack

app = App()

api_stack = ApiGatewayStack(app, "ApiGatewayStack")

ApiGatewayListStack(
    app, "ApiGatewayListStack",
    rest_api=api_stack.rest_api,
    apis_resource=api_stack.apis_resource
)

EcrPublicListStack(
    app, "EcrPublicListStack",
    rest_api=api_stack.rest_api,
    images_resource=api_stack.images_resource
)

GitHubPublicListStack(
    app, "GitHubPublicListStack",
    rest_api=api_stack.rest_api,
    repos_resource=api_stack.repos_resource
)

app.synth()
