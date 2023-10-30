provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)  
}

resource "google_service_account_iam_binding" "workload_identity_binding" {
  service_account_id = data.google_service_account.mev_boost_sync_sa.name
  role               = "roles/iam.workloadIdentityUser"
  members            = ["serviceAccount:enduring-art-207419.svc.id.goog[default/mev-boost-k8s-sa]"]
}

resource "google_compute_network" "vpc_network" {
  name                    = "mev-boost-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vpc_subnetwork" {
  name          = "mev-boost-subnet"
  region        = "us-central1"
  ip_cidr_range = "10.0.0.0/16"
  network       = google_compute_network.vpc_network.self_link

  secondary_ip_range {
    range_name    = "mev-boost-subnet-pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "mev-boost-subnet-services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

resource "google_container_cluster" "primary" {
  name               = "mev-boost-gke-cluster"
  location           = "us-central1-a"
  initial_node_count = 1
  network            = "mev-boost-vpc"
  subnetwork         = "mev-boost-subnet"

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {   
    cluster_secondary_range_name  = "mev-boost-subnet-pods"
    services_secondary_range_name = "mev-boost-subnet-services" 
  }

  remove_default_node_pool = true
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "mev-boost-node-pool"
  cluster    = google_container_cluster.primary.name
  location   = "us-central1-a"
  node_count = 8

  node_config {
    preemptible  = true
    machine_type = "e2-medium"
    
    labels = {
      pool = "mev-boost-node-pool"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append",
      "https://www.googleapis.com/auth/bigquery",
      "https://www.googleapis.com/auth/cloud-platform"      
    ]
  }
}

resource "kubernetes_service_account" "mev-boost-k8s-sa" {
  metadata {
    name      = "mev-boost-k8s-sa"
    namespace = "default"
    annotations = {
      "iam.gke.io/gcp-service-account" = data.google_service_account.mev_boost_sync_sa.email
    }
  }

  automount_service_account_token = true
}

output "gke_endpoint" {
  value = google_container_cluster.primary.endpoint
  description = "The endpoint of the GKE cluster."
}