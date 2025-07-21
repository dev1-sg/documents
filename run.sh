#!/usr/bin/env bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 scripts/generate_ecr_alpine_images_table.py > docs/docker-alpine-images-list.md
python3 scripts/generate_ecr_ci_images_table.py > docs/docker-ci-images-list.md
python3 scripts/generate_ecr_devcontainer_images_table.py > docs/docker-devcontainer-images.list.md
python3 scripts/generate_ecr_ubuntu_images_table.py > docs/docker-ubuntu-images.list.md
python3 scripts/generate_gh_repos_table.py > docs/github-repos-list.md
python3 scripts/generate_api_gateway_paths_table.py > docs/api-gateway-paths-list.md
