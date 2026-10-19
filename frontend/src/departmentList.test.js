import assert from "node:assert/strict";
import test from "node:test";
import { departmentEmptyMessage } from "./departmentList.js";

test("empty department text reflects the administrator's scope", () => {
  assert.equal(departmentEmptyMessage("super_admin"), "No departments found.");
  assert.equal(
    departmentEmptyMessage("department_admin"),
    "No assigned departments found.",
  );
});
