output "network_id" {
  value = google_compute_network.custom_vpc.id
}

output "network_name" {
  value = google_compute_network.custom_vpc.name
}

output "subnet_id" {
  value = google_compute_subnetwork.subnet.id
}

output "subnet_name" {
  value = google_compute_subnetwork.subnet.name
}

output "pods_range_name" {
  value = "gke-pods"
}

output "services_range_name" {
  value = "gke-services"
}
