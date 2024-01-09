provider "google" {  
  project = var.project_id
  region  = "us-central1"
}

data "google_client_config" "default" {}

data "google_service_account" "etl_service_account" {
  account_id = "mev-boost-etl-agent@${var.project_id}.iam.gserviceaccount.com"
}

module "bigquery" {
  source                = "../../modules/bigquery"    
  dataset_id            = "mev_boost"  
  view_id               = "bids_k8s_config"
  lock_table_id         = "bids_k8s_lock"
  project_id            = var.project_id
  cluster_location      = module.k8s_backload.cluster_location
  cluster_name          = module.k8s_backload.cluster_name
  service_account_email = data.google_service_account.etl_service_account.email
  labels                = {
    env = "test"
  }
}

provider "kubernetes" {
  host                   = "https://${module.k8s_backload.cluster_endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.k8s_backload.cluster_ca_certificate)
}

module "k8s_backload" {
  source                = "../../modules/k8s_backload"
  project_id            = var.project_id
  service_account_name  = data.google_service_account.etl_service_account.name
  network_name          = "mev-boost-vpc"
  subnetwork_name       = "mev-boost-subnet"
  region                = "us-central1"
  ip_cidr_range         = "10.0.0.0/16"
  secondary_ip_ranges        = [
    {
      range_name    = "mev-boost-subnet-pods"
      ip_cidr_range = "10.1.0.0/16"
    },
    {
      range_name    = "mev-boost-subnet-services"
      ip_cidr_range = "10.2.0.0/16"
    }
  ]
  k8s_service_account             = "mev-boost-k8s-sa"
  service_account_email           = data.google_service_account.etl_service_account.email
  cluster_name                    = "mev-boost-gke-cluster"
  cluster_location                = "us-central1-a"
  cluster_secondary_range_name    = "mev-boost-subnet-pods"
  services_secondary_range_name   = "mev-boost-subnet-services"
  node_pool_name                  = "mev-boost-node-pool"
  node_pool_location              = "us-central1-a"
  node_pool_count                 = 20  
  machine_type                    = "e2-medium"
  node_labels                     = { pool = "mev-boost-node-pool" }
  oauth_scopes                    = [
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
    "https://www.googleapis.com/auth/service.management.readonly",
    "https://www.googleapis.com/auth/servicecontrol",
    "https://www.googleapis.com/auth/trace.append",
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform"
  ]
  k8s_namespace                   = "default"
  transfer_job_name               = "mev-boost-bids-transfer-job"
  transfer_job_location           = "us-central1"
  transfer_job_timeout            = "7200s"
  transfer_job_container_image    = "gcr.io/${var.project_id}/mev-boost-bids-transfer:latest"
}

output "cluster_endpoint" {
  value = module.k8s_backload.cluster_endpoint
}

output "node_pool_name" {
  value = module.k8s_backload.node_pool_name
}

output "config_view_id" {
  value = module.bigquery.config_view_id
}

output "sink_writer_identity" {
  value = module.bigquery.sink_writer_identity
}

