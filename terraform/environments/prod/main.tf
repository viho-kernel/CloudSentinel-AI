terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "vpc" {
  source         = "../../modules/vpc"
  project_prefix = var.project_prefix
  environment    = var.environment
  region         = var.region
  subnet_cidr    = "10.12.0.0/20"
  pods_cidr      = "10.22.0.0/16"
  services_cidr  = "10.32.0.0/20"
}

module "iam" {
  source         = "../../modules/iam"
  project_id     = var.project_id
  project_prefix = var.project_prefix
  environment    = var.environment
}

module "gke" {
  source               = "../../modules/gke"
  project_id           = var.project_id
  project_prefix       = var.project_prefix
  environment          = var.environment
  region               = var.region
  network_id           = module.vpc.network_id
  subnet_id            = module.vpc.subnet_id
  pods_range_name      = module.vpc.pods_range_name
  services_range_name  = module.vpc.services_range_name
  node_count           = var.node_count
  machine_type         = var.machine_type
  node_service_account = module.iam.gke_node_sa_email
}

module "gcs" {
  source         = "../../modules/gcs"
  project_prefix = var.project_prefix
  environment    = var.environment
  bucket_purpose = "security-reports"
  region         = var.region
}
