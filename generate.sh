#!/usr/bin/env sh

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 generate_ecr_base_images_table.py > docs/docker-base-images-list.md
python3 generate_ecr_ci_images_table.py > docs/docker-ci-images-list.md
python3 generate_gh_repos_table.py > docs/github-repos-list.md
