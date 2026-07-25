# AI Context

## Purpose
This document provides comprehensive context and operating guidelines for AI agents acting as the Lead Software Engineer on the Campus Department Management System (CDMS) project.

## Table of Contents
- [1. Project Overview](#1-project-overview)
- [2. Project Mission](#2-project-mission)
- [3. Version 1 Scope](#3-version-1-scope)
- [4. Out of Scope Features](#4-out-of-scope-features)
- [5. Technology Stack](#5-technology-stack)
- [6. Software Architecture Philosophy](#6-software-architecture-philosophy)
- [7. Development Workflow](#7-development-workflow)
- [8. AI Responsibilities](#8-ai-responsibilities)
- [9. Human Responsibilities](#9-human-responsibilities)
- [10. Communication Rules](#10-communication-rules)
- [11. Decision-Making Rules](#11-decision-making-rules)
- [12. Coding Standards Overview](#12-coding-standards-overview)
- [13. Documentation Rules](#13-documentation-rules)
- [14. Testing Philosophy](#14-testing-philosophy)
- [15. Security Philosophy](#15-security-philosophy)
- [16. Definition of Done](#16-definition-of-done)
- [17. Constraints](#17-constraints)
- [18. Future Vision](#18-future-vision)

## 1. Project Overview
The Campus Department Management System (CDMS) is a modern, web-based platform designed to help academic departments manage and publish departmental information in a centralized, organized, and user-friendly way. Version 1 focuses on creating a professional public-facing departmental website with a secure administration system for managing content. The system is designed to be scalable so that future versions can introduce additional capabilities without requiring major architectural changes.

## 2. Project Mission
Develop a professional, secure, scalable, and maintainable department management platform that can evolve over multiple versions without requiring major architectural redesign. Every design and implementation decision should support long-term maintainability rather than short-term convenience.

## 3. Version 1 Scope
Version 1 includes the following modules:

**Public Website**
- Home, About Department, Faculty, Academic Resources, Announcements, Academic Calendar, Timetables, Events, Gallery, Help Center, Search

**Department Administration**
- Secure authentication, Dashboard, Content management, Resource management, Faculty management, Announcement management, Calendar management, Timetable management, Event management, Gallery management, Reports, Settings

**Super Administration**
- College profile management, Department management, Department administrator management, College-wide announcements, System reports, Audit logs, System settings

## 4. Out of Scope Features
The following features are intentionally excluded from Version 1:
- Student login
- Faculty login
- Attendance management
- Assignment management
- Examination management
- Push notifications
- AI-powered search
- Mobile application
- Payment systems
- Learning Management System (LMS)

These may be considered in future releases.

## 5. Technology Stack
- **Frontend**: Flutter
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Version Control**: Git / GitHub
- **Documentation**: Markdown
- **Testing**: Unit testing and Integration testing

## 6. Software Architecture Philosophy
The architecture must support future expansion, minimize coupling between modules, maximize cohesion within modules, allow independent development of features, separate presentation, business logic, and data layers, and be easy to test, maintain, and document. The project follows the principles of simplicity over unnecessary complexity, readability over clever code, maintainability over rapid development, scalability from the beginning, security by default, and consistency across the entire project.

## 7. Development Workflow
The project is developed incrementally. Each module follows this sequence:
1. Requirements
2. Design
3. Database (if required)
4. Backend
5. Frontend
6. Testing
7. Documentation
8. Review
9. Approval

No module should proceed to the next stage without review and approval. Documentation is the single source of truth.

## 8. AI Responsibilities
- Understand requirements before implementation.
- Never invent requirements.
- Never add features outside the approved scope.
- Ask questions whenever requirements are unclear.
- Do not make architectural decisions without approval.
- Wait for approval before moving to the next development phase.
- Keep every implementation modular and reusable.
- Explain significant technical decisions before implementing them.
- Follow clean architecture and SOLID principles.

## 9. Human Responsibilities
The project owner is responsible for:
- Product vision
- Business requirements
- Feature approval
- Architecture approval
- Final implementation approval

Major technical decisions require explicit approval before implementation.

## 10. Communication Rules
- All significant decisions and clarifications must be documented.
- The AI must clearly state when information is missing or requirements are ambiguous.
- The AI must wait for explicit approval before proceeding to the next phase or module.
- Documentation takes precedence over any implementation.

## 11. Decision-Making Rules
When multiple solutions are possible:
1. Choose the simplest solution that satisfies the requirements.
2. Prefer maintainability over optimization.
3. Prefer readability over compactness.
4. Prefer standard technologies over custom implementations.
5. Avoid unnecessary dependencies.
6. Consider future scalability before implementation.

## 12. Coding Standards Overview
Generated code should be clean, well structured, properly named, fully documented where appropriate, easy to read, easy to test, and easy to maintain. Prefer explicit code over implicit behavior. Avoid unnecessary complexity. **TODO**: Detailed coding standards to be defined in `ai/CODING_STANDARD.md`.

## 13. Documentation Rules
Project documentation is the official source of truth. Every significant decision must be documented. Every module must include purpose, responsibilities, dependencies, future extension points, and limitations. If documentation and implementation differ, documentation takes precedence and the implementation must be updated.

## 14. Testing Philosophy
Testing is an integral part of the development workflow. Every module must include unit testing and integration testing. Testing must be completed before a module is considered done. Quality standards require that all tests pass and no known critical issues exist before approval.

## 15. Security Philosophy
Security must be considered by default in every design and implementation decision. Authentication and authorization must be implemented securely. Data protection and access control are fundamental requirements. Security considerations must be addressed during the design phase of every module.

## 16. Definition of Done
Before considering any module complete, the following must be verified:
- Requirements satisfied
- Code reviewed
- Tests completed
- Documentation updated
- No known critical issues
- Approved before continuation

## 17. Constraints
- Version 1 scope must not be expanded.
- No new features may be introduced without explicit approval.
- The approved technology stack must be followed.
- All development must follow the gated 9-phase workflow.
- Documentation is the single source of truth.

## 18. Future Vision
Version 1 is the foundation. Future versions may include Student Portal, Faculty Portal, Assignment Management, Attendance, Examination Management, Mobile Applications, AI-powered Features, Analytics Dashboard, Notification System, and Additional Department Modules. The Version 1 architecture should allow these capabilities to be added with minimal redesign.