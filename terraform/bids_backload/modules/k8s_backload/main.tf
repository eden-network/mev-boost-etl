resource "google_service_account_iam_binding" "workload_identity_binding" {
  service_account_id = var.service_account_name
  role               = "roles/iam.workloadIdentityUser"
  members            = ["serviceAccount:${var.project_id}.svc.id.goog[default/${var.k8s_service_account}]"]
}

resource "google_compute_network" "vpc_network" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vpc_subnetwork" {
  name          = var.subnetwork_name
  region        = var.region
  ip_cidr_range = var.ip_cidr_range
  network       = google_compute_network.vpc_network.self_link

  dynamic "secondary_ip_range" {
    for_each = var.secondary_ip_ranges
    content {
      range_name    = secondary_ip_range.value.range_name
      ip_cidr_range = secondary_ip_range.value.ip_cidr_range
    }
  }
}

resource "google_container_cluster" "primary" {
  name               = var.cluster_name
  location           = var.cluster_location
  initial_node_count = 1
  network            = google_compute_network.vpc_network.name
  subnetwork         = google_compute_subnetwork.vpc_subnetwork.name

  deletion_protection = false

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {   
    cluster_secondary_range_name  = var.cluster_secondary_range_name
    services_secondary_range_name = var.services_secondary_range_name
  }

  remove_default_node_pool = true
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = var.node_pool_name
  cluster    = google_container_cluster.primary.name
  location   = var.node_pool_location
  node_count = var.node_pool_count

  node_config {
    preemptible  = true
    machine_type = var.machine_type
    labels       = var.node_labels
    oauth_scopes = var.oauth_scopes
    disk_size_gb = 20
    disk_type    = "pd-standard"
  }
}

resource "kubernetes_service_account" "mev_boost_k8s_sa" {
  metadata {
    name      = var.k8s_service_account
    namespace = var.k8s_namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = var.service_account_email
    }
  }

  automount_service_account_token = true
}

resource "google_cloud_run_v2_job" "default" {
  name     = var.transfer_job_name
  location = var.transfer_job_location
  template {
    template {
      containers {
        image = var.transfer_job_container_image
      }
      service_account = var.service_account_email
      timeout         = var.transfer_job_timeout
    }
  }
  lifecycle {
    ignore_changes = [
      launch_stage, 
    ]
  }
}