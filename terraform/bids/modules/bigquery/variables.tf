variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "staging_table_id" {
  description = "The ID of the BigQuery table for staging data."
  type        = string
}

variable "ui_table_id" {
  description = "The ID of the BigQuery table for bids ui data."
  type        = string
}

variable "block_number_partitioning_start" {
  description = "The block number to start partitioning from."
  type        = number
}

variable "block_number_partitioning_end" {
  description = "The block number to end partitioning at."
  type        = number
}

variable "block_number_partitioning_interval" {
  description = "The interval to partition by."
  type        = number
}

variable "labels" {
  description = "A map of labels to assign to the tables created by this module."
  type        = map(string)
}