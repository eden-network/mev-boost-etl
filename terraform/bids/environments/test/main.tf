provider "google" {  
  project = var.project_id
  region  = "US"
}

data "google_service_account" "mev_boost_etl" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery_bids" {
  source = "../../modules/bigquery"
  dataset_id                          = "mev_boost"

  staging_table_id                    = "bids_staging"  
  labels                              = {
    env = "production"
  }

  ui_table_id                         = "bids_ui"
  block_number_partitioning_start     = 18237000
  block_number_partitioning_end       = 18519100
  block_number_partitioning_interval  = 100
}

module "storage" {
  source = "../../modules/storage"

  bucket_name                    = "mev-boost-bids"
  location                       = "US"
  processed_bucket_lifecycle_age = 30
  bucket_iam_members             = ["serviceAccount:${data.google_service_account.mev_boost_etl.email}"]
}

# module "etl" {
#   source = "../../modules/etl"

#   job_name                     = "mev-boost-bids-transfer"
#   location                     = "us-central1"
#   container_image              = "gcr.io/enduring-art-207419/mev-boost-bids-transfer:latest"
#   service_account_email        = data.google_service_account.mev_boost_etl_sa.email
#   scheduler_job_name           = "mev-boost-bids-transfer-schedule"
#   scheduler_schedule           = "*/15 * * * *"
#   project                      = var.project_id  
# }

output "stage_table_id" {
  value = module.bigquery_bids.staging_table_id
}

output "ui_table_id" {
  value = module.bigquery_bids.ui_table_id
}

output "bucket_name" {
  value = module.storage.bucket_name
}

output "processed_bucket_name" {
  value = module.storage.processed_bucket_name
}

output "failed_bucket_name" {
  value = module.storage.failed_bucket_name
}