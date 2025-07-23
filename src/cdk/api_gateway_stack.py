from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_certificatemanager as acm,
    Duration,
)
from constructs import Construct

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        cert = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            certificate_arn="arn:aws:acm:ap-southeast-1:439152312044:certificate/00b71ea9-6363-44a8-8223-77a60ac200f3"
        )

        self.rest_api = apigw.RestApi(
            self, "ListPublicResourcesApi",
            rest_api_name="ListPublicResourcesApi",
            endpoint_types=[apigw.EndpointType.REGIONAL],
            deploy_options=apigw.StageOptions(stage_name="prod")
        )

        apigw.DomainName(
            self, "CustomDomain",
            domain_name="api.dev1-sg.com",
            certificate=cert,
            endpoint_type=apigw.EndpointType.REGIONAL,
            mapping=self.rest_api,
            base_path="v1/public"
        )

        self.apis_resource = self.rest_api.root.add_resource("apis")
        self.images_resource = self.rest_api.root.add_resource("images")
        self.repos_resource = self.rest_api.root.add_resource("repos")
        self.snippets_resource = self.rest_api.root.add_resource("snippets")

class ApiGatewayListStack(Stack):
    def __init__(self, scope: Construct, id: str, *, rest_api: apigw.RestApi, apis_resource: apigw.Resource, **kwargs):
        super().__init__(scope, id, **kwargs)

        function_name = "ApiGatewayListApis"

        lambda_fn = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions/api_list_paths"),
            timeout=Duration.seconds(30),
        )

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["apigateway:GET"],
            resources=["*"],
        ))

        rest = apis_resource.add_resource("rest")
        rest.add_method("GET", apigw.LambdaIntegration(lambda_fn))
