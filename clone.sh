#!/usr/bin/env bash

git clone --filter=blob:none --no-checkout https://github.com/dev1-sg/docker-base-images.git
cd docker-base-images
git sparse-checkout init --cone
git sparse-checkout set src
git checkout
cd -

git clone --filter=blob:none --no-checkout https://github.com/dev1-sg/docker-ci-images.git
cd docker-ci-images
git sparse-checkout init --cone
git sparse-checkout set src
git checkout
cd -
