output "config_view_id" {
  description = "The ID of the created view."
  value       = google_bigquery_table.bids_staging.table_id
}