variable "project_prefix" {
  type    = string
  default = "cloudsentinel"
}

variable "environment" {
  type = string
}

variable "bucket_purpose" {
  type    = string
  default = "audit-logs"
}

variable "region" {
  type    = string
  default = "US"
}
