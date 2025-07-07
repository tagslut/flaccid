#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
JOB_NAME="flaccid-job"
SA_EMAIL="flaccid-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com"

if [[ -z "$PROJECT_ID" ]]; then
  echo "❌  Please set your project:  gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

echo "🚀 Deploying FLACCID Job"
echo " • Project: $PROJECT_ID"
echo " • Region:  $REGION"
echo " • Job:     $JOB_NAME"
echo " • SA:      $SA_EMAIL"

gcloud run jobs deploy "$JOB_NAME" \
  --source . \
  --region "$REGION" \
  --service-account "$SA_EMAIL" \
  --task-timeout "3600s" \
  --set-env-vars="GCLOUD_PROJECT=${PROJECT_ID}" \
  --quiet

echo "✅ Deployed. To run:"
echo "  gcloud run jobs execute $JOB_NAME \\
    --region $REGION --wait \\
    --args=\"analyze,--source-uri=gs://YOUR_BUCKET/path,--project-id=$PROJECT_ID,--manifest-path=gs://YOUR_BUCKET/reports/plan.parquet\""
