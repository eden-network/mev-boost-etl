resource "google_bigquery_dataset" "mev_boost" {
  dataset_id   = var.dataset_id
  description  = var.dataset_description
  location     = var.location
}