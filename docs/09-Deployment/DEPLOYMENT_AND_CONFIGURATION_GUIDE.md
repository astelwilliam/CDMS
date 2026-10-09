# Deployment and Configuration Guide

**Status**: Draft  
**Document Version**: 1.0  
**Last Updated**: 2026-07-23  
**Depends On**: POSTGRESQL_SCHEMA_SPECIFICATION.md, ALEMBIC_MIGRATION_STRATEGY.md, LOGGING_AND_MONITORING_STRATEGY.md (future)  
**Referenced By**: TESTING_STRATEGY.md

## 1. Purpose
This document defines the deployment architecture, environment strategy, and configuration management approach for Version 1 of the Campus Department Management System (CDMS). It ensures consistent and reliable deployment across all environments.

## 2. Deployment Architecture
The system is deployed as three primary components:
- Frontend: React (Vite) web application
- Backend: FastAPI application
- Database: PostgreSQL

These components are deployed independently but work together to deliver the full system.

## 3. Environment Strategy
Three environments are maintained:
- Development: Used by developers for feature development and testing.
- Staging: Mirrors production for final validation before release.
- Production: The live environment serving end users.

Each environment has its own database instance and configuration.

## 4. Configuration Management
Configuration is managed through environment variables. No secrets or environment-specific values are stored in source code. All configuration is externalized and injected at runtime.

## 5. Environment Variables
Key configuration areas include:
- Database connection settings
- Application secret keys
- Logging level and format
- File storage paths or credentials
- Allowed CORS origins
- Token expiration settings

All environment variables are documented and required for each environment.

## 6. Database Configuration
PostgreSQL is configured with appropriate connection pooling, statement timeout settings, and backup mechanisms. Migrations are applied automatically during deployment using Alembic.

## 7. File Storage Strategy
Version 1 uses application-managed local storage for uploaded files (gallery images, resources, profile images). Storage paths are configured via environment variables. Future migration to object storage is supported by the abstraction defined in the architecture.

## 8. Logging Configuration
Logging is configured to output structured logs. Log level is controlled by environment variable. Production environments use higher log levels with appropriate retention policies.

## 9. Backup Strategy
Database backups are performed regularly. Backup frequency and retention policy are defined per environment. Staging and production databases have automated backup processes.

## 10. Deployment Workflow
The deployment workflow follows these steps:
1. Code is merged to the release branch after passing all tests.
2. A new release is tagged.
3. The backend is deployed with the latest migrations.
4. The frontend is built and deployed.
5. Smoke tests are executed in the target environment.
6. The deployment is considered complete after successful verification.

## 11. Rollback Strategy
In case of deployment failure, the system can be rolled back to the previous stable release. Database migrations are forward-only; rollback of schema changes requires manual intervention or data restoration from backup when necessary.

## 12. Best Practices
- Never store secrets in source code or repository.
- Use environment-specific configuration files or variables.
- Automate deployment as much as possible.
- Verify deployments with automated smoke tests.
- Maintain clear separation between environments.
- Document all required environment variables.

## 13. Open Questions
- Should container orchestration (e.g., Docker Compose or Kubernetes) be used in Version 1?
- What is the preferred method for managing secrets in production?
- Is blue-green deployment required for Version 1?