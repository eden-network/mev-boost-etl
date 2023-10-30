provider "google" {  
  project = var.project_id
  region  = var.location
}

data "google_client_config" "default" {}

data "google_service_account" "mev_boost_sync_sa" {
  account_id = var.service_account_id
}