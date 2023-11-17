output "config_view_id" {
  description = "The ID of the created view."
  value       = google_bigquery_table.config.table_id
}