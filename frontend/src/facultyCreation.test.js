import assert from "node:assert/strict";
import test from "node:test";
import { runFacultyCreationOnce } from "./facultyCreation.js";

test("a pending faculty creation ignores duplicate submissions", async () => {
  const inProgress = { current: false };
  let completeRequest;
  let requestCount = 0;
  const pendingRequest = new Promise((resolve) => {
    completeRequest = resolve;
  });

  const first = runFacultyCreationOnce(inProgress, async () => {
    requestCount += 1;
    await pendingRequest;
  });
  const second = await runFacultyCreationOnce(inProgress, () => {
    requestCount += 1;
  });

  assert.equal(second, false);
  assert.equal(requestCount, 1);
  assert.equal(inProgress.current, true);

  completeRequest();
  assert.equal(await first, true);
  assert.equal(inProgress.current, false);
});

test("faculty creation guard releases after a failed request", async () => {
  const inProgress = { current: false };
  await assert.rejects(
    runFacultyCreationOnce(inProgress, () => {
      throw new Error("request failed");
    }),
    /request failed/,
  );
  assert.equal(inProgress.current, false);
  assert.equal(await runFacultyCreationOnce(inProgress, async () => {}), true);
});
