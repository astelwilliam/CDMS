# Milestone 1E: Route authentication and authorization inventory

Scope: active application `backend/app/main.py`. Before/after policies are recorded below. Active JWT means a valid unexpired token whose subject resolves to an active database user. Business routes additionally require the exact database role `super_admin`; JWT role claims are not authoritative.

All 82 business operations across 17 routers required an active JWT after Milestone 1D. All now temporarily require an active super administrator through registration-level dependencies. No PATCH operations exist. Department-admin business operations are intentionally unavailable. Role and Permission tables are not integrated with authentication. Department-scoped authorization remains planned for Milestone 1F.

The draft [API specification](../07-API/FASTAPI_API_SPECIFICATION.md) describes public content lists, but existing generic list/detail queries do not enforce publication or soft-delete filtering. Public access to these implementations is not justified. Separate public endpoints with explicit visibility rules are needed. Settings, audit logs, roles, permissions and administrator records are administrative data. College/department reads also require super_admin; the current frontend receives 401 until a separate public API or appropriately authorized UI is implemented.

| Method | Path | Router/module | Before 1E | Policy after 1E | Public access justified? |
|---|---|---|---|---|---|
| GET | `/colleges/` | college | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/colleges/{college_id}` | college | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/colleges/` | college | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/colleges/{college_id}` | college | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/colleges/{college_id}` | college | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/departments/` | department | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/departments/{department_id}` | department | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/departments/` | department | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/departments/{department_id}` | department | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/departments/{department_id}` | department | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/faculty_members/` | faculty_member | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/faculty_members/{faculty_member_id}` | faculty_member | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/faculty_members/` | faculty_member | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/faculty_members/{faculty_member_id}` | faculty_member | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/faculty_members/{faculty_member_id}` | faculty_member | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/announcements/` | announcement | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/announcements/{announcement_id}` | announcement | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/announcements/` | announcement | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/announcements/{announcement_id}` | announcement | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/announcements/{announcement_id}` | announcement | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/events/` | event | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/events/{event_id}` | event | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/events/` | event | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/events/{event_id}` | event | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/events/{event_id}` | event | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/academic_resources/` | academic_resource | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/academic_resources/{resource_id}` | academic_resource | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/academic_resources/` | academic_resource | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/academic_resources/{resource_id}` | academic_resource | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/academic_resources/{resource_id}` | academic_resource | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/timetables/` | timetable | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/timetables/{timetable_id}` | timetable | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/timetables/` | timetable | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/timetables/{timetable_id}` | timetable | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/timetables/{timetable_id}` | timetable | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/gallery_albums/` | gallery_album | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/gallery_albums/{album_id}` | gallery_album | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/gallery_albums/` | gallery_album | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/gallery_albums/{album_id}` | gallery_album | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/gallery_albums/{album_id}` | gallery_album | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/gallery_images/` | gallery_image | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/gallery_images/{image_id}` | gallery_image | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/gallery_images/` | gallery_image | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/gallery_images/{image_id}` | gallery_image | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/gallery_images/{image_id}` | gallery_image | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/academic_calendars/` | academic_calendar | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/academic_calendars/{calendar_id}` | academic_calendar | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/academic_calendars/` | academic_calendar | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/academic_calendars/{calendar_id}` | academic_calendar | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/academic_calendars/{calendar_id}` | academic_calendar | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/help_center_articles/` | help_center_article | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/help_center_articles/{article_id}` | help_center_article | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/help_center_articles/` | help_center_article | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/help_center_articles/{article_id}` | help_center_article | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/help_center_articles/{article_id}` | help_center_article | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/settings/` | setting | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/settings/{setting_id}` | setting | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/settings/` | setting | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/settings/{setting_id}` | setting | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/settings/{setting_id}` | setting | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/audit_logs/` | audit_log | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/audit_logs/{log_id}` | audit_log | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/roles/` | role | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/roles/{role_id}` | role | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/roles/` | role | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/roles/{role_id}` | role | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/roles/{role_id}` | role | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/permissions/` | permission | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/permissions/{permission_id}` | permission | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/permissions/` | permission | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/permissions/{permission_id}` | permission | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/permissions/{permission_id}` | permission | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/department_administrators/` | department_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/department_administrators/{admin_id}` | department_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/department_administrators/` | department_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/department_administrators/{admin_id}` | department_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/department_administrators/{admin_id}` | department_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/super_administrators/` | super_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| GET | `/super_administrators/{admin_id}` | super_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/super_administrators/` | super_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| PUT | `/super_administrators/{admin_id}` | super_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| DELETE | `/super_administrators/{admin_id}` | super_administrator | Active JWT | Active JWT + super_admin | No; see visibility policy above |
| POST | `/auth/login` | auth | Public credential exchange | Public credential exchange | Yes; obtains a token after credential validation |
| GET | `/auth/me` | auth | Active JWT | Active JWT | No; current-user data |
| POST | `/auth/change-password` | auth | Active JWT | Active JWT | No; credential mutation |
| GET | `/health` | main | Public | Public | Yes; static status/service only, no database data |
| GET, HEAD | `/openapi.json` | FastAPI | Public | Public | Yes; API schema, retained per milestone requirement |
| GET, HEAD | `/docs` | FastAPI | Public | Public | Yes; Swagger UI, retained per milestone requirement |
| GET, HEAD | `/docs/oauth2-redirect` | FastAPI | Public | Public | Yes; Swagger authentication callback |
| GET, HEAD | `/redoc` | FastAPI | Public | Public | Yes; API documentation |

Documentation endpoints expose API structure, not permission to execute protected operations. CORS preflight handling is unchanged. Unregistered paths/methods retain normal 404/405 behavior.

Testing uses the registered application, real JWT verification, isolated SQLite sessions, and no authentication overrides. Denial cases cover every business operation; super-admin list requests cover every business router and a college create/read/update/delete cycle exercises representative writes. Department and unknown roles receive 403 across every business operation. Tests also cover database role changes overriding stale JWT claims and department-admin self-service. These tests establish the temporary role gate, not department isolation, granular permissions, or PostgreSQL-specific behavior.
