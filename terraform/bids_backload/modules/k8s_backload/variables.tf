variable "service_account_name" {
  description = "The name of the service account used for the workload identity binding."
  type        = string
}

variable "network_name" {
  description = "The name for the VPC network."
  type        = string
}

variable "subnetwork_name" {
  description = "The name for the VPC subnetwork."
  type        = string
}

variable "region" {
  description = "The region for the subnetwork."
  type        = string
}

variable "ip_cidr_range" {
  description = "The IP CIDR range for the subnetwork."
  type        = string
}

variable "secondary_ip_ranges" {
  description = "A map of secondary IP ranges for the subnet for pods and services."
  type = list(object({
    range_name    = string
    ip_cidr_range = string
  }))
  default = [
    {
      range_name    = "mev-boost-subnet-pods"
      ip_cidr_range = "10.1.0.0/16"
    },
    {
      range_name    = "mev-boost-subnet-services"
      ip_cidr_range = "10.2.0.0/16"
    }
  ]
}

variable "project_id" {
  description = "The project ID."
  type        = string
}

variable "k8s_service_account" {
  description = "The Kubernetes service account name."
  type        = string
}

variable "service_account_email" {
  description = "The email of the Google service account linked to the Kubernetes service account."
  type        = string
}

variable "cluster_name" {
  description = "The name of the GKE cluster."
  type        = string
}

variable "cluster_location" {
  description = "The location for the GKE cluster."
  type        = string
}

variable "cluster_secondary_range_name" {
  description = "The secondary range name used for cluster pod IPs."
  type        = string
}

variable "services_secondary_range_name" {
  description = "The secondary range name used for cluster service IPs."
  type        = string
}

variable "node_pool_name" {
  description = "The name for the node pool."
  type        = string
}

variable "node_pool_location" {
  description = "The location for the node pool."
  type        = string
}

variable "node_pool_count" {
  description = "The number of nodes for the node pool."
  type        = number
}

variable "machine_type" {
  description = "The machine type for the GKE nodes."
  type        = string
}

variable "node_labels" {
  description = "The labels for nodes in the node pool."
  type        = map(string)
  default     = {}
}

variable "oauth_scopes" {
  description = "The list of OAuth scopes for the nodes in the node pool."
  type        = list(string)
}

variable "k8s_namespace" {
  description = "The Kubernetes namespace where the service account will be created."
  type        = string
  default     = "default"
}

variable "transfer_job_name" {
  description = "The name of the Cloud Run job"
  type        = string
}

variable "transfer_job_location" {
  description = "The location where the job and scheduler will be deployed"
  type        = string
}

variable "transfer_job_container_image" {
  description = "The container image for the Cloud Run job"
  type        = string
}

variable "transfer_job_timeout" {
  description = "The maximum duration of the Cloud Run job"
  default     = "900s"
  type        = string
}
