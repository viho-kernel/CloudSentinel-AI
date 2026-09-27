# ==============================================================
# GCP Modular VPC Network (Enterprise Custom Subnetting)
# ==============================================================

resource "google_compute_network" "custom_vpc" {
  name                    = "${var.project_prefix}-${var.environment}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"
  description             = "Custom VPC for CloudSentinel ${var.environment} environment"
}

resource "google_compute_subnetwork" "subnet" {
  name                     = "${var.project_prefix}-${var.environment}-subnet"
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.custom_vpc.id
  private_ip_google_access = true

  # Secondary CIDR ranges for GKE Pods and Services (IP Aliasing)
  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = var.services_cidr
  }
}

# Software-Defined Cloud Router
resource "google_compute_router" "router" {
  name    = "${var.project_prefix}-${var.environment}-router"
  region  = var.region
  network = google_compute_network.custom_vpc.id
}

# Cloud NAT (Allows private GKE nodes to access internet without public IPs)
resource "google_compute_router_nat" "nat" {
  name                               = "${var.project_prefix}-${var.environment}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Zero-Trust Default Ingress Firewall (Deny unapproved inbound)
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.project_prefix}-${var.environment}-allow-internal"
  network = google_compute_network.custom_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080", "9090"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.subnet_cidr]
  description   = "Allow internal microservice traffic within VPC"
}

# Allow Google Cloud Health Checks and Load Balancers
resource "google_compute_firewall" "allow_gcp_health_checks" {
  name    = "${var.project_prefix}-${var.environment}-allow-healthchecks"
  network = google_compute_network.custom_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  # Well-known Google Cloud Health Check Source IP Ranges
  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22"
  ]
  target_tags = ["cloudsentinel-node"]
}
