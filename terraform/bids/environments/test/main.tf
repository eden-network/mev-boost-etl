provider "google" {
  project = var.project_id
  region  = "us-central1"
}

locals {
  project_id               = var.project_id
  public_project_id        = var.public_project_id
  location                 = "us-central1"
  dataset_id               = "mev_boost"
  config_view_id           = "bids_bau_config"
  staging_table_id         = "bids_staging"
  load_stored_procedure_id = "load_bids"
  bucket_name              = "mev-boost-bids"
  service_account_email    = data.google_service_account.mev_boost_etl.email
  service_account_name     = data.google_service_account.mev_boost_etl.name
  etl_image_digest         = ":latest"
}

data "google_service_account" "mev_boost_etl" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery_bids" {
  source                             = "../../modules/bigquery"
  project_id                         = local.project_id
  public_project_id                  = local.public_project_id
  dataset_id                         = local.dataset_id
  config_view_id                     = local.config_view_id
  table_id                           = "bids"
  labels                             = { env = "test" }
  staging_table_id                   = local.staging_table_id
  ui_table_id                        = "bids_ui"
  block_number_partitioning_start    = 15537940
  block_number_partitioning_end      = 19537939
  block_number_partitioning_interval = 1000
  service_account_name               = local.service_account_name
  service_account_email              = local.service_account_email
  location                           = local.location
  load_stored_procedure_id           = local.load_stored_procedure_id
}

module "storage" {
  source                         = "../../modules/storage"
  bucket_name                    = local.bucket_name
  location                       = "US"
  processed_bucket_lifecycle_age = 30
  bucket_iam_members             = ["serviceAccount:${local.service_account_email}"]
}

module "etl" {
  source                   = "../../modules/etl"
  logging_level            = "info"
  project_id               = local.project_id
  dataset_id               = local.dataset_id
  etl_config_table_id      = "etl_config"
  staging_table_id         = local.staging_table_id
  config_view_id           = local.config_view_id
  load_stored_procedure_id = local.load_stored_procedure_id
  batch_size_mb            = 100
  bucket_name              = local.bucket_name
  job_name                 = "mev-boost-bids"
  location                 = local.location
  container_image          = "gcr.io/${local.project_id}/mev-boost-bids-bau-etl${local.etl_image_digest}"
  service_account_email    = local.service_account_email
  job_timeout              = "3600s"
  scheduler_job_name       = "mev-boost-bids"
  scheduler_schedule       = "0 * * * *"
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

output "bids_cloud_run_job_name" {
  value = module.etl.cloud_run_job_name
}

output "bids_cloud_scheduler_job_name" {
  value = module.etl.cloud_scheduler_job_name
}