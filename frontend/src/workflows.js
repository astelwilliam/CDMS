const LIST_PAGE_SIZE = 100;
const MAX_LIST_PAGES = 1000;

async function loadAllPages(api, path) {
  const records = [];
  const seenIds = new Set();

  for (let pageNumber = 0; pageNumber < MAX_LIST_PAGES; pageNumber += 1) {
    const response = await api.get(path, {
      params: { skip: pageNumber * LIST_PAGE_SIZE, limit: LIST_PAGE_SIZE },
    });
    const page = response.data;

    if (!Array.isArray(page)) {
      throw new Error(`Unexpected list response from ${path}`);
    }

    for (const record of page) {
      if (record?.id == null || seenIds.has(record.id)) {
        throw new Error(`Repeated or invalid list record from ${path}`);
      }
      seenIds.add(record.id);
    }

    records.push(...page);
    if (page.length < LIST_PAGE_SIZE) return records;
  }

  throw new Error(`List page limit exceeded for ${path}`);
}

export async function loadAdministrativeData(api, role) {
  const requests = [
    loadAllPages(api, "/departments/"),
    loadAllPages(api, "/faculty_members/"),
  ];

  if (role === "super_admin") {
    requests.push(loadAllPages(api, "/colleges/"));
  }

  const [departments, faculty, colleges] = await Promise.all(requests);
  return {
    departments,
    faculty,
    colleges: colleges || [],
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
