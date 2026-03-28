#!/usr/bin/env bash

# 失败后终止继续执行
set -euo pipefail

./clean.sh


ll-builder build
ll-builder export 
ll-builder export  --layer

ll-builder build -f arm64/linglong.yaml  --skip-output-check
ll-builder export -f arm64/linglong.yaml --layer 