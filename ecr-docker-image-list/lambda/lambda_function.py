import os
import json
import boto3
from datetime import datetime
from botocore.config import Config

AWS_ECR_PUBLIC_ALIAS = os.getenv("AWS_ECR_PUBLIC_ALIAS", "dev1-sg")
AWS_ECR_PUBLIC_REGION = os.getenv("AWS_ECR_PUBLIC_REGION", "us-east-1")
AWS_ECR_PUBLIC_REPOSITORY_GROUP = os.getenv("AWS_ECR_PUBLIC_REPOSITORY_GROUP", "base")
AWS_ECR_PUBLIC_URI = f"public.ecr.aws/{AWS_ECR_PUBLIC_ALIAS}"
AWS_ECR_PUBLIC_URL = f"https://ecr-public.{AWS_ECR_PUBLIC_REGION}.amazonaws.com"

def get_ecr_client():
    return boto3.client(
        "ecr-public",
        region_name=AWS_ECR_PUBLIC_REGION,
        endpoint_url=AWS_ECR_PUBLIC_URL,
        config=Config(signature_version='v4')
    )

def get_repositories(client, prefix=None):
    repos = []
    for page in client.get_paginator("describe_repositories").paginate():
        for repo in page.get("repositories", []):
            if prefix is None or repo["repositoryName"].startswith(prefix):
                repos.append(repo)
    return repos

def get_latest_image_info(client, repository_name):
    try:
        images = client.describe_images(repositoryName=repository_name).get("imageDetails", [])
        if not images:
            return "<none>", 0

        target_images = [img for img in images if any(t != "latest" for t in img.get("imageTags", []))] or images
        latest_image = max(target_images, key=lambda img: img.get("imagePushedAt", datetime.min))

        tags = latest_image.get("imageTags", [])
        tag = next((t for t in tags if t != "latest"), tags[0] if tags else "<none>")
        size_mb = latest_image.get("imageSizeInBytes", 0) / (1024 ** 2)

        return tag, size_mb
    except Exception:
        return "<none>", 0

def lambda_handler(event, context):
    client = get_ecr_client()
    prefix = f"{AWS_ECR_PUBLIC_REPOSITORY_GROUP}/"

    repos = sorted(
        get_repositories(client, prefix=prefix),
        key=lambda r: r["repositoryName"]
    )

    results = []
    for i, repo in enumerate(repos, 1):
        name = repo["repositoryName"]
        tag, size_mb = get_latest_image_info(client, name)
        results.append({
            "number": i,
            "name": name,
            "group": name.split("/")[0] if "/" in name else "-",
            "uri": f"{AWS_ECR_PUBLIC_URI}/{name}",
            "latest_tag": tag,
            "image_size_mb": round(size_mb, 2)
        })

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "updated_at": datetime.now().astimezone().isoformat(),
            "images": results
        })
    }
