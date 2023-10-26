# Deployment

## Install prerequisites

Make sure you have the following installed:

- The Google Cloud SDK

## Environment setup

```bash
# Authenticate using Google Cloud
gcloud auth login

# Create a google cloud configuration for eden-data-private:
private_project='eden-data-private'
gcloud config configurations create $private_project
gcloud config set account <your_authenticated_email>
private_project_id=$(gcloud projects list --format='get(project_id)' --filter="name='$private_project'")
gcloud config set project $private_project_id

# Create a google cloud configuration for eden-data-public:
public_project='eden-data-public'
gcloud config configurations create $public_project
gcloud config set account <your_authenticated_email>
public_project_id=$(gcloud projects list --format='get(project_id)' --filter="name='$public_project'")
gcloud config set project $public_project_id
```

## Deploy artifacts

### Service account

The blocks received solution will use mev_boost_sync_agent service account created during the deployment of the mev-boost solution.

### Big Query

The `eden-data-public` project houses relay data extracted from known providers. We perform the following steps here:

- Reuse the `flashbots` dataset in `eden-data-private` and `eden-data-public`
- Create `blocks_received_staging` and `blocks-received-staging-archive` tables in `eden-data-private`
- Create a `blocks_received` table in `eden-data-public`

```bash
# Activate eden-data-private configuration
gcloud config configurations activate $private_project

# Create kline_1s_config table:
bq query --use_legacy_sql=false --project_id=$private_project_id < ./sql/schema/blocks_received.sql

# Check if blocks_received_staging_archive table exists
if bq ls $dataset_name | grep -q $table_name_staging_archive; then
    echo "Table $dataset_name.$table_name_staging_archive already exists."
else
    # Create table
    bq mk \
        --schema ./sql/schema/blocks_received_staging_archive.json \
        --table $dataset_name.$table_name_staging_archive
fi

# Activate eden-data-public configuration
gcloud config configurations activate $public_project

# Check if blocks_received table exists
if bq ls $dataset_name | grep -q $table_name; then
    echo "Table $dataset_name.$table_name already exists."
else
    # Create the table
    bq mk \
        --schema ./sql/schema/blocks_received.json \
        --time_partitioning_field block_timestamp \
        --time_partitioning_type DAY \
        --clustering_fields relay,builder_pubkey,slot \
        --table $dataset_name.$table_name
fi

# Switch back to the private project to create the metadata view
gcloud config configurations activate $private_project

# Create mev_boost_metadata view
bq query --use_legacy_sql=false "$(cat ./sql/views/blocks_received_metadata.sql)"
```

### Backload kubernetes cluster multi-node

```bash
# update the mev-boost-sync-agent service account with the iam.serviceAccountTokenCreator role so that it can be used to authenticate with the kubernetes cluster
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.serviceAccountTokenCreator \
  --member "serviceAccount:mev-boost-sync-agent@enduring-art-207419.iam.gserviceaccount.com" \
  mev-boost-sync-agent@enduring-art-207419.iam.gserviceaccount.com

```

<!-- ### Cloud Run Job

The etl app will pull data from a list of relays via a cloud run job. To create the cloud run job, we need to create a docker image and push it to the google cloud container registry using:

```bash
gcloud builds submit --config cloudbuild.production.yaml .
```

### Cloud Schedule

```bash
etl_task_name='mev-boost-etl'

# Get service uri
etl_task_uri=`gcloud run jobs list --filter="metadata.name=$etl_task_name" --uri`

# Create schedule
etl_task_cron="mev-boost-etl-cron"
gcloud scheduler jobs create http $etl_task_cron \
    --schedule "0 * * * *" \
    --uri $etl_task_uri:run \
    --http-method POST \
    --location "us-central1" \
    --oidc-service-account-email $mev_boost_svc_email
```

### Scheduled Query

Create a scheduled query to run every hour at half past. This will give enough time for the etl job to complete. Once complete, the data can be moved from `flashbots.mev_boost_staging` to `flashbots.mev_boost` with the `block_timestamp` for paritioning and `reorged` populated.

See `ethereum-etl-relay-data/sql/scheduled_queries/mev_boost_transformation.sql` for the script to use. -->
