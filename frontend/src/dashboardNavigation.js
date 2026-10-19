const dashboardViews = new Set(["overview", "departments", "faculty"]);

export function dashboardViewFromHash(hash) {
  const match = /^#dashboard\/(overview|departments|faculty)$/.exec(hash);
  return match && dashboardViews.has(match[1]) ? match[1] : "overview";
}

export function dashboardHashForView(view) {
  if (!dashboardViews.has(view)) {
    throw new Error("Unknown dashboard view");
  }
  return `#dashboard/${view}`;
}
