const sharedViews = [
  { id: "overview", label: "Overview" },
  { id: "departments", label: "Departments" },
  { id: "faculty", label: "Faculty" },
];

export function dashboardViewsForRole(role) {
  return role === "super_admin"
    ? [...sharedViews, { id: "colleges", label: "Colleges" }]
    : sharedViews;
}

export function dashboardViewFromHash(hash, role) {
  const match = /^#dashboard\/(overview|departments|faculty|colleges)$/.exec(hash);
  const allowedViews = dashboardViewsForRole(role);
  return match && allowedViews.some((view) => view.id === match[1])
    ? match[1]
    : "overview";
}

export function dashboardHashForView(view, role) {
  if (!dashboardViewsForRole(role).some((allowed) => allowed.id === view)) {
    throw new Error("Unknown dashboard view");
  }
  return `#dashboard/${view}`;
}
