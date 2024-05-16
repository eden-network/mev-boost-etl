resource "google_cloud_run_v2_job" "default" {
  name     = var.job_name
  location = var.location
  template {
    template {
      containers {
        image = var.container_image
        env {
          name  = "LOOGING_LEVEL"
          value = var.logging_level
        }
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "DATASET_ID"
          value = var.dataset_id
        }
        env {
          name  = "CONFIG_VIEW_ID"
          value = var.config_view_id
        }
        env {
          name  = "TABLE_ID_STAGING"
          value = var.staging_table_id
        }
        env {
          name  = "LOAD_SP_ID"
          value = var.load_stored_procedure_id
        }
        env {
          name  = "RATE_LIMIT_SECONDS"
          value = var.rate_limit_seconds
        }
        env {
          name  = "BUCKET_NAME"
          value = var.bucket_name
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
  name      = var.scheduler_job_name
  schedule  = var.scheduler_schedule
  time_zone = var.time_zone
  http_target {
    uri         = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    http_method = "POST"
    oauth_token {
      service_account_email = var.service_account_email
    }
  }
  depends_on = [google_cloud_run_v2_job.default]
}