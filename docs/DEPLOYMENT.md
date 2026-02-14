# Deployment Guide

## Production Deployment Checklist

### Security

- [ ] Change default admin credentials
- [ ] Implement proper password hashing (bcrypt/argon2)
- [ ] Add HTTPS/TLS encryption
- [ ] Implement rate limiting
- [ ] Add CORS restrictions
- [ ] Enable authentication tokens (JWT)
- [ ] Implement audit logging
- [ ] Add input sanitization
- [ ] Enable CSRF protection

### Database

- [ ] Replace in-memory storage with PostgreSQL/MySQL
- [ ] Implement database migrations
- [ ] Add connection pooling
- [ ] Enable database backups
- [ ] Implement data retention policies

### Infrastructure

- [ ] Containerize with Docker
- [ ] Set up Kubernetes orchestration
- [ ] Configure load balancer
- [ ] Set up Redis for caching
- [ ] Implement message queue (RabbitMQ/Kafka)
- [ ] Configure CDN for static assets

### Monitoring

- [ ] Add application monitoring (Prometheus/Grafana)
- [ ] Implement error tracking (Sentry)
- [ ] Set up log aggregation (ELK stack)
- [ ] Configure health checks
- [ ] Add performance monitoring (APM)
- [ ] Set up alerting (PagerDuty/Opsgenie)

### Compliance

- [ ] HIPAA compliance implementation
- [ ] Data encryption at rest and in transit
- [ ] Implement access controls (RBAC)
- [ ] Add audit trails
- [ ] Patient consent management
- [ ] Data anonymization for analytics
- [ ] Backup and disaster recovery plan

## Docker Deployment

### Dockerfile (API)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "scripts/run_api.py"]
```

### Dockerfile (Dashboard)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "scripts/run_dashboard.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./ml/models:/app/ml/models
      - ./data:/app/data

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "8501:8501"
    environment:
      - DASHBOARD_PORT=8501
      - API_URL=http://api:8000
    depends_on:
      - api

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=triage_db
      - POSTGRES_USER=triage_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Cloud Deployment

### AWS

1. **Elastic Beanstalk** for application hosting
2. **RDS** for PostgreSQL database
3. **ElastiCache** for Redis
4. **S3** for model storage
5. **CloudWatch** for monitoring
6. **ALB** for load balancing

### Azure

1. **App Service** for application hosting
2. **Azure Database for PostgreSQL**
3. **Azure Cache for Redis**
4. **Blob Storage** for models
5. **Application Insights** for monitoring
6. **Application Gateway** for load balancing

### GCP

1. **Cloud Run** for containerized apps
2. **Cloud SQL** for PostgreSQL
3. **Memorystore** for Redis
4. **Cloud Storage** for models
5. **Cloud Monitoring** for observability
6. **Cloud Load Balancing**

## Environment Variables

Create `.env` file:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Configuration
DASHBOARD_PORT=8501

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/triage_db

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Logging
LOG_LEVEL=INFO

# EHR Integration
EHR_INTEGRATION_ENABLED=true
DEFAULT_EHR_FORMAT=fhir
```

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple API instances behind load balancer
- Use Redis for session management
- Implement stateless architecture
- Use message queues for async tasks

### Vertical Scaling

- Increase CPU/RAM for ML inference
- Optimize model loading (lazy loading)
- Implement model caching
- Use GPU for faster inference (if needed)

## Backup Strategy

1. **Database**: Daily automated backups with 30-day retention
2. **Models**: Version control in S3/Blob Storage
3. **Logs**: Archive to cold storage after 90 days
4. **Configuration**: Store in version control

## Disaster Recovery

- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 1 hour
- Multi-region deployment for high availability
- Automated failover procedures
- Regular disaster recovery drills
