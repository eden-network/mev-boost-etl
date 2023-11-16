variable "bucket_name" {
  description = "The name of the bucket"
  type        = string
}

variable "location" {
  description = "The location to create the buckets in"
  type        = string
}

variable "processed_bucket_lifecycle_age" {
  description = "Number of days to retain processed files before deletion"
  type        = number
}

variable "bucket_iam_role" {
  description = "The IAM role to assign"
  type        = string
  default     = "roles/storage.objectAdmin"
}

variable "bucket_iam_members" {
  description = "The IAM members to bind to the role"
  type        = list(string)
}
