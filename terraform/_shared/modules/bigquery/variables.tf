variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "dataset_description" {
  description = "The description of the BigQuery dataset."
  type        = string
}

variable "location" {
  description = "The location for the BigQuery dataset."
  type        = string
}

variable "config_table_id" {
  description = "The ID of the mev_boost etl config table"
  type        = string
}

variable "labels" {
  description = "A map of labels to assign to the tables created by this module."
  type        = map(string)
}

variable "service_account_email" {
  description = "The email address of the service account to use for authentication."
  type        = string
}

variable "public_project_id" {
  description = "The GCP project ID of the public project."
  type        = string
}