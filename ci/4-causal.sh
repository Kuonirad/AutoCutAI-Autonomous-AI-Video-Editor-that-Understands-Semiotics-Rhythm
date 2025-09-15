#!/bin/bash
# Step 4: Causal analysis

# This script assumes a `target` executable and `default.profdata` exist.
# In a real CI, these would be artifacts from a test run.

# Generate the coverage report in JSON format
llvm-cov export -format=json -instr-profile=default.profdata target > run1.json

# Extract the basic-block hit counts into a CSV file
bb-extract run1.json > bb.csv

# Run the causal discovery script
python3 ci/4-pcmci.py >> $GITHUB_ENV
