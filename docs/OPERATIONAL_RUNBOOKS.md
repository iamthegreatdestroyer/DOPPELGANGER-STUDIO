# Operational Runbooks - DOPPELGANGER STUDIO

## Table of Contents
1. [Deployment Procedures](#deployment-procedures)
2. [Rollback Procedures](#rollback-procedures)
3. [Incident Response](#incident-response)
4. [Troubleshooting](#troubleshooting)
5. [Monitoring & Alerts](#monitoring--alerts)

---

## Deployment Procedures

### Standard Deployment (Docker Compose)

**Prerequisites:**
- Docker & Docker Compose installed
- `.env` file configured with all secrets
- Database migrations ready

**Steps:**
```bash
# 1. Pull latest code
git pull origin main

# 2. Build containers
docker-compose build

# 3. Run database migrations
docker-compose run app python -m scripts.db.migrate

# 4. Start services
docker-compose up -d

# 5. Verify deployment
docker-compose ps
docker-compose logs -f app

# 6. Run health checks
curl http://localhost:8000/health
```

**Verification Checklist:**
- [ ] All containers running
- [ ] Database accessible
- [ ] Redis responding
- [ ] API endpoints returning 200
- [ ] No error logs
- [ ] Monitoring dashboard accessible

### Production Deployment (Kubernetes)

**Prerequisites:**
- kubectl configured
- Secrets and ConfigMaps created
- Container registry accessible

**Steps:**
```bash
# 1. Build and push Docker image
docker build -t doppelganger-studio/app:v0.2.0 .
docker push doppelganger-studio/app:v0.2.0

# 2. Update image tag in deployment
kubectl set image deployment/doppelganger-app app=doppelganger-studio/app:v0.2.0

# 3. Monitor rollout
kubectl rollout status deployment/doppelganger-app

# 4. Verify pods
kubectl get pods -l app=doppelganger

# 5. Check logs
kubectl logs -f deployment/doppelganger-app

# 6. Run health check
kubectl port-forward service/doppelganger-service 8080:80
curl http://localhost:8080/health
```

**Verification Checklist:**
- [ ] All pods in Running state
- [ ] No CrashLoopBackOff errors
- [ ] Load balancer healthy
- [ ] API responding correctly
- [ ] Monitoring metrics flowing

---

## Rollback Procedures

### Docker Compose Rollback

**When to Rollback:**
- Critical bugs in production
- Performance degradation
- Data corruption risk
- Security vulnerability introduced

**Steps:**
```bash
# 1. Stop current deployment
docker-compose down

# 2. Checkout previous stable version
git checkout <previous-stable-tag>

# 3. Rebuild containers
docker-compose build

# 4. Restore database if needed
docker-compose exec postgres psql -U doppelganger_user doppelganger < backup.sql

# 5. Start services
docker-compose up -d

# 6. Verify rollback
docker-compose logs -f app
curl http://localhost:8000/health
```

**Post-Rollback:**
- [ ] Verify all services operational
- [ ] Check database integrity
- [ ] Monitor error rates
- [ ] Document rollback reason
- [ ] Schedule post-mortem

### Kubernetes Rollback

**Steps:**
```bash
# 1. Check rollout history
kubectl rollout history deployment/doppelganger-app

# 2. Rollback to previous revision
kubectl rollout undo deployment/doppelganger-app

# Or rollback to specific revision
kubectl rollout undo deployment/doppelganger-app --to-revision=2

# 3. Monitor rollback
kubectl rollout status deployment/doppelganger-app

# 4. Verify pods
kubectl get pods -l app=doppelganger
kubectl logs -f deployment/doppelganger-app
```

---

## Incident Response

### Severity Levels

**P0 - Critical (15min response)**
- Complete service outage
- Data loss occurring
- Security breach

**P1 - High (1hr response)**
- Major feature unavailable
- Significant performance degradation
- API errors >10%

**P2 - Medium (4hr response)**
- Minor feature issue
- Intermittent errors
- Performance slowdown

**P3 - Low (24hr response)**
- Cosmetic issues
- Feature requests
- Documentation errors

### P0 Incident Response

**1. Alert Detection**
```bash
# Check monitoring dashboard
open https://dashboard.doppelganger-studio.com

# Check service status
kubectl get pods -l app=doppelganger
docker-compose ps
```

**2. Initial Triage**
```bash
# Check application logs
kubectl logs -f deployment/doppelganger-app --tail=100
docker-compose logs --tail=100 app

# Check resource usage
kubectl top pods
docker stats

# Check dependencies
kubectl get svc
docker-compose ps postgres redis mongo
```

**3. Communication**
- Update status page
- Notify stakeholders
- Create incident channel

**4. Mitigation**
- Scale up if resource issue
- Rollback if deployment issue
- Restart if transient issue
- Database restore if data issue

**5. Resolution**
- Fix root cause
- Deploy fix
- Verify resolution
- Update documentation

**6. Post-Incident**
- Write post-mortem
- Implement preventive measures
- Update runbooks

---

## Troubleshooting

### Common Issues

#### Issue: High Memory Usage

**Symptoms:**
- Memory usage >90%
- OOMKilled pods
- Slow response times

**Diagnosis:**
```bash
# Check memory usage
kubectl top pods
docker stats

# Check for memory leaks
python -m src.services.optimization.memory_manager
```

**Resolution:**
```bash
# Increase memory limits
kubectl edit deployment doppelganger-app
# Update resources.limits.memory

# Force garbage collection
kubectl exec -it <pod-name> -- python -c "import gc; gc.collect()"

# Restart pods
kubectl rollout restart deployment/doppelganger-app
```

#### Issue: Database Connection Failures

**Symptoms:**
- Connection timeout errors
- "Too many connections" errors
- Slow queries

**Diagnosis:**
```bash
# Check PostgreSQL status
kubectl exec -it postgres-pod -- psql -U doppelganger_user -c \"SELECT * FROM pg_stat_activity;\"

# Check connection pool
kubectl logs deployment/doppelganger-app | grep \"database\"
```

**Resolution:**
```bash
# Restart PostgreSQL
kubectl rollout restart deployment/postgres

# Increase connection limit
kubectl exec -it postgres-pod -- psql -U postgres -c \"ALTER SYSTEM SET max_connections = 200;\"

# Restart app to reset pools
kubectl rollout restart deployment/doppelganger-app
```

#### Issue: Redis Connection Failures

**Symptoms:**
- Cache misses increasing
- Redis timeout errors
- Slow API responses

**Diagnosis:**
```bash
# Check Redis status
kubectl exec -it redis-pod -- redis-cli ping

# Check memory usage
kubectl exec -it redis-pod -- redis-cli info memory
```

**Resolution:**
```bash
# Flush cache if needed
kubectl exec -it redis-pod -- redis-cli flushall

# Restart Redis
kubectl rollout restart deployment/redis
```

#### Issue: CI/CD Pipeline Failures

**Symptoms:**
- Tests failing
- Build errors
- Deployment blocked

**Diagnosis:**
```bash
# Check GitHub Actions logs
# Visit: https://github.com/sgbilod/DOPPELGANGER-STUDIO/actions

# Run tests locally
pytest tests/ -v
```

**Resolution:**
```bash
# Fix failing tests
pytest tests/unit/test_failing_module.py -v

# Rebuild Docker image
docker-compose build --no-cache

# Re-run CI
git commit --allow-empty -m \"trigger CI\"
git push
```

---

## Monitoring & Alerts

### Dashboard Access

**Production Dashboard:**
```
https://dashboard.doppelganger-studio.com
```

**Local Dashboard:**
```bash
# Start monitoring
python -m src.services.monitoring.dashboard

# Open browser
open http://localhost:3000
```

### Key Metrics to Monitor

**System Metrics:**
- CPU usage (alert if >80%)
- Memory usage (alert if >85%)
- Disk I/O (alert if >100MB/s sustained)
- Network I/O (alert if >500MB/s)

**Application Metrics:**
- API response time (alert if >500ms p95)
- Error rate (alert if >1%)
- Request rate (monitor trends)
- Active connections (alert if >1000)

**Database Metrics:**
- Query time (alert if >100ms avg)
- Connection pool usage (alert if >80%)
- Deadlocks (alert if any)
- Replication lag (alert if >5s)

### Alert Configuration

**Critical Alerts (Page Immediately):**
- Service down
- Error rate >10%
- Memory >95%
- Database connection failures

**Warning Alerts (Email):**
- Memory >85%
- CPU >80%
- Error rate >1%
- Response time >500ms

**Info Alerts (Dashboard Only):**
- Memory >75%
- CPU >60%
- Elevated request rate

### On-Call Procedures

**When Alert Fires:**
1. Acknowledge alert within 5 minutes
2. Access monitoring dashboard
3. Follow incident response procedures
4. Escalate if cannot resolve in 30 minutes
5. Update status page
6. Document resolution

**After Resolution:**
1. Mark incident resolved
2. Update runbooks if needed
3. Schedule post-mortem if P0/P1
4. Thank team members

---

## Emergency Contacts

**On-Call Engineer:** [Rotation schedule]  
**Team Lead:** [Contact info]  
**Database Admin:** [Contact info]  
**Security Team:** [Contact info]

---

**Document Version:** 1.0  
**Last Updated:** October 12, 2025  
**Next Review:** January 2026
