# Department authorization and identity linkage

Status: design proposal for Milestone 1F-B; no implementation or access relaxation.
Source baseline: `daf999b` (Milestone 1E), 541 previously verified tests.
Labels: **Confirmed** describes inspected source, **Proposed** describes future work,
and **Unresolved** identifies a decision or operational prerequisite, not a guarantee.

## 1. Current architecture and evidence

**Confirmed:** [User](../../backend/app/models/user.py) maps to `users`. Its primary
key is `String(36)`, with application-generated UUID values. Email is unique and
used for credential lookup; JWT `sub` identifies `User.id`. The
[authentication service](../../backend/app/services/auth_service.py) loads current
database state, rejects inactive users, and returns the database role. Existing
[dependencies](../../backend/app/api/deps/auth.py) compare exact `User.role` strings.
JWT role claims are not authoritative.

**Confirmed:** [DepartmentAdministrator](../../backend/app/models/department_administrator.py)
maps to `department_administrators` with independent `id`, unique `email`, and
`role_id -> roles.id`. It has no user foreign key. Super administrators likewise
have independent records without user linkage. Neither email equality nor a
`Role` record establishes authenticated identity. Role/Permission tables are not
integrated with authentication; preserve `User.role` semantics.

**Confirmed:** [Association tables](../../backend/app/models/association_tables.py)
include `department_administrator_departments`, with the composite primary key
`(department_administrator_id, department_id)`. Both columns reference their
respective primary keys with `ON DELETE CASCADE`. Multiple administrators per
department and multiple departments per administrator are structurally supported.
[Department](../../backend/app/models/department.py) has `college_id` and `deleted_at`.

**Confirmed:** The [initial migration](../../backend/alembic/versions/d084ff6d14cb_initial_cdms_schema.py)
has revision `d084ff6d14cb`, no parent revision, and these same identity/assignment
structures. Live schema, contents, and applied migration version are unverified.
[main.py](../../backend/app/main.py) currently protects all 17 business routers / 82
operations with `get_current_super_admin`. This remains unchanged in 1F-B through 1F-D.

**Confirmed:** The [administrator repository](../../backend/app/repositories/department_administrator_repository.py)
has an email lookup, but its `get_by_department()` ignores the department argument.
Do not use either for authenticated assignment resolution. The
[base repository](../../backend/app/repositories/base.py) uses unscoped get/list
operations, commits mutations internally, and physically deletes records.
Existing filtered helpers are not themselves authorization checks.

## 2. Proposed relationship and smallest migration

**Proposed:** Resolve identity only through:

`users.id -> department_administrators.user_id -> department_administrator_departments -> departments.id`

Add exactly one nullable column and two named constraints:

| Element | Proposed definition |
|---|---|
| Column | `department_administrators.user_id`, `String(36)`, nullable, no default |
| Foreign key | `fk_department_administrators_user_id_users`: `user_id -> users.id`, `ON DELETE RESTRICT` |
| Unique constraint | `uq_department_administrators_user_id`: unique non-null user linkage |

The type matches `users.id`; do not convert existing string IDs to native UUID.
PostgreSQL's ordinary UNIQUE semantics permit multiple NULLs while preventing two
administrator records from sharing a linked user. One column also prevents a
single administrator record from referencing multiple users. Its unique index
is sufficient for lookup; do not add a redundant index. Preserve the existing
assignment primary key and foreign keys. Do not make either assignment column
individually unique. No new assignment table or super-administrator link is needed.

**Proposed deletion behavior:** deleting a linked user is blocked until an explicit,
privileged unlink or administrator removal. Deleting an administrator may remove
its assignments through existing cascades but must never delete its User.
Deactivation is the preferred account-disable action. Soft deletion of a department
does not cascade assignments; resolution must exclude that department explicitly.
Do not introduce ORM delete/delete-orphan cascades toward User.

**Proposed migration plan:**

1. Add a new revision after the actual current head (presently `d084ff6d14cb`);
   never edit the initial migration. Check drift before a future deployment.
2. Add the nullable column, foreign key, and unique constraint. Existing rows remain
   NULL, preserving IDs, emails, roles, and assignments. Perform no data backfill.
3. Verify on disposable PostgreSQL: existing-row upgrade, multiple NULLs, duplicate
   linked-user rejection, nonexistent-user rejection, restricted user deletion,
   preserved assignment behavior, downgrade and re-upgrade.
4. Downgrade removes the new constraints and column only. It loses stored links;
   export verified mappings and disable scoped access before any operational rollback.
5. Provision links later using explicitly verified User-ID/administrator-ID mappings
   through a separately authorized trusted process. Never infer mappings from email.
   Unlinked records confer no access. A future NOT NULL constraint is optional and
   requires reconciliation, not part of this migration.

**Confirmed/proposed integration:** Both models are already imported by
`app/models/__init__.py`, loaded through `app/db/base.py` into Alembic metadata.
No new model import is required. A column/FK is enough for an explicit query;
bidirectional ORM convenience relationships are unnecessary for this minimum.
Existing [administrator schemas](../../backend/app/api/schemas/department_administrator.py)
need not change in 1F-C. Do not expose generic client updates of `user_id` or
assignments. A future privileged provisioning contract requires separate review.

## 3. Proposed identity and authorization rules

1. Authenticate with existing JWT validation and current database User state.
   Missing/invalid/expired credentials, missing User, or inactive User remain 401.
2. Exact `super_admin` retains existing business access without requiring an
   administrator profile or department assignments. Never represent this privilege
   as an empty department-ID collection.
3. Exact `department_admin` may enter a scoped path only when that operation has
   explicitly been enabled and tested. Unknown/case-mismatched/empty roles deny 403.
4. Query `DepartmentAdministrator.user_id == current_user.id`, then join its
   assignment rows and non-deleted departments. Missing linkage, ambiguous/corrupt
   linkage, or no eligible assignments denies 403. Database failures must not fall
   back to unscoped access. Foreign-key violations should be prevented by constraints;
   inconsistent ownership encountered at runtime denies access.
5. `User.role` is the authoritative role compatibility check, both at privileged
   link provisioning and on requests. Do not compare `Role.name` to invented values
   or require a guessed `role_id`. Administrator `role_id` remains existing metadata;
   it cannot grant access or override User.role. Role changes take effect on subsequent
   requests; no role/assignment claims are trusted from JWTs.
6. Resolve assignments per request, without cross-request caching. A future scoped
   dependency returns explicit user/admin identity and allowed department IDs, with
   a separate super-admin branch. IDs from request bodies, queries, or paths never
   enlarge the allowed set.

## 4. Proposed authorization matrix and rollout

All entries below are future policy gates; today all business operations remain
super-admin-only. Active users retain their own `/auth/me` and password change.
Login, health, and documentation retain their existing public policy.

| Operation | Super admin | Linked department admin | Missing link / unknown role |
|---|---|---|---|
| Assigned-department list/detail | Existing access | Scoped GET only starting 1F-E | 403 |
| Department create/update/delete | Existing access | Blocked, including profile edits initially | 403 |
| Faculty CRUD | Existing access | Own departments only after 1F-F | 403 |
| Other eligible content CRUD | Existing access | Blocked until individually enabled in 1F-G | 403 |
| Colleges, administrator records, identity/assignment management | Existing access | Blocked | 403 |
| Roles, permissions, audit logs | Existing access | Blocked | 403 |
| Announcements and settings | Existing access | Blocked pending ownership policy | 403 |
| Ownership transfers, restore, bulk actions, association mutation | Existing operations only | Blocked; no implicit grants | 403 |

## 5. Proposed resource ownership rules

| Resource | Confirmed ownership | Rule before department access can open |
|---|---|---|
| Departments | Own ID; required college FK | Assigned ID, not deleted; no implicit access to sibling departments |
| Faculty, events, academic resources, timetables, calendars, gallery albums, help articles | Required department FK | Scoped SQL predicate plus live department and resource |
| Gallery images | Required album FK | Join image -> live album -> live assigned department |
| Event/image association | Two foreign keys | Both sides authorized and same department; cross-department links blocked |
| Announcements | Nullable college and department FKs | Both/neither permitted today; remain blocked until ownership semantics resolved |
| Settings | Nullable college/department FKs; scope enum-like CHECK | CHECK does not enforce owner consistency; remain blocked pending scope/key policy |
| Audit logs | Actor ID/textual object reference | Not reliable department ownership; global only |
| Colleges, users, roles, permissions, administrator identities | No applicable department resource ownership | Global administration only |

**Proposed query/mutation rules:**

- List: apply authorized department, ownership-parent, soft-delete, and requested
  filters in SQL before ordering, pagination, and counts. Stable ordering includes
  the primary key. Reject negative offsets and bound limits (proposed maximum 100).
  Explicit unauthorized department/parent filters return 404; do not ignore them.
- Detail: look up by object ID AND authorized ownership. Return the same 404 for
  absent, deleted, or out-of-scope objects without revealing ownership details.
- Create: validate the requested department or parent in the authorized scope;
  persist only that verified owner. Missing/invalid input remains schema validation;
  a well-formed unauthorized owner returns 404. Do not silently choose a department.
- Update: first retrieve the existing record within scope; allow only approved
  content fields. Ownership/parent changes are prohibited even between two assigned
  departments. Reject attempts explicitly; do not silently accept owner fields.
- Delete: authorize the existing object and live parent within the write transaction.
  For the first faculty workflow, propose soft deletion for department-admin requests,
  with no restore/purge access. Preserve the existing super-admin path pending a
  separate deletion-policy decision; tests must make the difference explicit.
- Nested output and relationships must be scoped too. An authorized parent must not
  expose unauthorized associated records, file references, or global aggregates.

## 6. Revocation and concurrent requests

**Proposed semantics:** no guarantee that already-returned data can be revoked.
Reads authorized before a revocation commits may finish; subsequent reads must
resolve current assignments. Include assignment membership in resource queries,
not just a previously copied ID list, to minimize stale authorization windows.

**Proposed write protocol (required before 1F-F):** authorize and mutate within one
transaction. Lock the current User, linked administrator, relevant department,
assignment, ownership parents, and target rows in a documented consistent order;
recheck status/role/link/membership after obtaining locks. Serialize competing writes
and authorization-changing transactions through those same rows. For example,
removing an assignment must conflict with the scoped transaction's assignment lock;
relinking must conflict with the administrator lock. A write ordered before revocation
may commit first; a revocation ordered first must make the write fail authorization.
Never claim instantaneous cancellation of in-flight requests.

Do not call internally committing generic repository mutations in this path: they
can release authorization locks early. Introduce only the transaction-aware methods
needed for the first scoped workflow. Multi-row operations use sorted IDs within a
fixed table order. Define and test handling of deadlocks/serialization failures;
no retry may skip authorization. Direct out-of-band SQL is outside the application
protocol and must be operationally controlled.

**Unresolved implementation gate:** exact PostgreSQL lock modes/order and the
provisioning/revocation transaction entry points require review and two-session
integration tests before enabling scoped writes. SQLite tests alone cannot prove
this guarantee. Keep writes blocked if this gate cannot be met.

## 7. Independently testable implementation sequence

### 1F-C: Identity-link model and migration

Add only the proposed column/constraints and narrowly necessary model metadata.
Keep schemas, mappings, assignment rows, role semantics, and route guards unchanged.
Acceptance: disposable PostgreSQL migration/constraint tests described above pass;
existing records survive; no implicit mappings; existing suite remains green.
Do not run migration tests against development PostgreSQL.

### 1F-D: Identity and assignment resolution dependency

Add explicit lookup by user ID and a request-scoped resolution context. Do not reuse
the defective administrator get_by_department helper. Keep all business guards as-is.
Acceptance: active exact roles, unlinked users, multiple assignments, deleted
departments, removed links/assignments, inactive accounts, stale claims and role
changes are tested. A matching email with no FK linkage never grants access.
Multiple same-college assignments work; no eligible assignment denies access.

### 1F-E: Assigned-department reads only

Enable only GET `/departments/` and GET `/departments/{department_id}` for resolved
department administrators; preserve super-admin behavior. Because the current router
guard is super-admin-only, move that guard to the non-enabled operations when this
router is split; do not merely remove protection from the router.
Acceptance: two-department/two-user isolation, pagination/filter/count behavior,
404 non-disclosure, soft-deleted departments, and next-request revocation work.
All department writes and other business routes still reject department admins.

### 1F-F: One complete faculty workflow

Enable scoped list/detail/create/update/delete only for faculty, after concurrency
and deletion gates are accepted. Faculty has direct, required ownership and no
multi-parent ambiguity, making it the proposed first resource.
Acceptance: full positive CRUD in assigned departments; cross-department negative
tests for every method; owner-tampering rejection; failed writes unchanged; deleted
records/parents inaccessible; super-admin regression tests; PostgreSQL concurrency
tests prove the write/revocation ordering. Other content stays blocked.

### 1F-G: Extend one eligible resource at a time

Proposed order: academic resources, timetables, calendars, help articles, gallery
albums, then images and events after association handling is settled. Each resource
must pass the 1F-F isolation matrix, including indirect/nested ownership as applicable,
before its guard changes. Do not enable announcements/settings or association
mutation merely because another content resource passed. Keep unsupported routes
super-admin-only and maintain the route inventory with each change.

For every implementation milestone, run relevant tests, the complete regression
suite, and Git whitespace/diff checks; commit only that milestone after verification.
This design document does not authorize implementation or production data changes.

## 8. Remaining decisions and security risks

- **Unresolved provisioning:** who verifies mappings, how IDs are presented/reviewed,
  how relinking/revocation is audited, and which privileged interface performs it.
  No user IDs or mappings have been inferred. No general writable schema field is
  permitted as a shortcut. Production department access requires a reviewed process.
- **Unresolved cross-college policy:** existing many-to-many structure permits it.
  Proposed conservative gate: if one administrator's eligible assignments span
  multiple colleges, deny department access until explicitly approved; test this in
  1F-D. Do not infer college-wide access from any department assignment.
- **Unresolved role metadata:** administrator role_id may disagree with User.role.
  User.role remains authoritative; no permission-table or Role.name mapping is
  implied. Resolving duplicated role metadata is separate work.
- **Unresolved mixed ownership:** announcements permit both/neither owners and SET
  NULL on owner deletion; settings only validate scope vocabulary. Define consistent
  owner constraints and allowed department setting keys before opening either.
- **Unresolved deletion policy:** generic hard deletes and ORM cascades coexist with
  soft-delete columns. Department profile writes, parent deletion, restore, purge,
  and ownership transfer remain blocked pending explicit policies.
- **Unresolved file access:** database ownership checks alone do not protect any
  independently accessible file URLs. Review delivery/storage before claiming file
  confidentiality for images or academic resources.
- **Unverified deployment state:** migration head, existing assignments, duplicate
  identity records, and database drift need a separately authorized operational audit.
  A nullable FK deliberately permits unlinked legacy records; they grant no access.

## 9. Design-only verification

Checked against the source files linked above, the initial migration, current router
registration, and existing schemas/repositories. No application files, migration,
database data, dependency, or frontend changes belong to 1F-B. The 541-test baseline
is historical, not a claim that tests were rerun for this documentation-only change.
Review document links and diff, run Git whitespace/status checks, then stage only
this file for `docs(security): design department authorization and identity linkage`.
