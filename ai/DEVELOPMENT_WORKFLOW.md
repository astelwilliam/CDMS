# Development Workflow

## Purpose
This document defines the official development process, workflows, and collaboration rules for the Campus Department Management System (CDMS). It ensures consistent, high-quality, and maintainable development across all modules.

## Table of Contents
- [1. Development Philosophy](#1-development-philosophy)
- [2. Project Lifecycle](#2-project-lifecycle)
- [3. Module Development Workflow](#3-module-development-workflow)
- [4. Requirement Analysis Process](#4-requirement-analysis-process)
- [5. Design Review Process](#5-design-review-process)
- [6. Database Design Phase](#6-database-design-phase)
- [7. Backend Development Phase](#7-backend-development-phase)
- [8. Frontend Development Phase](#8-frontend-development-phase)
- [9. Testing Phase](#9-testing-phase)
- [10. Documentation Update Process](#10-documentation-update-process)
- [11. Code Review Process](#11-code-review-process)
- [12. Approval Process](#12-approval-process)
- [13. Git Workflow](#13-git-workflow)
- [14. Branch Strategy](#14-branch-strategy)
- [15. Commit Message Convention](#15-commit-message-convention)
- [16. Pull Request Checklist](#16-pull-request-checklist)
- [17. Release Workflow](#17-release-workflow)
- [18. Bug Fix Workflow](#18-bug-fix-workflow)
- [19. Refactoring Rules](#19-refactoring-rules)
- [20. Change Management](#20-change-management)
- [21. Versioning Policy](#21-versioning-policy)
- [22. AI Collaboration Rules](#22-ai-collaboration-rules)
- [23. Human Review Responsibilities](#23-human-review-responsibilities)
- [24. Definition of Done](#24-definition-of-done)

## 1. Development Philosophy
Development follows a disciplined, documentation-first, and approval-gated approach. The focus is on long-term maintainability, consistency, and quality rather than speed. Every phase must be completed and reviewed before proceeding.

## 2. Project Lifecycle
The project is developed incrementally, module by module. Each module follows a strict 9-phase workflow. No phase may be skipped. The project owner retains final authority on all approvals and scope decisions.

## 3. Module Development Workflow
Every module must follow this sequence in order:
1. Requirement Analysis
2. Design Review
3. Database Design (if applicable)
4. Backend Development
5. Frontend Development
6. Testing
7. Documentation Update
8. Code Review
9. Approval

Progress to the next phase is only permitted after successful completion and approval of the current phase.

## 4. Requirement Analysis Process
- Requirements are derived exclusively from approved project documentation.
- The AI must identify any ambiguities or missing information.
- Clarification requests must be raised before proceeding.
- Requirements must be documented and approved before design begins.

## 5. Design Review Process
- A design document or specification must be created for the module.
- The design must align with the approved architecture and coding standards.
- The design must be reviewed and approved before implementation begins.
- **TODO**: Define the format and required contents of design documents.

## 6. Database Design Phase
- Database changes must follow PostgreSQL naming conventions defined in `ai/CODING_STANDARD.md`.
- Schema design must consider future scalability.
- All database changes require migration scripts.
- Database design must be reviewed and approved before backend development.

## 7. Backend Development Phase
- Backend code must follow Python/FastAPI best practices and the coding standards in `ai/CODING_STANDARD.md`.
- Business logic must be separated from presentation and data access layers.
- All public APIs must be documented.
- Code must be written in small, testable units.

## 8. Frontend Development Phase
- Frontend code must follow Flutter/Dart best practices and the coding standards in `ai/CODING_STANDARD.md`.
- UI components must be modular and reusable.
- State management and navigation must follow approved patterns.
- **TODO**: Define approved state management approach for Flutter.

## 9. Testing Phase
- Unit tests must be written for all non-trivial logic.
- Integration tests are required for API endpoints and critical flows.
- All tests must pass before code review.
- Test coverage and quality must meet project expectations.

## 10. Documentation Update Process
- All relevant project documentation must be updated after implementation.
- Module specifications, API documentation, and architecture documents must reflect the changes.
- Documentation is considered part of the deliverable and must be completed before approval.

## 11. Code Review Process
- All code must undergo peer review (or AI-assisted review followed by human review).
- Reviewers must verify adherence to coding standards, security practices, and architectural principles.
- All review comments must be addressed before merging.

## 12. Approval Process
- Each phase requires explicit approval from the project owner before the next phase can begin.
- Final module approval is granted only after all phases are complete and the Definition of Done is satisfied.
- Approvals must be recorded in the project documentation or decision log.

## 13. Git Workflow
The project uses a centralized Git workflow with feature branches. All changes are made through pull requests. Direct commits to the main branch are prohibited.

## 14. Branch Strategy
- `main`: Production-ready code only.
- `develop`: Integration branch for ongoing development.
- Feature branches: Created from `develop` using the naming pattern `feature/<module-name>-<short-description>`.
- Hotfix branches: Created from `main` when urgent fixes are required.

## 15. Commit Message Convention
Commit messages must follow this format:
```
<type>: <short summary>

[optional body]

[optional footer]
```
Types include: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. Messages must be clear and reference related issues or modules when applicable.

## 16. Pull Request Checklist
Before submitting a pull request:
- All tests pass
- Documentation is updated
- Coding standards are followed
- No sensitive data is included
- Branch is up to date with `develop`
- Clear description of changes is provided

## 17. Release Workflow
Releases are created from the `main` branch after all modules in a version are approved. Release notes must be generated and the version must be tagged in Git. **TODO**: Define release cadence and tagging format.

## 18. Bug Fix Workflow
Bugs are tracked separately. Critical bugs follow the hotfix branch workflow. Non-critical bugs are addressed in the next development cycle following the standard module workflow where applicable.

## 19. Refactoring Rules
Refactoring is permitted only when it improves maintainability without changing external behavior. All refactoring must be covered by existing tests. Significant refactoring requires prior approval.

## 20. Change Management
Any change that affects scope, architecture, or previously approved decisions must go through a formal change request process and receive explicit approval before implementation.

## 21. Versioning Policy
The project follows semantic versioning. Version numbers are updated according to the nature of changes (major, minor, patch). **TODO**: Confirm exact versioning rules and release numbering for Version 1.

## 22. AI Collaboration Rules
- The AI acts strictly as an implementation guide and must not make unilateral decisions.
- The AI must wait for approval at each gate.
- The AI must raise questions when requirements or decisions are unclear.
- All AI-generated content must be reviewed by a human.

## 23. Human Review Responsibilities
The project owner is responsible for:
- Approving requirements and designs
- Reviewing and approving code at each gate
- Making final scope and architectural decisions
- Granting final module approval

## 24. Definition of Done
A module is considered done only when:
- All nine workflow phases are completed
- All tests pass
- Documentation is updated
- Code review is approved
- Final approval is granted by the project owner
- No known critical issues remain

---

**Document Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-07-23  
**Depends On**: README.md, PROJECT_CORE.md, AI_CONTEXT.md, CODING_STANDARD.md  
**Referenced By**: All future module development prompts and AI_CONTEXT.md