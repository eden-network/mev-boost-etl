resource "google_storage_bucket" "bids_bucket" {
  name = var.bucket_name
  location = var.location
}

resource "google_storage_bucket" "processed_bucket" {
  name     = "${var.bucket_name}-processed"
  location = var.location  

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 1
    }
  }
}

resource "google_storage_bucket" "failed_bucket" {
  name     = "${var.bucket_name}-failed"
  location = var.location  
}

resource "google_storage_bucket_iam_binding" "bucket_binding" {
  bucket = google_storage_bucket.bids_bucket.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${data.google_service_account.mev_boost_sync_sa.email}"
  ]
}

resource "google_storage_bucket_iam_binding" "processed_bucket_binding" {
  bucket = google_storage_bucket.processed_bucket.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${data.google_service_account.mev_boost_sync_sa.email}"
  ]
}

resource "google_storage_bucket_iam_binding" "failed_bucket_binding" {
  bucket = google_storage_bucket.failed_bucket.name
  role   = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${data.google_service_account.mev_boost_sync_sa.email}"
  ]
}