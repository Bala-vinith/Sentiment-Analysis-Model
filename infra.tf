terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
     version = "5.11.0"
    }
  }
}

provider "google" {
  # Configuration options
  project = "gcp-trainer-project-1"
  region  = "asia-south1"
  zone    = "asia-south1-a"
  # credentials = "keys.json"
}

# VPC & subnet creation
resource "google_compute_network" "sentiment-analysis-model-vpc" {
  name                    = "sentiment-analysis-model-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "mumbai_subnet" {
  name          = "mumbai-subnet"
  region        = "asia-south1"
  network       = google_compute_network.sentiment-analysis-model-vpc.self_link
  ip_cidr_range = "10.1.0.0/24"
}

resource "google_compute_subnetwork" "delhi_subnet" {
  name          = "delhi-subnet"
  region        = "asia-south2"
  network       = google_compute_network.sentiment-analysis-model-vpc.self_link
  ip_cidr_range = "10.2.0.0/24"
}

# Artifact Registry
resource "google_artifact_registry_repository" "my-repo" {
  location      = "us-central1"
  repository_id = "sentiment_analysis_model"
  description   = "example docker repository"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }
}

# Cloud Run
resource "google_cloud_run_service" "my_cloud_run_service" {
  name     = "sentiment_analysis_model"
  location = "asia-south1"

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  network {
    egress_tag = google_compute_network.sentiment-analysis-model-vpc.name
  }
}
