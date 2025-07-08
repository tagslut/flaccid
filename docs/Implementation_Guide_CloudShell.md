# FLACCID Pipeline: Cloud Shell Quickstart

## Prerequisites
- A GCP project with billing enabled.
- `gcloud` CLI installed (Cloud Shell has it by default).
- Your user has `roles/owner` or `roles/editor` on the project.

## 1. Set Up

```bash
# 1. Configure project
gcloud config set project YOUR_PROJECT_ID

# 2. Clone this repo
git clone <your-repo-url>
cd flaccid

# 3. Create source bucket & SA
export BUCKET=flunkyard
export SA=flaccid-runtime-sa
export SA_EMAIL=${SA}@$(gcloud config get-value project).iam.gserviceaccount.com

gsutil mb -l US-CENTRAL1 gs://$BUCKET
gcloud iam service-accounts create $SA --display-name "FLACCID Runner"
gsutil iam ch serviceAccount:$SA_EMAIL:objectAdmin gs://$BUCKET
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/iam.serviceAccountUser"
