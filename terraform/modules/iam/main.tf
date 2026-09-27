# ==============================================================
# Enterprise Least-Privilege IAM & Workload Identity Federation
# ==============================================================

# 1. GKE Node Agent Service Account
resource "google_service_account" "gke_node_sa" {
  account_id   = "${var.project_prefix}-${var.environment}-node-sa"
  display_name = "CloudSentinel GKE Node Pool Service Account"
  description  = "Restricted service account for GKE VM nodes (no default Compute Engine admin rights)"
}

# Attach minimal logging and monitoring roles to GKE Nodes
resource "google_project_iam_member" "node_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

resource "google_project_iam_member" "node_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

resource "google_project_iam_member" "node_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

resource "google_project_iam_member" "node_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}


# 2. Application Service Account (Used via Workload Identity)
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_prefix}-${var.environment}-app-sa"
  display_name = "CloudSentinel Core App Service Account"
  description  = "Dedicated identity for CloudSentinel FastAPI microservice running inside GKE"
}

# Grant access to Secret Manager
resource "google_project_iam_member" "app_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Workload Identity Binding: K8s Service Account -> GCP Service Account
resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = google_service_account.app_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[cloudsentinel/cloudsentinel-sa]"
}
