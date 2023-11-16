output "staging_table_id" {
  description = "The ID of the staging table created."
  value       = google_bigquery_table.bids_staging.table_id
}

output "ui_table_id" {
  description = "The ID of the bids ui table created."
  value       = google_bigquery_table.bids_ui.table_id
}