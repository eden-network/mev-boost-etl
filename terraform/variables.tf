variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "bucket_name" {
  description = "The name of the GCS bucket."
  type        = string
}

variable "service_account_id" {
    description = "The service account ID."
    type        = string
}

variable "location" {
    description = "The location of the resources associated with this solution."
    type        = string
}