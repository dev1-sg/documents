import os
import json
import boto3
from datetime import datetime
from botocore.config import Config
from zoneinfo import ZoneInfo

AWS_ECR_PUBLIC_ALIAS = os.getenv("AWS_ECR_PUBLIC_ALIAS", "dev1-sg")
AWS_ECR_PUBLIC_REGION = os.getenv("AWS_ECR_PUBLIC_REGION", "us-east-1")
AWS_ECR_PUBLIC_REPOSITORY_GROUP = os.getenv("AWS_ECR_PUBLIC_REPOSITORY_GROUP", "base")

ECR_PUBLIC_URI = f"public.ecr.aws/{AWS_ECR_PUBLIC_ALIAS}"
ECR_PUBLIC_URL = f"https://ecr-public.{AWS_ECR_PUBLIC_REGION}.amazonaws.com"

TZ = ZoneInfo("Asia/Singapore")

def to_singapore_time(dt):
    if not dt:
        return None
    return dt.astimezone(TZ).replace(microsecond=0).isoformat()

def get_ecr_client():
    return boto3.client(
        "ecr-public",
        region_name=AWS_ECR_PUBLIC_REGION,
        endpoint_url=ECR_PUBLIC_URL,
        config=Config(signature_version='v4')
    )

def list_repositories(client, prefix=None):
    paginator = client.get_paginator("describe_repositories")
    for page in paginator.paginate():
        for repo in page.get("repositories", []):
            if not prefix or repo["repositoryName"].startswith(prefix):
                yield repo["repositoryName"]

def get_latest_image(client, repo_name):
    images = client.describe_images(repositoryName=repo_name).get("imageDetails", [])
    if not images:
        return "<none>", 0.0, "<none>", None

    valid_images = [img for img in images if img.get("imageTags")]
    latest = max(valid_images or images, key=lambda img: img.get("imagePushedAt", datetime.min))

    tag = next((t for t in latest.get("imageTags", []) if t != "latest"), latest.get("imageTags", [])[0])
    size_mb = round(latest.get("imageSizeInBytes", 0) / (1024**2), 2)
    sha_digest = latest.get("imageDigest", "<none>")
    pushed_at = to_singapore_time(latest.get("imagePushedAt"))

    return tag or "<none>", size_mb, sha_digest, pushed_at

def lambda_handler(event, context):
    client = get_ecr_client()
    prefix = f"{AWS_ECR_PUBLIC_REPOSITORY_GROUP}/"

    images = []
    for i, repo_name in enumerate(sorted(list_repositories(client, prefix)), 1):
        tag, size_mb, sha_digest, pushed_at = get_latest_image(client, repo_name)
        group = repo_name.split("/")[0] if "/" in repo_name else "-"
        images.append({
            "number": i,
            "image_name": repo_name,
            "image_group": group,
            "uri": f"{ECR_PUBLIC_URI}/{repo_name}",
            "latest_tag": tag,
            "latest_sha": sha_digest,
            "size_mb": size_mb,
            "uploaded_at": pushed_at
        })

    return {
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({f"docker-{prefix.strip('/')}-images": images}, indent=2)
    }
