resource "google_bigquery_dataset" "mev_boost" {
  dataset_id   = var.dataset_id
  description  = var.dataset_description
  location     = var.location
}

resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id
  table_id   = var.config_table_id    

  labels = var.labels

  schema = file("${path.module}/etl_config.json")
}

resource "google_bigquery_dataset_iam_member" "dataset_writer" {
  dataset_id   = google_bigquery_dataset.mev_boost.dataset_id
  role         = "roles/bigquery.dataEditor"
  member       = "serviceAccount:${var.service_account_email}"
}

resource "google_bigquery_dataset" "mev_boost_public" {
  project      = var.public_project_id
  dataset_id   = var.dataset_id
  description  = var.dataset_description
  location     = var.location

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  access {
    role          = "roles/bigquery.dataViewer"
    special_group = "allAuthenticatedUsers"
  }
}