provider "google" {  
  project = var.project_id
  region  = "us-central1"
}

data "google_service_account" "mev_boost_etl" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery_bids" {
  source = "../../modules/bigquery"
  project_id                          = var.project_id
  dataset_id                          = "mev_boost"

  config_view_id                      = "bids_bau_config"

  table_id                            = "bids"
  labels                              = {
    env = "test"
  }

  staging_table_id                    = "bids_staging"  

  ui_table_id                         = "bids_ui"
  block_number_partitioning_start     = 18237000
  block_number_partitioning_end       = 18519100
  block_number_partitioning_interval  = 100

  service_account_name               = data.google_service_account.mev_boost_etl.name
  service_account_email              = data.google_service_account.mev_boost_etl.email

  location                            = "us-central1"

  load_storedproc_name                = "load_bids"
}

module "storage" {
  source = "../../modules/storage"

  bucket_name                    = "mev-boost-bids"
  location                       = "US"
  processed_bucket_lifecycle_age = 30
  bucket_iam_members             = ["serviceAccount:${data.google_service_account.mev_boost_etl.email}"]
}

module "etl" {
  source = "../../modules/etl"

  project                      = var.project_id  
  location                     = "us-central1"
  service_account_email        = data.google_service_account.mev_boost_etl.email

  # bids transfer
  job_name                     = "mev-boost-bids-transfer"  
  container_image              = "gcr.io/enduring-art-207419/mev-boost-bids-transfer:latest"
  scheduler_job_name           = "mev-boost-bids-transfer-schedule"
  scheduler_schedule           = "5,35 * * * *"  

  # bids bau
  bau_job_name                 = "mev-boost-bids-bau"  
  bau_container_image          = "gcr.io/enduring-art-207419/mev-boost-bids-bau-etl:latest"
  bau_scheduler_job_name       = "mev-boost-bids-bau-schedule"
  bau_scheduler_schedule       = "15,45 * * * *"  
  bau_job_timeout              = "900s"
}

output "stage_table_id" {
  value = module.bigquery_bids.staging_table_id
}

output "ui_table_id" {
  value = module.bigquery_bids.ui_table_id
}

output "config_view_id" {
  value = module.bigquery_bids.config_view_id

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

output "bids_transfer_cloud_run_job_name" {  
  value = module.etl.cloud_run_job_name
}

output "bids_transfer_cloud_scheduler_job_name" {
  value = module.etl.cloud_scheduler_job_name
}

output "bau_cloud_run_job_name" {  
  value = module.etl.bau_cloud_run_job_name
}

output "bau_cloud_scheduler_job_name" {  
  value = module.etl.bau_cloud_scheduler_job_name
}
