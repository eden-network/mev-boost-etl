output "cluster_endpoint" {
  value       = google_container_cluster.primary.endpoint
  description = "The endpoint of the GKE cluster."
}

output "cluster_ca_certificate" {
  value = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
}

output "node_pool_name" {
  value       = google_container_node_pool.primary_preemptible_nodes.name
  description = "Name of the node pool."
}

output "cluster_name" {
  value       = google_container_cluster.primary.name
  description = "The name of the GKE cluster."
}

output "cluster_location" {
  value       = google_container_cluster.primary.location
  description = "The location of the GKE cluster."
}