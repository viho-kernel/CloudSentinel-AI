output "gke_node_sa_email" {
  value = google_service_account.gke_node_sa.email
}

output "app_sa_email" {
  value = google_service_account.app_sa.email
}
