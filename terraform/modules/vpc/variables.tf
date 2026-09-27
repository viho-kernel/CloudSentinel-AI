variable "project_prefix" {
  type        = string
  description = "Prefix for all naming conventions (e.g. cloudsentinel)"
  default     = "cloudsentinel"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
}

variable "region" {
  type        = string
  description = "GCP Region (e.g. us-central1)"
  default     = "us-central1"
}

variable "subnet_cidr" {
  type        = string
  description = "Primary IP range for the subnet"
  default     = "10.10.0.0/20"
}

variable "pods_cidr" {
  type        = string
  description = "Secondary IP range for GKE Pods"
  default     = "10.20.0.0/16"
}

variable "services_cidr" {
  type        = string
  description = "Secondary IP range for GKE Services"
  default     = "10.30.0.0/20"
}
