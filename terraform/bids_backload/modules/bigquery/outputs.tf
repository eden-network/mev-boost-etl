output "config_view_id" {
  description = "The ID of the created view."
  value       = google_bigquery_table.config.table_id
}

output "k8s_lock_table_id" {
  description = "The ID of the lock table created."
  value       = google_bigquery_table.k8s_lock.table_id
}

output "sink_writer_identity" {
  value = google_logging_project_sink.sink.writer_identity
}
