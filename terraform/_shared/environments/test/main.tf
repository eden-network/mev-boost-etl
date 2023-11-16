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
}

module "bigquery_mev_boost" {
  source = "../../modules/bigquery"

  dataset_id           = "mev_boost"
  dataset_description  = "Dataset for housing mev-boost data"
  location             = "US"  
}

output "service_account_email" {
  value = module.service_account.service_account_email
}

output "dataset_id" {
  value = module.bigquery_mev_boost.dataset_id
}