variable "job_name" {
  description = "The name of the Cloud Run job"
  type        = string
}

variable "bau_job_name" {
  description = "The name of the Cloud Run job for the BAU application"
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

variable "bau_container_image" {
  description = "The container image for the Cloud Run job for the BAU application"
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

variable "bau_job_timeout" {
  description = "The maximum duration of the Cloud Run job for the BAU application"
  default     = "900s"
  type        = string
}

variable "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  type        = string
}

variable "bau_scheduler_job_name" {
  description = "The name of the Cloud Scheduler job for the BAU application"
  type        = string
}


variable "scheduler_schedule" {
  description = "The schedule on which the Cloud Scheduler job should run"
  type        = string
}

variable "bau_scheduler_schedule" {
  description = "The schedule on which the Cloud Scheduler job should run for the BAU application"
  type        = string
}

variable "time_zone" {
  description = "The time zone for the Cloud Scheduler job schedule"
  type        = string
  default     = "UTC"
}

variable "project" {
  description = "The project ID"
  type        = string
}