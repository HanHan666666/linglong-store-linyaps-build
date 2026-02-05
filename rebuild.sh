#!/usr/bin/env bash

./clean.sh


ll-builder build
ll-builder export 
ll-builder export  --layer

ll-builder build -f arm64/linglong.yaml  --skip-output-check
ll-builder export -f arm64/linglong.yaml --layer 