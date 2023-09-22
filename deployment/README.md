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

One service account is needed. It will require persmissions to:

- Read and write to its staging dataset in eden-data-private
- Read and write to its production dataset in eden-data-public
- Invoke a cloud run task from cloud scheduler

This service account needs to be created in the eden-data-private project.

```bash
# Make sure eden-data-private configuration is activated
gcloud config configurations activate $private_project

# Create service account
mev_boost_svc_name='mev-boost-sync-agent'
gcloud iam service-accounts create $mev_boost_svc_name \
    --description="Service account with cloud run permissions and read/write access to mev_boost dataset in eden-data-private, read/write access to mev_boost dataset in eden-data-public" \
    --display-name="$mev_boost_svc_name"

# Create custom role
mev_boost_sync_role='mev-boost-sync-role'
gcloud iam roles create $mev_boost_sync_role \
    --project=$private_project \
    --file=./deployment/mev_boost_sync_role_private.yaml

# Get the service account email address
mev_boost_svc_email=$(gcloud iam service-accounts list --format='get(email)' --filter="displayName=$mev_boost_svc_name")

# Add the service account to the newly created role
gcloud projects add-iam-policy-binding $private_project \
  --member serviceAccount:$mev_boost_svc_email \
  --role projects/$private_project/roles/$mev_boost_sync_role

# Switch to eden-data-public configuration
gcloud config configurations activate $public_project

# Create custom role using the same name
gcloud iam roles create $mev_boost_sync_role \
    --project=$public_project \
    --file=./deployment/mev_boost_sync_role_public.yaml

# Add the service account we created in eden-data-private to the newly created role in eden-data-public. It's fine to re-use the same service account across projects.
gcloud projects add-iam-policy-binding $public_project \
  --member serviceAccount:$mev_boost_svc_email \
  --role projects/$public_project/roles/$mev_boost_sync_role
```

### Big Query

The eden-data-public project houses relay data extracted from known providers. We perform the following steps here:

- Create a mev-boost dataset in eden-data-private and eden-data-public
- Create a slots-staging table in eden-data-private
- Create a slots table in eden-data-public

```bash
dataset_name='flashbots'
table_name='mev_boost'
table_name_staging='mev_boost_staging'

# Activate eden-data-private configuration
gcloud config configurations activate $private_project

# Check if flashbots dataset exists
if bq ls -d $dataset_name; then
    echo "Dataset $dataset_name already exists."
else
    # Create dataset
    bq mk -d \
        --location "US" \
        --description "Dataset for housing mev-boost staging data" \
        $dataset_name
fi

# Check if mev_boost_staging table exists
if bq ls $dataset_name | grep -q $table_name_staging; then
    echo "Table $dataset_name.$table_name_staging already exists."
else
    # Create table
    bq mk \
        --schema ./sql/schema/mev_boost_staging.json \
        --table $dataset_name.$table_name_staging
fi

# Get current dataset permissions and dump to file
bq show \
    --format=prettyjson \
    $private_project:$dataset_name > perms_flashbots_dataset_private.json

# Add the following to the `access` section in `perms_flashbots_dataset_private.json` NOTE (make sure you change $mev_boost_svc_email variable with the actual value before pasting):
```

```json
{
    "role": "WRITER",
    "userByEmail": $mev_boost_svc_email
}
```

```bash
# Update the private flashbots dataset to include the new permissions:

bq update \
    --source perms_flashbots_dataset_private.json \
    $private_project:$dataset_name

# Activate eden-data-public configuration
gcloud config configurations activate $public_project

# Check if flashbots dataset exists
if bq ls -d $dataset_name; then
    echo "Dataset $dataset_name already exists."
else
    # Create dataset
    bq mk -d \
        --location "US" \
        --description "Dataset for housing mev-boost data" \
        $dataset_name
fi

# Check if mev_boost table exists
if bq ls $dataset_name | grep -q $table_name; then
    echo "Table $dataset_name.$table_name already exists."
else
    # Create the table
    bq mk \
        --schema ./sql/schema/mev_boost.json \
        --time_partitioning_field block_timestamp \
        --time_partitioning_type DAY \
        --clustering_fields relay,builder_pub_key,slot \
        --table $dataset_name.$table_name
fi

# Get current dataset permissions and dump to file
bq show \
    --format=prettyjson \
    $public_project:$dataset_name > perms_flashbots_dataset_public.json

# Add the following to the `access` section in `perms_flashbots_dataset_public.json` NOTE (make sure you change $mev_boost_svc_email variable with the actual value before pasting):
```

```json
{
    "role": "WRITER",
    "userByEmail": $mev_boost_svc_email
}
```

```bash
# Update the public flashbots dataset to include the new permissions:

bq update \
    --source perms_flashbots_dataset_public.json \
    $public_project:$dataset_name
```

### Cloud Run Task

The etl app will pull data from a list of relays via a cloud run task.

```bash
etl_task_name=mev-boost-etl

# Deploy cloud run task

gcloud run deploy $etl_task_name \
    --source . \
    --service-account $mev_boost_svc_email \
    --env-vars-file ./.env.production.yaml \
    --no-allow-unauthenticated
```

### Cloud Schedule

```bash
# Get service uri

sync_service_uri=`gcloud run tasks list --filter="metadata.name=$etl_task_name" --format="value(status.address.url)"`

# Create schedule

gcloud scheduler jobs create http flashbots-blocks-sync-hourly \
    --schedule "0 * * * *" \
    --uri "$sync_service_uri/sync" \
    --http-method POST \
    --location "us-central1" \
    --oidc-service-account-email $readwrite_svc_email
```

### Scheduled Query

Create a scheduled query to run every hour at half past. This will give enough time for the batch load into the staging table to complete. Once complete, the data can be moved from `flashbots.blocks_staging` to `flashbots.blocks` with the `block_timestamp` for paritioning.

See `../sql/scheduled_queries/flashbots_etl_load.sql` for the script to use.
