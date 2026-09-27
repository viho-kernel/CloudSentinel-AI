variable "project_id" {
  type    = string
  default = "cloudsentinel-staging"
}

variable "project_prefix" {
  type    = string
  default = "cloudsentinel"
}

variable "environment" {
  type    = string
  default = "staging"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "node_count" {
  type    = number
  default = 2
}

variable "machine_type" {
  type    = string
  default = "e2-standard-2"
}
