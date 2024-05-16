variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "dataset_id" {
  description = "The BigQuery dataset ID."
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

variable "ui_table_id" {
  description = "The ID of the BigQuery table for bids ui data."
  type        = string
}

variable "block_number_partitioning_start" {
  description = "The block number to start partitioning from."
  type        = number
}

variable "block_number_partitioning_end" {
  description = "The block number to end partitioning at."
  type        = number
}

variable "block_number_partitioning_interval" {
  description = "The interval to partition by."
  type        = number
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

variable "config_view_id" {
  description = "The ID of the bau config view"
  type        = string
}

variable "load_stored_procedure_id" {
  description = "The id of the stored procedure used to move data from staging to finalised"
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