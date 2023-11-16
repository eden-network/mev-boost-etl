output "service_account_email" {
  description = "The email address of the service account."
  value       = google_service_account.service_account.email
}

output "service_account_unique_id" {
  description = "The unique ID of the service account."
  value       = google_service_account.service_account.unique_id
}