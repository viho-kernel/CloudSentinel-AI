variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "project_prefix" {
  type        = string
  default     = "cloudsentinel"
}

variable "environment" {
  type        = string
}

variable "region" {
  type        = string
  default     = "us-central1"
}

variable "network_id" {
  type        = string
}

variable "subnet_id" {
  type        = string
}

variable "pods_range_name" {
  type        = string
}

variable "services_range_name" {
  type        = string
}

variable "master_cidr" {
  type        = string
  description = "CIDR range for GKE master control plane"
  default     = "172.16.0.0/28"
}

variable "node_count" {
  type        = number
  default     = 2
}

variable "machine_type" {
  type        = string
  default     = "e2-standard-2"
}

variable "node_service_account" {
  type        = string
  description = "Email of custom service account attached to GKE nodes"
}
