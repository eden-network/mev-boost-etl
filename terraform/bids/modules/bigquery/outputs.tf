output "table_id" {
  description = "The ID of the bids table created."
  value       = google_bigquery_table.bids.table_id
}

output "staging_table_id" {
  description = "The ID of the staging table created."
  value       = google_bigquery_table.bids_staging.table_id
}

output "ui_table_id" {
  description = "The ID of the bids ui table created."
  value       = google_bigquery_table.bids_ui.table_id
}

output "config_view_id" {
  description = "The ID of the bids bau view created."
  value       = google_bigquery_table.config.table_id
}

output "load_storedproc_name" {
  description = "The name of the stored procedure created to move data from staging to finalized."
  value = google_bigquery_routine.sproc.routine_id
}