# ==============================================================
# Production Private GKE Cluster with Workload Identity
# ==============================================================

resource "google_container_cluster" "primary" {
  name     = "${var.project_prefix}-${var.environment}-gke"
  location = var.region

  # Best practice: Do not use default node pool; delete it and create dedicated pool
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = var.network_id
  subnetwork = var.subnet_id

  # VPC-Native IP Allocation (Alias IPs)
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  # Security: Private Cluster Configuration (Nodes have NO public IPs)
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_cidr
  }

  # Security: Workload Identity Federation (Eliminates static service account keys)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Security: In-cluster Zero-Trust Network Policy Engine
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # Security: Enforce Kubernetes RBAC (Disable legacy ABAC)
  enable_legacy_abac = false

  # Master Authorized Networks (Restrict cluster API access)
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0" # In staging/prod, restrict to corporate bastion/VPN
      display_name = "Bastion-Or-CI-Runner"
    }
  }

  # Maintenance & Upgrades
  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
  }
}

# Dedicated Managed GKE Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.project_prefix}-${var.environment}-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.node_count

  node_config {
    machine_type    = var.machine_type
    service_account = var.node_service_account
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    tags = ["cloudsentinel-node"]

    # Security: Shielded VM nodes
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
