import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

const departments = [
  { id: "active-department", name: "Active Department", deleted_at: null },
  { id: "deleted-department", name: "Deleted Department", deleted_at: "2026-10-20T12:00:00Z" },
];

const faculty = [
  { id: "active", name: "Active Faculty", department_id: "active-department", deleted_at: null },
  { id: "deleted", name: "Deleted Faculty", department_id: "active-department", deleted_at: "2026-10-20T12:00:00Z" },
  { id: "orphaned", name: "Orphaned Faculty", department_id: "deleted-department", deleted_at: null },
  { id: "unresolved", name: "Unresolved Faculty", department_id: "missing-department", deleted_at: null },
];

function facultyCard(markup, name) {
  const cards = markup.match(/<article\b[^>]*>[\s\S]*?<\/article>/g) ?? [];
  const card = cards.find((candidate) => candidate.includes(`<h3>${name}</h3>`));
  assert.ok(card, `Missing ${name} faculty card`);
  return card;
}

test("faculty history stays visible, labeled, and read-only when unavailable", async () => {
  const vite = await createServer({ server: { middlewareMode: true, hmr: false } });
  try {
    const { default: FacultyList } = await vite.ssrLoadModule("/src/FacultyList.jsx");
    const markup = renderToStaticMarkup(
      createElement(FacultyList, { faculty, departments, role: "super_admin", onEdit() {} }),
    );

    assert.match(facultyCard(markup, "Active Faculty"), />Edit</);
    assert.match(facultyCard(markup, "Deleted Faculty"), /Deleted/);
    assert.doesNotMatch(facultyCard(markup, "Deleted Faculty"), />Edit</);
    assert.match(facultyCard(markup, "Orphaned Faculty"), /Read-only — Department deleted/);
    assert.doesNotMatch(facultyCard(markup, "Orphaned Faculty"), />Edit</);
    assert.doesNotMatch(facultyCard(markup, "Unresolved Faculty"), />Edit</);
  } finally {
    await vite.close();
  }
});

test("department administrators never see faculty edit controls", async () => {
  const vite = await createServer({ server: { middlewareMode: true, hmr: false } });
  try {
    const { default: FacultyList } = await vite.ssrLoadModule("/src/FacultyList.jsx");
    const markup = renderToStaticMarkup(
      createElement(FacultyList, { faculty, departments, role: "department_admin", onEdit() {} }),
    );

    assert.match(markup, /Active Faculty/);
    assert.doesNotMatch(markup, />Edit</);
  } finally {
    await vite.close();
  }
});
