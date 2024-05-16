# MEV-Boost Bids ETL

This repository houses the code for collecting and processing bids data from all MEV-boost relays in the ecosystem, facilitating both hourly loading and slot rangebound backloading.

## Overview

The system is designed to:

- Collect latest bids: Runs every hour to fetch the latest bids data and push them to a BigQuery table.
- Process data: Transform and clean data for storage and analysis.
- Store data: Save processed data into cloud storage and BigQuery tables.
- Backload historical bids: Utilizes Kubernetes to manage a cluster of nodes for parallel processing enabling efficient backloading of extensive historical data.

## Repository Structure

- /src: etl application
  - /api: Code for extracting and reading data from MEV-boost relays.
  - /bigquery: Package for modules interfacing with BigQuery (writing and managing data).
  - /cloud_storage: Package for modules managing data in cloud storage.
  - /tests: End-to-end and integration tests.
- /kubernetes: Kubernetes YAML configurations for deployment of backloading solution.
- /cloudbuild: Cloud Build configurations for building and deploying the various apps.

## Prerequisites

- Google Cloud SDK
- Docker
- Kubernetes CLI (kubectl)
- Access to Google Cloud services

## Building and Pushing Docker Images

- Use Google Cloud Build for creating and managing Docker images as specified in the cloudbuild YAML files.

Example:

```bash
gcloud builds submit --config ./cloudbuild/bau.yaml .
```

Note: neccesary environment variables are set in the terraform configuration that deploys the cloud run app.

## Bids Backload Walkthrough

Things to do:

- Ensure your `gcloud` config is set to the correct project
- Deploy the /\_shared and /bids terraform configuration to create necessary infrastructure (see parent readme for example)
- Deploy /bids_backload terraform configuration
- Connect to deployed cluster (see below)
- Ensure the configuration table is configured to provide a slot range for each node (see /terraform/bids_backload/modules/bigquery/config.sql). i.e. if you've deployed 20 nodes, you'll need 20 config entries.
- Deploy the stateful set (see deployment)
- Monitor
- Manually transfer new bids from cloud storage to bigquery.
  - Run the transfer cloud run app that get's deployed as part of the /bids_backload infrastructure
  - See /terraform/bids/modules/bigquery/load_bids.sql for how to transfer for to finalised table (requires editing)

### Connect to cluster:

```bash
gcloud container clusters get-credentials mev-boost-gke-cluster --zone us-central1-a

# check that you can connect to the cluster
kubectl get nodes
```

### Deployment

```bash
# build and push the docker image using gcloud
gcloud builds submit --config ./cloudbuild/backload.yaml .

# run the bash script to apply the stateful set to the cluster
./apply_statefulset.sh
```

### Monitor the deployment

Using kubernetes:

```bash
# check the status of the pods
kubectl get pods -o wide

# check the logs of the pod
kubectl logs -f mev-boost-bids-statefulset-0

# check the status of the statefulset
kubectl get statefulset

# check the status of the service
kubectl get service
```

Using gcp logging. Use the following filter:

```
resource.labels.location="us-central1-a"
AND resource.labels.cluster_name="mev-boost-gke-cluster"
AND resource.labels.namespace_name=default
AND severity>=INFO
```

### Delete the deployment

```bash
./delete_statefulset.sh
```
