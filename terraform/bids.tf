# resource "google_compute_instance" "default" {
#   name         = "mev-boost-etl-bids"
#   machine_type = "e2-standard-2"
#   zone         = "us-central1-a"

#   boot_disk {
#     initialize_params {
#       image = "debian-cloud/debian-9"
#       size  = 50
#     }
#   }

#   network_interface {
#     network = "default"
#     access_config {
#     }
#   }

#   service_account {
#     email  = data.google_service_account.mev_boost_sync_sa.email
#     scopes = ["cloud-platform"]
#   }

# }

resource "google_cloud_run_v2_job" "default" {
  name     = "mev-boost-bids-transfer"
  location = "us-central1"

  template {
    template {
      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello"
      }
      service_account = data.google_service_account.mev_boost_sync_sa.email
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
}

resource "google_cloud_scheduler_job" "job" {
  name     = "mev-boost-bids-transfer-schedule"
  schedule = "*/15 * * * *"
  time_zone = "UTC"

  http_target {
    uri = "https://${google_cloud_run_v2_job.default.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${google_cloud_run_v2_job.default.project}/jobs/${google_cloud_run_v2_job.default.name}:run"
    http_method = "POST"

    oauth_token {
      service_account_email = data.google_service_account.mev_boost_sync_sa.email
    }    
  }

  depends_on = [resource.google_cloud_run_v2_job.default]
}