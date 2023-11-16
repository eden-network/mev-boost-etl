output "bucket_name" {
  value = google_storage_bucket.bids_bucket.name
}

output "processed_bucket_name" {
  value = google_storage_bucket.processed_bucket.name
}

output "failed_bucket_name" {
  value = google_storage_bucket.failed_bucket.name
}
