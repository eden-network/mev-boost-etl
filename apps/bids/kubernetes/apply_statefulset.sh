#!/bin/bash

# Explicitly export PROJECT_ID
export PROJECT_ID=$(gcloud config get-value project)

echo "Using PROJECT_ID: $PROJECT_ID"

# Replace environment variables in the YAML file and apply the configuration
envsubst < statefulset.yaml | kubectl apply -f -