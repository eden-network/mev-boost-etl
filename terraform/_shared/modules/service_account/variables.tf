variable "account_id" {
  description = "The service account ID. Must be unique within the project."
  type        = string
}

variable "display_name" {
  description = "The display name for the service account."
  type        = string
}

variable "description" {
  description = "A description of the service account."
  type        = string
}

variable "project_id" {
  description = "The ID of the project in which the service account will be created."
  type        = string
}

variable "role_id" {
  description = "Role ID for the custom role."
  type        = string
}

variable "role_title" {
  description = "Role title for the custom role."
  type        = string
}

variable "role_description" {
  description = "Role description for the custom role."
  type        = string
}

variable "role_permissions" {
  description = "List of permissions for the custom role."
  type        = list(string)
  default     = [
    "bigquery.jobs.create",
    "run.jobs.run",
    "run.routes.invoke"
  ]
}