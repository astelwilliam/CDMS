export async function loadAdministrativeData(api, role) {
  const requests = [
    api.get("/departments/", { params: { skip: 0, limit: 100 } }),
    api.get("/faculty_members/", { params: { skip: 0, limit: 100 } }),
  ];

  if (role === "super_admin") {
    requests.push(api.get("/colleges/", { params: { skip: 0, limit: 100 } }));
  }

  const [departments, faculty, colleges] = await Promise.all(requests);
  return {
    departments: departments.data,
    faculty: faculty.data,
    colleges: colleges?.data || [],
  };
}

export async function createFacultyMember(api, values) {
  const response = await api.post("/faculty_members/", values);
  return response.data;
}

export function requestErrorMessage(error) {
  const status = error?.response?.status;
  if (status === 401) return "";
  if (status === 403) return "Your account is not authorized for this action.";
  if (status === 404) return "The selected department is unavailable.";
  if (status === 503) return "The service is temporarily unavailable. Try again.";
  return "CDMS data could not be loaded.";
}

const FACULTY_UPDATE_FIELDS = [
  "name",
  "title",
  "biography",
  "contact_information",
  "profile_image_reference",
];

export async function updateFacultyMember(api, facultyId, values) {
  const payload = {};

  for (const field of FACULTY_UPDATE_FIELDS) {
    if (Object.prototype.hasOwnProperty.call(values, field)) {
      payload[field] = values[field];
    }
  }

  const response = await api.put(
    `/faculty_members/${encodeURIComponent(facultyId)}`,
    payload,
  );

  return response.data;
}
