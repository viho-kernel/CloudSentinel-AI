# ==============================================================
# Hardened Google Cloud Storage (CIS GCP Benchmark 5.1 & 5.2)
# ==============================================================

resource "google_storage_bucket" "secure_bucket" {
  name          = "${var.project_prefix}-${var.environment}-${var.bucket_purpose}"
  location      = var.region
  force_destroy = false

  # CIS GCP Benchmark 5.2: Enforce Uniform Bucket-Level Access
  uniform_bucket_level_access = true

  # CIS GCP Benchmark 5.1: Enforce Public Access Prevention
  public_access_prevention = "enforced"

  # Protect against accidental deletion / ransomware
  versioning {
    enabled = true
  }

  # Cost Optimization Lifecycle Rule
  lifecycle_rule {
    condition {
      num_newer_versions = 3
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    security    = "hardened"
  }
}
