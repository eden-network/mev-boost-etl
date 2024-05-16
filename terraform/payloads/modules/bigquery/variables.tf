variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "etl_config_view_id" {
  description = "The ID of the generic etl config view"
  type        = string
}

variable "config_view_id" {
  description = "The ID of the bau config view"
  type        = string
}

variable "table_id" {
  description = "The ID of the BigQuery table for finalised data."
  type        = string
}

variable "staging_table_id" {
  description = "The ID of the BigQuery table for staging data."
  type        = string
}

variable "load_stored_procedure_id" {
  description = "The ID of the stored procedure used to move data from staging to finalised"
  type        = string
}

variable "labels" {
  description = "A map of labels to assign to the tables created by this module."
  type        = map(string)
}

variable "service_account_name" {
  description = "The name of the service account to run the scheduled query"
  type        = string
}

variable "service_account_email" {
  description = "The email of the service account to run the scheduled query"
  type        = string
}

variable "location" {
  description = "The location of the scheduled query"
  type        = string
}

variable "public_project_id" {
  description = "The GCP project ID of the public project."
  type        = string
}