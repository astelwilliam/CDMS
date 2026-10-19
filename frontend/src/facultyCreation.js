export async function runFacultyCreationOnce(inProgress, task) {
  if (inProgress.current) return false;

  inProgress.current = true;
  try {
    await task();
    return true;
  } finally {
    inProgress.current = false;
  }
}
