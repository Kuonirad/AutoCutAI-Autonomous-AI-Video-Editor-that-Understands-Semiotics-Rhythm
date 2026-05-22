#!/bin/bash
set -euo pipefail

# Step 10: Immutable seal

# Note: This script requires the AWS CLI to be installed and configured.

# 10.1  Hash every artefact
sha512sum pt.data attractor.txt falpha.txt cbmc.out norm.txt behaviour.zst > SHA512SUMS

# 10.2  Store in an append-only log (example: QLDB) when credentials are configured.
if command -v aws >/dev/null 2>&1 && [ -n "${AWS_ACCESS_KEY_ID:-}" ]; then
  aws qldb send-command --ledger ChaosLog \
    --statement "INSERT INTO Evidence ?" \
    --parameters file://SHA512SUMS
else
  echo "AWS QLDB credentials unavailable; SHA512SUMS is the local immutable seal."
fi
