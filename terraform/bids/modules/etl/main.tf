resource "google_cloud_run_v2_job" "default" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        image = var.container_image
        resources {
          limits = {
            cpu    = "4"
            memory = "8Gi"
          }
        }
      }
      service_account = var.service_account_email
      timeout         = var.job_timeout
      max_retries     = 0
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage, 
    ]
  }
}

resource "google_cloud_scheduler_job" "job" {
  name     = var.scheduler_job_name
  schedule = var.scheduler_schedule
  time_zone = var.time_zone

  http_target {
    uri        = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project}/jobs/${var.job_name}:run"
    http_method = "POST"

    oauth_token {
      service_account_email = var.service_account_email
    }    
  }

  depends_on = [google_cloud_run_v2_job.default]
}