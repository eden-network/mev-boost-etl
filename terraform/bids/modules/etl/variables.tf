variable "job_name" {
  description = "The name of the Cloud Run job"
  type        = string
}

variable "location" {
  description = "The location where the job and scheduler will be deployed"
  type        = string
}

variable "container_image" {
  description = "The container image for the Cloud Run job"
  type        = string
}

variable "service_account_email" {
  description = "The service account email to use with the Cloud Run job"
  type        = string
}

variable "job_timeout" {
  description = "The maximum duration of the Cloud Run job"
  default     = "900s"
  type        = string
}

variable "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  type        = string
}

variable "scheduler_schedule" {
  description = "The schedule on which the Cloud Scheduler job should run"
  type        = string
}

variable "time_zone" {
  description = "The time zone for the Cloud Scheduler job schedule"
  type        = string
  default     = "UTC"
}

variable "logging_level" {
  description = "The logging level to use for the deployment"
  type        = string
}

variable "project_id" {
  description = "The project ID"
  type        = string
}

variable "dataset_id" {
  description = "The dataset ID where the tables and stored procedure are stored"
  type        = string
}

variable "etl_config_table_id" {
  description = "The configuration table for relays"
  type        = string
}

variable "staging_table_id" {
  description = "The staging table for the load"
  type        = string
}

variable "config_view_id" {
  description = "The configuration view for business as usual load"
  type        = string
}

variable "bucket_name" {
  description = "The name of the bucket where new bids files are initially staged"
  type        = string
}

variable "batch_size_mb" {
  description = "The max size of in memory files before they're pushed to cloud storage"
  type        = string
}

variable "load_stored_procedure_id" {
  description = "The name of the stored procedure used to move data from the staging table to the final bids table"
  type        = string
}