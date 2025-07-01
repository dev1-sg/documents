import os
import json
import boto3
import glob
import docker
import base64
from dotenv import load_dotenv
import nbformat as nbf

load_dotenv(override=False)

def get_env(key, default=None):
    return os.getenv(key, default)

AWS_ECR_PUBLIC_ALIAS = get_env("AWS_ECR_PUBLIC_ALIAS", "dev1-sg")
AWS_ECR_PUBLIC_REGION = get_env("AWS_ECR_PUBLIC_REGION", "us-east-1")
AWS_ECR_PUBLIC_REPOSITORY_GROUP = get_env("AWS_ECR_PUBLIC_REPOSITORY_GROUP", "base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_READMME_PATH = get_env("OUTPUT_READMME_PATH", os.path.join(BASE_DIR, "../src"))
OUTPUT_READMME_FILE = "inspect-image.ipynb"

def login_to_ecr_public(region_name="us-east-1"):
    ecr = boto3.client("ecr-public", region_name=region_name)
    token = ecr.get_authorization_token()["authorizationData"]["authorizationToken"]
    decoded = base64.b64decode(token).decode()
    username, password = decoded.split(":", 1)

    client = docker.from_env()
    login_response = client.login(
        username=username,
        password=password,
        registry="public.ecr.aws"
    )
    print("[INFO] Logged in to ECR Public:", login_response)

def pull_image(client, image_name):
    low_level = docker.APIClient()
    try:
        for line in low_level.pull(image_name, stream=True, decode=True):
            if 'error' in line:
                print(f"[ERROR] Pull error: {line['error']}")
        image = client.images.get(image_name)
        print("[DEBUG] Pull complete")
        return image
    except docker.errors.APIError as e:
        print(f"[ERROR] Failed to pull image {image_name}: {e}")
        raise

def get_arch(client, image):
    arch = client.images.get(image.id).attrs.get("Architecture", "unknown")
    print(f"[DEBUG] Image architecture: {arch}")
    return arch

def run_cmd(client, image, cmd, arch):
    print(f"[DEBUG] Running command '{cmd}' on image '{image}' with arch '{arch}'")
    try:
        output = client.containers.run(image, cmd, remove=True, platform=f"linux/{arch}")
        return output.decode().strip().splitlines()
    except docker.errors.ContainerError as e:
        print(f"[ERROR] Container command error:\n{e.stderr.decode() if e.stderr else str(e)}")
        raise
    except docker.errors.APIError as e:
        print(f"[ERROR] Docker API error during command: {e}")
        raise

def get_pkgs(client, image, arch):
    try:
        return run_cmd(client, image, "apk info", arch)
    except docker.errors.DockerException:
        try:
            return run_cmd(client, image, "sh -c 'apt list | tail -n +2'", arch)
        except docker.errors.DockerException as e:
            print(f"[WARN] Both apk and apt commands failed: {e}")
            return []

def render_container_data(container_data):
    return f"container_data = {json.dumps(container_data, indent=4)}"

def main():
    client = docker.from_env()
    login_to_ecr_public()

    for dir_path in glob.glob(f"{OUTPUT_READMME_PATH}/*/"):
        image_name = os.path.basename(os.path.normpath(dir_path))
        image_uri = f"public.ecr.aws/{AWS_ECR_PUBLIC_ALIAS}/{AWS_ECR_PUBLIC_REPOSITORY_GROUP}/{image_name}:latest"
        notebook_path = os.path.join(dir_path, OUTPUT_READMME_FILE)

        print(f"[INFO] Processing image {image_name}")

        try:
            image = pull_image(client, image_uri)
            arch = get_arch(client, image)

            os_release_info = run_cmd(client, image_uri, "cat /etc/os-release", arch)
            os_env_vars = run_cmd(client, image_uri, "env", arch)
            os_pkg_bin = get_pkgs(client, image_uri, arch)
            os_pkg_local_bin = run_cmd(client, image_uri, "ls -1 /usr/local/bin", arch)

            container_data = {
                "image_uri": image_uri,
                "os_release_info": os_release_info,
                "os_env_vars": os_env_vars,
                "os_pkg_bin": os_pkg_bin,
                "os_pkg_local_bin": os_pkg_local_bin
            }

            code_cell_content = render_container_data(container_data)

            nb = nbf.v4.new_notebook()
            nb.cells.append(nbf.v4.new_code_cell(code_cell_content))

            with open(notebook_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)

            print(f"[INFO] Wrote notebook for {image_name}")

        except Exception as e:
            print(f"[ERROR] Failed processing {image_name}: {e}")

if __name__ == "__main__":
    main()
