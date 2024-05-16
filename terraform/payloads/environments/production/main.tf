provider "google" {
  project = var.project_id
  region  = "us-central1"
}

locals {
  project_id               = var.project_id
  public_project_id        = var.public_project_id
  location                 = "us-central1"
  dataset_id               = "mev_boost"
  config_view_id           = "payloads_config"
  staging_table_id         = "payloads_staging"
  load_stored_procedure_id = "load_payloads"
  bucket_name              = "mev-boost-payloads-prod"
  service_account_name     = data.google_service_account.mev_boost_etl.name
  service_account_email    = data.google_service_account.mev_boost_etl.email
  etl_image_tag            = ":latest"
}

data "google_service_account" "mev_boost_etl" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery" {
  source                   = "../../modules/bigquery"
  service_account_name     = local.service_account_name
  service_account_email    = local.service_account_email
  project_id               = local.project_id
  public_project_id        = local.public_project_id
  dataset_id               = local.dataset_id
  etl_config_view_id       = "etl_config"
  config_view_id           = local.config_view_id
  table_id                 = "payloads"
  staging_table_id         = local.staging_table_id
  load_stored_procedure_id = local.load_stored_procedure_id
  labels                   = { env = "production" }
  location                 = local.location
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
  config_view_id           = local.config_view_id
  staging_table_id         = local.staging_table_id
  load_stored_procedure_id = local.load_stored_procedure_id
  rate_limit_seconds       = "2"
  bucket_name              = local.bucket_name
  job_name                 = "mev-boost-payloads"
  location                 = local.location
  container_image          = "gcr.io/${var.project_id}/mev-boost-payloads-etl${local.etl_image_tag}"
  service_account_email    = local.service_account_email
  job_timeout              = "3600s"
  scheduler_job_name       = "mev-boost-payloads"
  scheduler_schedule       = "0 * * * *"
}

output "table_id" {
  value = module.bigquery.table_id
}

output "staging_table_id" {
  value = module.bigquery.staging_table_id
}

output "staging_archive_table_id" {
  value = module.bigquery.staging_archive_table_id
}

output "config_view_id" {
  value = module.bigquery.config_view_id
}

output "load_stored_procedure_id" {
  value = module.bigquery.load_stored_procedure_id
}

output "cloud_run_job_name" {
  value = module.etl.cloud_run_job_name
}

output "cloud_scheduler_job_name" {
  value = module.etl.cloud_scheduler_job_name
}