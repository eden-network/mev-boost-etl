# MEV Boost ETL

This repository contains the code and infrastructure for managing the extraction, transformation, and loading (ETL) processes for MEV-Boost data, including both bids and payloads. The system handles real-time data collection, processing, and storage, as well as historical data backloading using Kubernetes.

## Overview

The system is designed to:

- Collect Latest Data: Runs at regular intervals to fetch the latest bids and payloads data.
- Process Data: Transform and clean data for storage and analysis.
- Store Data: Save processed data into cloud storage and BigQuery tables.
- Backload Historical Bids Data: Utilizes Kubernetes to manage a cluster of nodes for parallel processing, enabling efficient backloading of extensive historical data.

## Repository Structure

### Applications

- /apps: Contains the specific applications for bids and payloads data.
  - /bids: Handles the extraction and processing of bids data.
  - /payloads: Handles the extraction and processing of payloads data.

### Infrastructure

- /terraform: Contains Terraform configurations for managing the infrastructure across different environments.
  - /\_shared: Shared infrastructure components.
    - /environments: Environment-specific configurations (production, test).
    - /modules: Reusable Terraform modules.
      - /bigquery: BigQuery-related infrastructure.
      - /service_account: Service account configurations.
  - /bids: Infrastructure specific to the bids application.
    - /environments: Environment-specific configurations (production, test).
    - /modules: Reusable Terraform modules.
      - /bigquery: BigQuery-related infrastructure.
      - /etl: ETL process-related infrastructure (cloud run, cloud scheduler etc).
      - /storage: Cloud storage infrastructure.
  - /payloads: Infrastructure specific to the payloads application.
    - /environments: Environment-specific configurations (production, test).
    - /modules: Reusable Terraform modules.
      - /bigquery: BigQuery-related infrastructure.
      - /etl: ETL process-related infrastructure (cloud run, cloud scheduler etc).
      - /storage: Cloud storage infrastructure.
  - /bids_backload: Infrastructure specific to the bids_backloading solution.
    - /environments: Environment-specific configurations (test-only).
    - /modules: Reusable Terraform modules.
      - /bigquery: BigQuery-related infrastructure.
      - /k8s_backload: Kubernetes-related infrastructure and configuration.

## Prerequisites

- Google Cloud SDK
- Docker
- Kubernetes CLI (kubectl)
- Access to Google Cloud services

## Terraform

The following is an example deployment using the terraform configurations in this repository:

```bash
cd ./terraform/{app}/environments/{environment}

# initialize terraform
terraform init

# plan the deployment (check everything is as expected before)
terraform plan

# before the deployment
terraform apply

# destroy the deployment (when/if no longer needed)
terraform destroy
```
