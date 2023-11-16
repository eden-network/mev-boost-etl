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