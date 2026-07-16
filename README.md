# GitOps + Helm + ArgoCD Demo

A complete, self-contained CI/CD pipeline demonstrating GitOps deployment practices —
from a Flask API through Docker, GitHub Actions, Kubernetes, Helm, Terraform, and ArgoCD.

Built as a portfolio project to demonstrate hands-on experience with the modern
Platform/DevOps engineering toolchain.

---

## What This Repo Demonstrates

| Skill | Where |
|---|---|
| Python application development (Dev/Prod) | `python/infra-api/app.py` |
| Docker (multi-stage, non-root, healthcheck) | `python/infra-api/Dockerfile` |
| CI: linting, unit tests, containerized system tests, container registry publishing (GHCR) | `.github/workflows/ci-infra-api.yml` |
| Kubernetes manifests via Helm (Dev/Prod) | `gitops/helm/infra-api/` |
| CD (Dev): Ephemeral Kubernetes testing (Kind) | `.github/workflows/cd-dev-infra-api.yml` |
| Infrastructure as Code (Terraform, Azure/AKS) | `terraform/` |
| GitOps continuous delivery (ArgoCD) | `gitops/argocd/argocd-infra-api.yaml` |
| CD (Prod): IaC ArgoCD Azure deployment (OIDC federation) | `.github/workflows/cd-prod-infra-api.yml` |

---

## Architecture

```
Push to main
     │
     ▼
┌─────────────┐   ┌──────────────┐   ┌───────────────┐
│    Lint     │──▶│  Unit + Sys  │──▶│  Build & Push │
│  (flake8)   │   │    Tests     │   │  (GHCR image) │
└─────────────┘   └──────────────┘   └───────┬───────┘
                                             │
                                             ▼
                                   ┌────────────────────┐
                                   │   Deploy to Dev    │
                                   │  (ephemeral Kind   │
                                   │   cluster)         │
                                   └────────────────────┘

Manual trigger (workflow_dispatch, image_tag input)
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│                     Deploy to Prod                         │
│                                                            │
│  1. Azure login (OIDC)                                     │
│  2. Terraform provisions a minimal AKS cluster             │
│  3. ArgoCD installed into the cluster                      │
│  4. ArgoCD Application syncs Helm chart (values-prod.yaml) │
│  5. Live endpoints verified (/health, /version, /excuse)   │
│  6. Terraform destroys the cluster — always, even on       │
│     failure (if: always()) [control costs]                 │
└────────────────────────────────────────────────────────────┘
```

**Dev** deploys to a throwaway Kubernetes cluster that exists only for the duration
of the CD job — no cloud account required.

**Prod** provisions a real Azure Kubernetes Service cluster, deploys to it the GitOps
way (via ArgoCD watching this repo), verifies endpoints, then tears the cluster down 
completely. The entire prod lifecycle — create, deploy, verify, destroy — 
happens inside a single workflow run, so there's no persistent cloud cost and 
no cluster left running unattended.

This pipeline is split across three separate workflow files - 
`ci-infra-api.yml`, `cd-dev-infra-api.yml`, and `cd-prod-infra-api.yml`. 
`cd-dev-infra-api.yml` triggers automatically off of `ci-infra-api.yml`, 
while `cd-prod-infra-api.yml` requires a workflow_dispatch and a valid image_tag.

---

## The Application

A small Flask API (`python/infra-api/app.py`) with environment-aware behavior —
`/excuse` and `/oncall` return different tones depending on `APP_ENV` (dev vs prod),
which is a deliberate way of proving the Helm `values.yaml` / `values-prod.yaml`
split is actually taking effect.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness/readiness probe target |
| `GET /version` | Deployment metadata — image tag, git SHA, environment |
| `GET /metrics` | Basic in-memory metrics (per-worker, not aggregated — see note below) |
| `GET /excuse` | Environment-aware incident excuse generator |
| `GET /oncall` | Environment-aware on-call status |

See `python/infra-api/README.md` for full endpoint documentation.

> **Note:** `/metrics`' `requests_served` counter is intentionally per-process, not
> shared across Gunicorn workers or Kubernetes replicas. This surfaced as a real bug
> during development — a good illustration of why in-memory state doesn't scale
> across multiple processes/pods without an external store (Redis, etc.).

---

## How to Demo This Repo

**Everything is visible without needing to run anything.** For a public GitHub repo,
Actions workflow run logs — including the formatted prod verification summary — are
visible to anyone. Check the **Actions** tab — you'll see three separate workflows listed: 
`CI - Infrastructure API`, `CD (Dev) - Infrastructure API`, and `CD (Prod) - Infrastructure API`.

**To trigger a fresh run yourself** (requires write access to this repo — see
"Access Control" below):

1. **CI - Infrastructure API** — runs automatically on every push to `main`, or by opening a pull request
2. **CD (Dev) - Infrastructure API** — triggers automatically once `CI - Infrastructure API` completes successfully on `main`
3. **CD (Prod) - Infrastructure API** — go to Actions → Click on the workflow → Run workflow, provide an
   `image_tag` from a successful dev deploy (visible in that run's logs), and run.
   This requires manual approval on the `prod` environment before the job executes.

A prod run takes roughly 15-20 minutes end to end and costs a few cents in Azure
compute — the cluster is destroyed automatically regardless of whether the run
succeeds or fails.

---

## Access Control

- `workflow_dispatch` (manual runs) requires **write access** to this repository
- The `prod` GitHub Environment has a **required reviewer** rule
- The Azure service principal used for prod deploys is scoped to **Contributor
  on a single resource group only** via OIDC federated credentials

---

## Repo Structure

```
.
├── python/infra-api/                    # Flask app, Dockerfile, unit + system tests
├── gitops/helm/infra-api/               # Helm chart (values.yaml = dev, values-prod.yaml = prod overrides)
├── terraform/                           # Minimal AKS cluster provisioning (ephemeral, per-run)
├── gitops/argocd/argocd-infra-api.yaml  # ArgoCD Application manifest (prod sync target)
├── AZURE_OIDC_SETUP.md        # One-time manual setup for passwordless Azure auth
└── .github/workflows/
    ├── ci-infra-api.yml                 # Lint, unit tests, system tests, build & push image
    ├── cd-dev-infra-api.yml             # Auto-triggers on ci-infra-api.yml success, deploys to ephemeral Kind cluster
    └── cd-prod-infra-api.yml            # Manual trigger, provisions AKS via Terraform + ArgoCD, then destroys
```

---

## One-Time Setup (if forking/reproducing this)

See `AZURE_OIDC_SETUP.md` for the manual, one-time Azure resource group and OIDC
federated credential setup required before the `cd-prod-infra-api.yml` workflow  can run. 
This only needs to be done once — everything after that is fully automated per run.
