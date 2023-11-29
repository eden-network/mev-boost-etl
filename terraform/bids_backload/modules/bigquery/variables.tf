variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "view_id" {
  description = "The ID of the BigQuery table."
  type        = string
}

variable "k8s_namespace" {
  description = "The Kubernetes namespace where the service account will be created."
  type        = string
  default     = "default"
}

variable "cluster_name" {
  description = "The name of the GKE cluster."
  type        = string
}

variable "cluster_location" {
  description = "The location for the GKE cluster."
  type        = string
}

variable "project_id" {
  description = "The project ID."
  type        = string
}

variable "service_account_email" {
  description = "The email of the Google service account linked to the Kubernetes service account."
  type        = string
}
