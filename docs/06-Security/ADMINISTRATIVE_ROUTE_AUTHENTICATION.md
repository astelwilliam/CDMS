# Milestone 1D: Route authentication inventory

Scope: active application `backend/app/main.py`. Before/after policies are recorded below. Active JWT means a valid unexpired token whose subject resolves to an active database user. This is authentication only, not RBAC or department isolation.

All 82 business operations were previously unauthenticated. All now require an active JWT through registration-level dependencies. No PATCH operations exist.

The draft [API specification](../07-API/FASTAPI_API_SPECIFICATION.md) describes public content lists, but existing generic list/detail queries do not enforce publication or soft-delete filtering. Public access to these implementations is not justified. Separate public endpoints with explicit visibility rules are needed. Settings, audit logs, roles, permissions and administrator records are administrative data. College/department reads also remain authenticated; the current frontend receives 401 until a separate public API or authenticated UI is implemented.

| Method | Path | Router/module | Before | Policy after 1D | Public access justified? |
|---|---|---|---|---|---|
| GET | `/colleges/` | college | None | Active JWT | No; see visibility policy above |
| GET | `/colleges/{college_id}` | college | None | Active JWT | No; see visibility policy above |
| POST | `/colleges/` | college | None | Active JWT | No; see visibility policy above |
| PUT | `/colleges/{college_id}` | college | None | Active JWT | No; see visibility policy above |
| DELETE | `/colleges/{college_id}` | college | None | Active JWT | No; see visibility policy above |
| GET | `/departments/` | department | None | Active JWT | No; see visibility policy above |
| GET | `/departments/{department_id}` | department | None | Active JWT | No; see visibility policy above |
| POST | `/departments/` | department | None | Active JWT | No; see visibility policy above |
| PUT | `/departments/{department_id}` | department | None | Active JWT | No; see visibility policy above |
| DELETE | `/departments/{department_id}` | department | None | Active JWT | No; see visibility policy above |
| GET | `/faculty_members/` | faculty_member | None | Active JWT | No; see visibility policy above |
| GET | `/faculty_members/{faculty_member_id}` | faculty_member | None | Active JWT | No; see visibility policy above |
| POST | `/faculty_members/` | faculty_member | None | Active JWT | No; see visibility policy above |
| PUT | `/faculty_members/{faculty_member_id}` | faculty_member | None | Active JWT | No; see visibility policy above |
| DELETE | `/faculty_members/{faculty_member_id}` | faculty_member | None | Active JWT | No; see visibility policy above |
| GET | `/announcements/` | announcement | None | Active JWT | No; see visibility policy above |
| GET | `/announcements/{announcement_id}` | announcement | None | Active JWT | No; see visibility policy above |
| POST | `/announcements/` | announcement | None | Active JWT | No; see visibility policy above |
| PUT | `/announcements/{announcement_id}` | announcement | None | Active JWT | No; see visibility policy above |
| DELETE | `/announcements/{announcement_id}` | announcement | None | Active JWT | No; see visibility policy above |
| GET | `/events/` | event | None | Active JWT | No; see visibility policy above |
| GET | `/events/{event_id}` | event | None | Active JWT | No; see visibility policy above |
| POST | `/events/` | event | None | Active JWT | No; see visibility policy above |
| PUT | `/events/{event_id}` | event | None | Active JWT | No; see visibility policy above |
| DELETE | `/events/{event_id}` | event | None | Active JWT | No; see visibility policy above |
| GET | `/academic_resources/` | academic_resource | None | Active JWT | No; see visibility policy above |
| GET | `/academic_resources/{resource_id}` | academic_resource | None | Active JWT | No; see visibility policy above |
| POST | `/academic_resources/` | academic_resource | None | Active JWT | No; see visibility policy above |
| PUT | `/academic_resources/{resource_id}` | academic_resource | None | Active JWT | No; see visibility policy above |
| DELETE | `/academic_resources/{resource_id}` | academic_resource | None | Active JWT | No; see visibility policy above |
| GET | `/timetables/` | timetable | None | Active JWT | No; see visibility policy above |
| GET | `/timetables/{timetable_id}` | timetable | None | Active JWT | No; see visibility policy above |
| POST | `/timetables/` | timetable | None | Active JWT | No; see visibility policy above |
| PUT | `/timetables/{timetable_id}` | timetable | None | Active JWT | No; see visibility policy above |
| DELETE | `/timetables/{timetable_id}` | timetable | None | Active JWT | No; see visibility policy above |
| GET | `/gallery_albums/` | gallery_album | None | Active JWT | No; see visibility policy above |
| GET | `/gallery_albums/{album_id}` | gallery_album | None | Active JWT | No; see visibility policy above |
| POST | `/gallery_albums/` | gallery_album | None | Active JWT | No; see visibility policy above |
| PUT | `/gallery_albums/{album_id}` | gallery_album | None | Active JWT | No; see visibility policy above |
| DELETE | `/gallery_albums/{album_id}` | gallery_album | None | Active JWT | No; see visibility policy above |
| GET | `/gallery_images/` | gallery_image | None | Active JWT | No; see visibility policy above |
| GET | `/gallery_images/{image_id}` | gallery_image | None | Active JWT | No; see visibility policy above |
| POST | `/gallery_images/` | gallery_image | None | Active JWT | No; see visibility policy above |
| PUT | `/gallery_images/{image_id}` | gallery_image | None | Active JWT | No; see visibility policy above |
| DELETE | `/gallery_images/{image_id}` | gallery_image | None | Active JWT | No; see visibility policy above |
| GET | `/academic_calendars/` | academic_calendar | None | Active JWT | No; see visibility policy above |
| GET | `/academic_calendars/{calendar_id}` | academic_calendar | None | Active JWT | No; see visibility policy above |
| POST | `/academic_calendars/` | academic_calendar | None | Active JWT | No; see visibility policy above |
| PUT | `/academic_calendars/{calendar_id}` | academic_calendar | None | Active JWT | No; see visibility policy above |
| DELETE | `/academic_calendars/{calendar_id}` | academic_calendar | None | Active JWT | No; see visibility policy above |
| GET | `/help_center_articles/` | help_center_article | None | Active JWT | No; see visibility policy above |
| GET | `/help_center_articles/{article_id}` | help_center_article | None | Active JWT | No; see visibility policy above |
| POST | `/help_center_articles/` | help_center_article | None | Active JWT | No; see visibility policy above |
| PUT | `/help_center_articles/{article_id}` | help_center_article | None | Active JWT | No; see visibility policy above |
| DELETE | `/help_center_articles/{article_id}` | help_center_article | None | Active JWT | No; see visibility policy above |
| GET | `/settings/` | setting | None | Active JWT | No; see visibility policy above |
| GET | `/settings/{setting_id}` | setting | None | Active JWT | No; see visibility policy above |
| POST | `/settings/` | setting | None | Active JWT | No; see visibility policy above |
| PUT | `/settings/{setting_id}` | setting | None | Active JWT | No; see visibility policy above |
| DELETE | `/settings/{setting_id}` | setting | None | Active JWT | No; see visibility policy above |
| GET | `/audit_logs/` | audit_log | None | Active JWT | No; see visibility policy above |
| GET | `/audit_logs/{log_id}` | audit_log | None | Active JWT | No; see visibility policy above |
| GET | `/roles/` | role | None | Active JWT | No; see visibility policy above |
| GET | `/roles/{role_id}` | role | None | Active JWT | No; see visibility policy above |
| POST | `/roles/` | role | None | Active JWT | No; see visibility policy above |
| PUT | `/roles/{role_id}` | role | None | Active JWT | No; see visibility policy above |
| DELETE | `/roles/{role_id}` | role | None | Active JWT | No; see visibility policy above |
| GET | `/permissions/` | permission | None | Active JWT | No; see visibility policy above |
| GET | `/permissions/{permission_id}` | permission | None | Active JWT | No; see visibility policy above |
| POST | `/permissions/` | permission | None | Active JWT | No; see visibility policy above |
| PUT | `/permissions/{permission_id}` | permission | None | Active JWT | No; see visibility policy above |
| DELETE | `/permissions/{permission_id}` | permission | None | Active JWT | No; see visibility policy above |
| GET | `/department_administrators/` | department_administrator | None | Active JWT | No; see visibility policy above |
| GET | `/department_administrators/{admin_id}` | department_administrator | None | Active JWT | No; see visibility policy above |
| POST | `/department_administrators/` | department_administrator | None | Active JWT | No; see visibility policy above |
| PUT | `/department_administrators/{admin_id}` | department_administrator | None | Active JWT | No; see visibility policy above |
| DELETE | `/department_administrators/{admin_id}` | department_administrator | None | Active JWT | No; see visibility policy above |
| GET | `/super_administrators/` | super_administrator | None | Active JWT | No; see visibility policy above |
| GET | `/super_administrators/{admin_id}` | super_administrator | None | Active JWT | No; see visibility policy above |
| POST | `/super_administrators/` | super_administrator | None | Active JWT | No; see visibility policy above |
| PUT | `/super_administrators/{admin_id}` | super_administrator | None | Active JWT | No; see visibility policy above |
| DELETE | `/super_administrators/{admin_id}` | super_administrator | None | Active JWT | No; see visibility policy above |
| POST | `/auth/login` | auth | Public credential exchange | Public credential exchange | Yes; obtains a token after credential validation |
| GET | `/auth/me` | auth | Active JWT | Active JWT | No; current-user data |
| POST | `/auth/change-password` | auth | Active JWT | Active JWT | No; credential mutation |
| GET | `/health` | main | Public | Public | Yes; static status/service only, no database data |
| GET, HEAD | `/openapi.json` | FastAPI | Public | Public | Yes; API schema, retained per milestone requirement |
| GET, HEAD | `/docs` | FastAPI | Public | Public | Yes; Swagger UI, retained per milestone requirement |
| GET, HEAD | `/docs/oauth2-redirect` | FastAPI | Public | Public | Yes; Swagger authentication callback |
| GET, HEAD | `/redoc` | FastAPI | Public | Public | Yes; API documentation |

Documentation endpoints expose API structure, not permission to execute protected operations. CORS preflight handling is unchanged. Unregistered paths/methods retain normal 404/405 behavior.

Testing uses the registered application, real JWT verification, isolated SQLite sessions, and no authentication overrides. Denial cases cover every business operation; authenticated list requests cover every business router and a college create/read/update/delete cycle exercises representative writes. These tests do not establish role authorization or PostgreSQL-specific behavior.
