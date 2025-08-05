#!/bin/bash
# jq '.' testData.json | uv run print.py
uv run print.py "$(jq -c '.' testData.json)"