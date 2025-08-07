#!/bin/bash
uv run print.py "$(jq -c '.' testData.json)"