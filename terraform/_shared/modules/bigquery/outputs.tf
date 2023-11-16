output "dataset_id" {
  description = "The ID of the created dataset."
  value       = google_bigquery_dataset.mev_boost.dataset_id
}