# MEV-Boost Payloads ETL

This repository houses the code for collecting and processing payloads data hourly from all MEV-boost relays in the ecosystem.

## Overview

The system is designed to:

- Collect latest payloads: Runs every hour to fetch the latest bids data and push tem to a BigQuery table.
- Process data: Transform and clean data for storage and analysis.
- Store data: Save processed data into cloud storage and BigQuery tables.

## Repository Structure

- /src: etl application
  - /api: Code for extracting and reading data from MEV-boost relays.
  - /bigquery: Package for modules interfacing with BigQuery (writing and managing data).
  - /cloud_storage: Package for modules managing data in cloud storage.
  - /tests: End-to-end and integration tests.
  - main_extract.py: Standalone app for data extraction process to cloud storage.
  - main_full.py: Full etl app; the complete data processing pipeline.
  - main_load.py: Standalone app for loading data from the staging table to the final table.
  - main_transfer.py: Standalone app for transferring staged data from cloud storage to bigquery.

## Prerequisites

- Google Cloud SDK
- Docker
- Access to Google Cloud services

## Building and Pushing Docker Images

- Use Google Cloud Build for creating and managing Docker images as specified in the cloudbuild YAML files.

Example:

```bash
gcloud builds submit --config ./cloudbuild.yaml .
```

Note: neccesary environment variables are set in the terraform configuration that deploys the cloud run app.

## Additional Resources

- For detailed infrastructure setup using Terraform, refer to the additional README in the parent folder.
