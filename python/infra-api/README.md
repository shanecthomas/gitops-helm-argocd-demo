# Internal Infrastructure API

> *"If it's in prod, it's fine. Probably."*

A containerized Flask REST API serving critical internal infrastructure intelligence,
including incident excuses, deployment affirmations, and on-call status reporting.

Built as the application layer for a GitHub Actions → Kubernetes CI/CD pipeline demo.

---

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | API index and available endpoints |
| `GET /health` | Liveness check (used by k8s probes) |
| `GET /version` | Deployment metadata — version, git SHA, environment |
| `GET /metrics` | Application metrics *(interpret loosely)* |
| `GET /excuse` | Industry-standard incident excuse generator |
| `GET /deploy` | Pre-deployment moral support |
| `GET /fortune` | Daily Linux wisdom |
| `GET /oncall` | On-call engineer situational awareness status |

---

## Quick Start

**Run locally with Python:**
```bash
pip3 install -r requirements.txt
APP_ENV=dev python3 app.py
curl http://localhost:5050/health
```

**Run with Docker:**
```bash
docker build -t infra-api .
docker run -p 5050:5050 -e APP_ENV=dev infra-api
curl http://localhost:5050/excuse
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `unknown` | Environment name (`dev` / `prod`) |
| `APP_VERSION` | `0.0.1-whoknows` | Injected at build time by CI pipeline |
| `GIT_SHA` | `c0ffee` | Git commit SHA, injected by GitHub Actions |
| `PORT` | `5050` | Listening port |

---

## CI/CD Pipeline

This app is deployed via a GitHub Actions pipeline:

1. **CI** — lint (`flake8`), build Docker image, push to registry
2. **CD (dev)** — deploy to `dev` namespace on Kind cluster, run health check
3. **CD (prod)** — deploy to `prod` namespace on manual approval

See `.github/workflows/` for pipeline definitions.

---

## Why This App?

Every service I deploy in production has a `/health` endpoint.
Most of them could use a `/excuse` endpoint too.
