output "cloud_run_job_name" {
  description = "The name of the Cloud Run job"
  value       = google_cloud_run_v2_job.default.name
}

output "cloud_scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.job.name
}