# DOPPELGANGER-STUDIO Port Assignments (10000 Series)

**Purpose:** Port configuration for DOPPELGANGER-STUDIO project.

**Port Series:** 10000-10999 (exclusive range)

**Last Updated:** December 18, 2025

---

## 🎯 Port Allocation Summary

| Port Range | Category | Description |
|------------|----------|-------------|
| 10000-10099 | Application | Frontend, Dashboard |
| 10080-10099 | API | REST API, Services |
| 10400-10499 | Databases | PostgreSQL, MongoDB |
| 10500-10599 | Cache | Redis |
| 10900-10999 | Observability | Prometheus, Grafana |

---

## 📌 Application & API Tier (10000-10099)

| Port | Service | Description | Config |
|------|---------|-------------|--------|
| **10000** | Dashboard | React monitoring UI | `docker-compose.yml` |
| **10080** | Main API | FastAPI backend | `docker-compose.yml` |

---

## 📊 Infrastructure (10400-10599)

| Port | Service | Internal | Description | Config |
|------|---------|----------|-------------|--------|
| **10432** | PostgreSQL | 5432 | Primary database | `docker-compose.yml` |
| **10500** | Redis | 6379 | Cache and pub/sub | `docker-compose.yml` |
| **10517** | MongoDB | 27017 | Document storage | `docker-compose.yml` |

---

## 📈 Observability (10900-10999)

| Port | Service | Internal | Description | Config |
|------|---------|----------|-------------|--------|
| **10900** | Prometheus | 9090 | Metrics collection | `docker-compose.yml` |
| **10910** | Grafana | 3000 | Dashboards | `docker-compose.yml` |

---

## 🌐 Quick Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:10000 |
| API | http://localhost:10080 |
| Grafana | http://localhost:10910 |
| PostgreSQL | localhost:10432 |
| Redis | localhost:10500 |
| MongoDB | localhost:10517 |

---

## 🔗 Cross-Project Reference

For complete port allocations across all projects in the ecosystem, see the **MASTER_PORT_ASSIGNMENTS.md** in the NEURECTOMY project:
- **DOPPELGANGER-STUDIO:** 10000-10999
- **NEURECTOMY:** 16000-16999
- **SigmaLang:** 26000-26999
- **SigmaVault:** 36000-36999
- **Ryot LLM:** 46000-46999

---

## 🚀 Getting Started

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

**Version:** 1.0
**Status:** Active and maintained
