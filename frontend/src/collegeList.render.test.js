import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

test("college list renders loaded records and an informative empty state", async () => {
  const vite = await createServer({ server: { middlewareMode: true } });
  try {
    const { default: CollegeList } = await vite.ssrLoadModule("/src/CollegeList.jsx");
    const records = renderToStaticMarkup(
      createElement(CollegeList, {
        colleges: [
          {
            id: "college-1",
            name: "Engineering",
            description: "Technical programs",
            contact_information: "engineering@example.com",
          },
          { id: "college-2", name: "Arts", description: null, contact_information: null },
        ],
      }),
    );

    assert.match(records, /Engineering/);
    assert.match(records, /Technical programs/);
    assert.match(records, /engineering@example\.com/);
    assert.match(records, /Arts/);
    assert.match(records, /No description provided\./);
    assert.doesNotMatch(records, /college-1/);

    const empty = renderToStaticMarkup(createElement(CollegeList, { colleges: [] }));
    assert.match(empty, /No colleges found\./);
    assert.match(empty, /class="empty-state"/);
  } finally {
    await vite.close();
  }
});
