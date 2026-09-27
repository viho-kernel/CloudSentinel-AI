variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "cloudsentinel-dev"
}

variable "project_prefix" {
  type    = string
  default = "cloudsentinel"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "node_count" {
  type    = number
  default = 1
}

variable "machine_type" {
  type    = string
  default = "e2-medium"
}
