provider "google" {  
  project = var.project_id
  region  = "US"
}

module "service_account" {
  source      = "../../modules/service_account"
  account_id  = "mev-boost-etl-agent"
  display_name = "mev-boost-etl-agent"
  description = "Service account with cloud run permissions and read/write access to mev_boost dataset in enduring-art-207419, read/write access to mev_boost dataset in avalanche-304119"
  project_id  = var.project_id

  role_id = "mev_boost_etl_agent"
  role_title = "mev-boost-etl-agent"
  role_description = "Custom role for mevboost etl agent permissions"
  role_permissions = [
    "bigquery.jobs.create",
    "run.jobs.run",
    "run.routes.invoke"
  ]
}

module "bigquery_mev_boost" {
  source = "../../modules/bigquery"

  dataset_id           = "mev_boost"
  dataset_description  = "Dataset for housing mev-boost data"
  location             = "US"

  config_table_id      = "etl_config"
  labels               = {
    env = "test"
  }

  service_account_email = module.service_account.service_account_email
  
  public_project_id     = "avalanche-304119"
}

output "service_account_email" {
  value = module.service_account.service_account_email
}

output "service_account_unique_id" {  
  value = module.service_account.service_account_unique_id
}

output "custom_role_id" {
  value = module.service_account.custom_role_id  
}

output "dataset_id" {
  value = module.bigquery_mev_boost.dataset_id
}

output "table_id" {
  value = module.bigquery_mev_boost.table_id
}