#!/bin/bash
# Step 10: Immutable seal

# Note: This script requires the AWS CLI to be installed and configured.

# 10.1  Hash every artefact
 feat/chaos-pipeline
sha512sum pt.data attractor.txt falpha.txt cbmc.out norm.txt behaviour.zst > SHA512SUMS

sha512sum pt.data attractor.txt falpha.txt behaviour.zst > SHA512SUMS
 main

# 10.2  Store in an append-only log (example: QLDB)
# This command will fail if the ledger 'ChaosLog' does not exist
# or if credentials are not configured.
aws qldb send-command --ledger ChaosLog \
  --statement "INSERT INTO Evidence ?" \
  --parameters file://SHA512SUMS
