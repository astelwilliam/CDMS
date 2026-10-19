import assert from "node:assert/strict";
import test from "node:test";
import { dashboardHashForView, dashboardViewFromHash } from "./dashboardNavigation.js";

test("dashboard section survives refresh through its URL hash", () => {
  for (const view of ["overview", "departments", "faculty"]) {
    assert.equal(dashboardViewFromHash(dashboardHashForView(view)), view);
  }
});

test("missing or unsupported dashboard hashes open overview", () => {
  for (const hash of ["", "#faculty", "#dashboard/unknown", "#dashboard/faculty/extra"]) {
    assert.equal(dashboardViewFromHash(hash), "overview");
  }
  assert.throws(() => dashboardHashForView("unknown"), /Unknown dashboard view/);
});
