provider "google" {  
  project = var.project_id
  region  = "us-central1"
}

data "google_service_account" "mev_boost_etl" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery" {
  source = "../../modules/bigquery"
  project_id                          = var.project_id
  public_project_id                   = "eden-data-public"
  dataset_id                          = "mev_boost"

  service_account_name               = data.google_service_account.mev_boost_etl.name
  service_account_email              = data.google_service_account.mev_boost_etl.email

  etl_config_view_id                  = "etl_config"
  config_view_id                      = "payloads_config"

  table_id                            = "payloads"
  labels                              = {
    env = "production"
  }

  staging_table_id                    = "payloads_staging"  

  location                            = "us-central1"

  load_storedproc_name                = "load_payloads"
}

module "etl" {
  source = "../../modules/etl"

  project                      = var.project_id  
  location                     = "us-central1"
  service_account_email        = data.google_service_account.mev_boost_etl.email
  
  job_name                     = "mev-boost-payloads"  
  container_image              = "gcr.io/${var.project_id}/mev-boost-payloads-etl:latest"
  scheduler_job_name           = "mev-boost-payloads"
  scheduler_schedule           = "*/15 * * * *"  
  job_timeout                  = "900s"  
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

output "load_storedproc_id" {
  value = module.bigquery.load_storedproc_name
}

output "cloud_run_job_name" {  
  value = module.etl.cloud_run_job_name
}

output "cloud_scheduler_job_name" {
  value = module.etl.cloud_scheduler_job_name
}