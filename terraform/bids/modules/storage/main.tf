resource "google_storage_bucket" "bids_bucket" {
  name     = var.bucket_name
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
      age = var.processed_bucket_lifecycle_age
    }
  }
}

resource "google_storage_bucket" "failed_bucket" {
  name     = "${var.bucket_name}-failed"
  location = var.location
}

resource "google_storage_bucket_iam_binding" "bucket_binding" {
  bucket  = google_storage_bucket.bids_bucket.name
  role    = var.bucket_iam_role
  members = var.bucket_iam_members
}

resource "google_storage_bucket_iam_binding" "processed_bucket_binding" {
  bucket  = google_storage_bucket.processed_bucket.name
  role    = var.bucket_iam_role
  members = var.bucket_iam_members
}

resource "google_storage_bucket_iam_binding" "failed_bucket_binding" {
  bucket  = google_storage_bucket.failed_bucket.name
  role    = var.bucket_iam_role
  members = var.bucket_iam_members
}   