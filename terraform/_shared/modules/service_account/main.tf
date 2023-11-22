resource "google_service_account" "service_account" {
  account_id   = var.account_id
  display_name = var.display_name
  description  = var.description
  project      = var.project_id
}

resource "google_project_iam_custom_role" "custom_role" {
  role_id     = var.role_id
  title       = var.role_title
  description = var.role_description
  permissions = var.role_permissions
}

resource "google_project_iam_member" "service_account_iam" {
  project = var.project_id
  role    = "projects/${var.project_id}/roles/${google_project_iam_custom_role.custom_role.role_id}"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}