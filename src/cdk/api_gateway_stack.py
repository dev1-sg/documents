from aws_cdk import Stack, aws_apigateway as apigw, aws_certificatemanager as acm
from constructs import Construct

class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        cert = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            certificate_arn="arn:aws:acm:ap-southeast-1:439152312044:certificate/00b71ea9-6363-44a8-8223-77a60ac200f3"
        )

        self.rest_api = apigw.RestApi(
            self, "EcrPublicApi",
            rest_api_name="EcrPublicApi",
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

        self.images_resource = self.rest_api.root.add_resource("images")

        self.repos_resource = self.rest_api.root.add_resource("repos")
