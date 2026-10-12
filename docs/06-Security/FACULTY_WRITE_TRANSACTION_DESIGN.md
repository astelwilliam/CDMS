# Faculty write transaction and locking protocol

Status: implementation design for Milestone 1F-F2. No authorization or database
behavior changes are authorized by this document.

Source baseline: `a24e030`, with 572 previously verified backend tests. This design
extends the identity and ownership rules in
[DEPARTMENT_AUTHORIZATION_DESIGN.md](DEPARTMENT_AUTHORIZATION_DESIGN.md).

## 1. Confirmed current behavior

`faculty_members.department_id` is a required foreign key to `departments.id` with
`ON DELETE RESTRICT`. Both models have `deleted_at`. Department-admin faculty reads
already join the live parent department and filter by resolved assignments.

Faculty writes remain super-admin-only. The generic base repository commits inside
`create`, `update`, and physical `delete`; these methods cannot participate in a
scoped authorization transaction. `get_db` closes its session but does not define a
commit policy. SQLAlchemy autobegins a transaction on the first database query.

There is no application path for adding or removing rows from
`department_administrator_departments`, or for setting/relinking
`DepartmentAdministrator.user_id`. Administrator schemas expose neither field.
Any future privileged assignment or relinking path must implement this protocol
before department-admin faculty writes are enabled.

## 2. Transaction boundary

Each create, update, or soft-delete request uses one SQLAlchemy session and exactly
one database transaction:

1. Decode and validate the JWT as today. Initial database authentication queries may
   autobegin the request transaction, but their results are preliminary only.
2. Inside the write service, acquire all required row locks in the order below and
   re-read every authorization fact from PostgreSQL.
3. Validate ownership and input after locks are held.
4. Flush the mutation, then commit once at the outer service/route boundary.
5. On authorization, validation, integrity, timeout, or database failure, roll back
   the whole transaction. Never commit from a repository helper.

The route must not call `BaseRepository.create`, `update`, or `delete`. Add narrowly
named methods that only select/lock, add an object, or change fields; they call
`flush()` when an identifier or constraint check is needed and never commit or roll
back. Response serialization occurs after a successful commit/refresh.

The preliminary 1F-D context is not write authorization. It may identify the likely
administrator and department, but the locked revalidation below is authoritative.

## 3. Global lock order

All application paths that change authorization or scoped faculty data acquire rows
by table in this order:

1. `users`
2. `department_administrators`
3. `departments`
4. `department_administrator_departments`
5. `faculty_members`

Use `SELECT ... FOR UPDATE` for each row. Within one table, lock primary keys in
ascending lexical order. Multi-user relinking locks both old and new user IDs in
that order; multi-department assignment changes lock all department IDs and then all
association keys in `(department_administrator_id, department_id)` order. Do not
lock through one multi-table outer-join query because PostgreSQL lock targets and
nullable join rows become difficult to reason about.

An assignment row must already exist for a department-admin faculty write. Locking
that row makes a concurrent delete wait. The administrator and department locks
also serialize relinking, new assignment insertion, department deletion, and cases
where an association row does not yet exist.

## 4. Locked authorization sequence

For every department-admin write:

1. Lock `users.id == JWT sub`. Require the row to exist, `is_active = true`, and
   `role == "department_admin"`. JWT role or department claims are ignored.
2. Lock the single `department_administrators` row whose `user_id` equals that user
   ID. Require exactly one. Missing or changed linkage returns the existing generic
   403. The database unique constraint prevents two committed matches; detected
   corruption fails closed.
3. Determine the requested owner: create uses the body `department_id`; update and
   delete use the faculty row's existing owner, obtained initially only as a lookup
   hint. Lock that `departments` row and require `deleted_at IS NULL`.
4. Lock the exact association row for the administrator and department. Require it
   to exist. Recheck that all administrator assignments still resolve to one college;
   cross-college state fails closed.
5. For update/delete, lock the faculty row and require its current `department_id`
   to equal the locked department and `deleted_at IS NULL`. Missing, deleted, or
   out-of-scope targets return the same 404.

Create inserts only after steps 1-4. The client-supplied department ID never expands
scope. A well-formed unauthorized or deleted department returns the same 404 used
for an absent owner. Update/delete must not reveal whether an unauthorized faculty
ID exists.

Super-admin behavior remains a separate explicit branch. It still authenticates
against current database state. Preserving its existing write semantics is allowed,
but it must not enter the department-admin branch or interpret an empty assignment
set as global access.

## 5. Revocation, relinking, and identity changes

The privileged assignment-removal transaction locks the affected user, then
administrator, department, and association row in the global order before deleting
the association and committing. Assignment insertion uses the same locks before
inserting. Relinking locks old/new users in sorted order, then the administrator,
revalidates its current `user_id`, updates it, and commits.

User deactivation or role changes lock the user row before mutation. Administrator
deletion locks its linked user, administrator, every assigned department in sorted
order, and all assignment rows before deletion. Department soft/hard deletion locks
the department through a compatible privileged workflow; when administrator IDs
are also involved, the workflow must begin with their users and administrators.

Ordering semantics are deliberate: if a faculty write locks the assignment first,
it may commit before a waiting revocation. If revocation commits first, the later
write finds no assignment and fails. Already-returned responses cannot be revoked.
Direct or legacy SQL that ignores this protocol can violate the guarantee and must
be restricted operationally.

## 6. Mutation policies

- **Create:** require a live assigned department; persist that verified ID.
- **Update:** allow only existing content fields. `department_id` is immutable,
  including moves between two assigned departments. Reject owner fields explicitly
  with 422 rather than silently ignoring them.
- **Department-admin delete:** set `deleted_at` using database time and return 204.
  An already deleted or inaccessible row returns the common 404. No restore or purge.
- **Super-admin delete:** retain the existing hard-delete contract for this milestone;
  its long-term deletion policy remains unresolved and must be tested separately.
- **Parents:** a deleted department denies all department-admin faculty writes.

No schema migration is required for these policies.

## 7. Deadlocks and transaction failures

Treat PostgreSQL SQLSTATE `40P01` (deadlock), `40001` (serialization failure), and
`55P03` (lock unavailable/lock timeout) as transient transaction failures. Always
roll back before responding. The first implementation should return a generic 503
with `Retry-After` and perform no automatic retry. This keeps request-body handling
and audit behavior simple. If retries are added later, retry the entire transaction,
including all locked authorization checks, with a small bounded count and jitter;
never resume after the failed statement or reuse cached authorization.

Configure finite transaction-local lock and statement timeouts in integration tests
and deployment policy. Do not translate these failures into 404/403 or expose table,
lock, user, administrator, or department identifiers.

## 8. Disposable PostgreSQL two-session tests

Use two independent connections and explicit barriers/events; SQLite is insufficient.
Each test asserts final rows as well as HTTP/service outcomes:

1. **Write first:** session A locks and updates/soft-deletes faculty; session B's
   assignment removal blocks. A commits, then B commits. The next write is denied.
2. **Revocation first:** B deletes and commits the assignment before A reaches its
   locked check. A returns 404/403 per the operation and changes no faculty data.
3. **Rollback:** A mutates then raises before commit while B waits. After A rolls
   back, B revokes successfully and no faculty mutation remains.
4. **Create races:** repeat both orderings for create and assert no row is created
   when revocation wins.
5. **Relink races:** relink the administrator while update/create waits; the old user
   cannot write after relinking commits, and the new user needs valid current role.
6. **Account races:** deactivation and role change winning the lock order cause the
   pending write to fail closed.
7. **Parent races:** department soft deletion winning first blocks the write; a write
   winning first commits before deletion proceeds.
8. **Target races:** concurrent update and soft-delete serialize on the faculty row;
   no lost update or resurrection occurs.
9. **Deadlock/timeout injection:** force `40P01`/`55P03`; assert full rollback, generic
   503, and no retry that skips authorization.
10. **Isolation matrix:** cross-department create/update/delete, owner-field tampering,
    deleted targets/parents, and missing assignments never change stored data.

Run these tests only against a disposable PostgreSQL database with a distinct URL
and destructive-test opt-in, following the existing PostgreSQL test safeguards.

## 9. Independently testable implementation steps

1. Add transaction-aware faculty repository primitives and unit tests proving they
   never commit, hard-delete, restore, or change ownership. Keep routes unchanged.
2. Add the locked department-admin write authorization service and PostgreSQL tests
   for role/link/department/assignment/target revalidation. Keep routes unchanged.
3. Add privileged assignment/relink/deactivation mutation services using the same
   lock order, or keep every such mutation unavailable. Pass the two-session tests.
4. Enable scoped faculty create only; test assigned and cross-department behavior,
   rollback, stale JWT claims, and both revocation orderings.
5. Enable scoped faculty update with explicit ownership-field rejection and the same
   concurrency matrix.
6. Enable scoped faculty soft-delete, leaving restore/purge and other resources
   blocked. Run focused PostgreSQL tests and the complete backend suite at each step.

## 10. Unresolved decisions and release gates

- Define the privileged provisioning/revocation interface, actor authorization, and
  audit record before any assignment mutation is exposed.
- Decide whether super-admin hard delete should later become soft delete; this design
  preserves current behavior only to avoid an unrelated contract change.
- Select production lock/statement timeout values and the public 503 error envelope.
- Decide whether immutable-owner rejection requires a global schema `extra="forbid"`
  policy or a faculty-specific request check; silent ignoring is unacceptable.
- Define durable security-audit events and whether they must commit atomically with
  each faculty or assignment mutation.

Scoped faculty writes remain blocked until steps 1-3 and the disposable PostgreSQL
concurrency suite pass. This document does not authorize application changes or
database operations.
