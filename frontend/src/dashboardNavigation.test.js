import assert from "node:assert/strict";
import test from "node:test";
import {
  dashboardHashForView,
  dashboardViewFromHash,
  dashboardViewsForRole,
} from "./dashboardNavigation.js";

test("dashboard section survives refresh through its URL hash", () => {
  for (const view of ["overview", "departments", "faculty"]) {
    assert.equal(dashboardViewFromHash(dashboardHashForView(view)), view);
  }
  assert.equal(
    dashboardViewFromHash(dashboardHashForView("colleges", "super_admin"), "super_admin"),
    "colleges",
  );
});

test("missing or unsupported dashboard hashes open overview", () => {
  for (const hash of ["", "#faculty", "#dashboard/unknown", "#dashboard/faculty/extra"]) {
    assert.equal(dashboardViewFromHash(hash), "overview");
  }
  assert.throws(() => dashboardHashForView("unknown"), /Unknown dashboard view/);
});

test("college navigation is available only to super administrators", () => {
  assert.equal(
    dashboardViewsForRole("super_admin").some((view) => view.id === "colleges"),
    true,
  );
  assert.equal(dashboardHashForView("colleges", "super_admin"), "#dashboard/colleges");
  assert.equal(dashboardViewFromHash("#dashboard/colleges", "super_admin"), "colleges");
  assert.equal(dashboardViewFromHash("#dashboard/colleges"), "overview");
  assert.throws(() => dashboardHashForView("colleges"), /Unknown dashboard view/);

  for (const role of ["department_admin", "unknown"]) {
    assert.equal(dashboardViewsForRole(role).some((view) => view.id === "colleges"), false);
    assert.equal(dashboardViewFromHash("#dashboard/colleges", role), "overview");
    assert.throws(() => dashboardHashForView("colleges", role), /Unknown dashboard view/);
  }
});

test("department administrators retain only their allowed dashboard sections", () => {
  for (const view of ["overview", "departments", "faculty"]) {
    assert.equal(
      dashboardViewFromHash(dashboardHashForView(view, "department_admin"), "department_admin"),
      view,
    );
  }
  assert.equal(dashboardViewFromHash("#dashboard/unsupported", "department_admin"), "overview");
});

test("a college hash falls back to overview when the account role changes", () => {
  const collegeHash = dashboardHashForView("colleges", "super_admin");
  assert.equal(dashboardViewFromHash(collegeHash, "department_admin"), "overview");
});
