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

resource "google_compute_subnetwork" "mumbai-subnet" {
  name          = "mumbai"
  region        = "asia-south1"
  network       = google_compute_network.sentiment-analysis-model-vpc.id
  ip_cidr_range = "10.5.0.0/24"
}

resource "google_compute_subnetwork" "delhi-subnet" {
  name          = "delhi"
  region        = "asia-south2"
  network       = google_compute_network.sentiment-analysis-model-vpc.id
  ip_cidr_range = "10.4.0.0/24"
}

# Artifact Registry
resource "google_artifact_registry_repository" "my-repo" {
  location      = "us-central1"
  repository_id = "sentiment-analysis-model"
  description   = "example docker repository"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }
}

#cloudbuild triggeer


resource "google_cloudbuild_trigger" "github-trigger" {
  name     = "github-trigger"
  description = "Cloud Build trigger for GitHub repository"
  github {
    owner  = "Bala-vinith"
    name   = "gcp-ml-model"
    push {
      branch = "main"  # Change this to your desired branch
    }
  }

  build {
    timeout = "1200s"  # Change this to your desired build timeout

    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${var.project}/sentiment-analysis-model:latest", "."]
    }

    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project}/sentiment-analysis-model:latest"]
    }

    images = ["gcr.io/${var.project}/sentiment-analysis-model:latest"]
  }
}


# Cloud Run
resource "google_cloud_run_service" "my-cloud-run-service" {
  name     = "sentiment-analysis-model"
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

}
