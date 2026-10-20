import assert from "node:assert/strict";
import test from "node:test";
import { collegeEmptyMessage } from "./collegeList.js";

test("empty colleges list explains the absence of records", () => {
  assert.equal(collegeEmptyMessage(), "No colleges found.");
});
