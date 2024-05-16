resource "google_bigquery_dataset" "mev_boost" {
  dataset_id  = var.dataset_id
  description = var.dataset_description
  location    = var.location
}

resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id
  table_id   = var.config_table_id
  labels     = var.labels
  schema     = file("${path.module}/etl_config.json")
}

resource "google_bigquery_dataset_iam_member" "dataset_writer" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"
}

resource "google_bigquery_dataset" "mev_boost_public" {
  project     = var.public_project_id
  dataset_id  = var.dataset_id
  description = var.dataset_description
  location    = var.location
}

resource "google_bigquery_dataset_iam_member" "public_dataset_writer" {
  project    = var.public_project_id
  dataset_id = google_bigquery_dataset.mev_boost_public.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"
}

resource "google_bigquery_dataset_iam_member" "public_data_viewer" {
  project    = var.public_project_id
  dataset_id = google_bigquery_dataset.mev_boost_public.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "allAuthenticatedUsers"
}

# Have to do this manually as we don't know the service account for this until it's created/ alternative is to use Terraform remote state.
# Unnessary as backloading won't be done in perpetuity.
resource "google_bigquery_dataset_iam_member" "logs_dataset_writer" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:service-797929678396@gcp-sa-logging.iam.gserviceaccount.com"
}