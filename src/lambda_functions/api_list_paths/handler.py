import os
import json
import boto3
import urllib.parse
from botocore.config import Config

def get_boto3_client():
    session = boto3.Session()
    region = session.region_name
    rest_client = session.client("apigateway")
    http_client = session.client("apigatewayv2")
    return rest_client, http_client, region

def get_custom_domain_mappings(http_client):
    domain_map = {}
    domains = http_client.get_domain_names().get("Items", [])
    for domain in domains:
        mappings = http_client.get_api_mappings(DomainName=domain["DomainName"]).get("Items", [])
        for mapping in mappings:
            domain_map.setdefault(mapping["ApiId"], []).append({
                "domain": domain["DomainName"],
                "mappingKey": mapping.get("ApiMappingKey", ""),
                "fullPath": f"https://{domain['DomainName']}/{mapping.get('ApiMappingKey', '')}".rstrip("/")
            })
    return domain_map

def collect_rest_apis(rest_client, region, domain_map):
    rest_api = []
    rest_apis = rest_client.get_rest_apis().get("items", [])
    for api in rest_apis:
        api_id = api["id"]
        name = api["name"]
        description = api.get("description")

        resources = rest_client.get_resources(restApiId=api_id).get("items", [])
        routes = []
        for res in resources:
            path = res["path"]
            methods = res.get("resourceMethods", {}).keys()
            for method in methods:
                routes.append({"method": method, "path": path})

        stages = rest_client.get_stages(restApiId=api_id).get("item", [])
        invoke_urls = [
            {
                "stage": stage["stageName"],
                "url": f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage['stageName']}/"
            } for stage in stages
        ]

        full_paths = []
        mappings = domain_map.get(api_id, [])
        for mapping in mappings:
            for route in routes:
                route_path = route["path"].lstrip("/")
                full_url = urllib.parse.urljoin(mapping["fullPath"].rstrip("/") + "/", route_path)
                full_paths.append(full_url)

        rest_api.append({
            "apiId": api_id,
            "type": "REST",
            "name": name,
            "description": description,
            "routes": routes,
            "invokeUrls": invoke_urls,
            "customDomains": mappings,
            "fullPaths": full_paths
        })

    return rest_api

def lambda_handler(event, context):
    rest_client, http_client, region = get_boto3_client()
    domain_map = get_custom_domain_mappings(http_client)
    rest_api = collect_rest_apis(rest_client, region, domain_map)

    return {
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"rest_apis": rest_api}, indent=2)
    }
