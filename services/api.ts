//  Base API endpoint (API Gateway)
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://vp9kv18c5m.execute-api.ap-south-1.amazonaws.com/prod";

// -------------------- Core API Helper --------------------
const api = {
  async request<T>(endpoint: string, options: RequestInit): Promise<T> {
    try {
      const res = await fetch(endpoint, options);
      const rawText = await res.text();
      let data: any;

      try {
        data = JSON.parse(rawText);
      } catch {
        data = rawText ? { message: rawText } : {};
      }

      // Parse Lambda proxy nested JSON
      if (typeof data?.body === "string") {
        try {
          data = JSON.parse(data.body);
        } catch {
          console.warn("Could not parse nested body JSON:", data.body);
        }
      }

      if (!res.ok) {
        throw new Error(data?.message || `HTTP error ${res.status}`);
      }

      return {
        success: data.success ?? true,
        message: data.message ?? "OK",
        ...data,
      } as T;
    } catch (err: any) {
      console.error("API request failed:", err.message);
      throw err;
    }
  },

  // ---------- POST helper ----------
  post<T>(endpoint: string, body: object): Promise<T> {
    const url = endpoint.startsWith("http")
      ? endpoint
      : `${API_BASE_URL}${endpoint}`;
    return this.request<T>(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },

  // ---------- GET helper ----------
  get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = endpoint.startsWith("http")
      ? new URL(endpoint)
      : new URL(`${API_BASE_URL}${endpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null) {
          url.searchParams.append(key, val);
        }
      });
    }

    return this.request<T>(url.toString(), { method: "GET" });
  },
};

// -------------------- AUTHENTICATION --------------------
export const login = async (role: string, id: string, password: string) => {
  const endpoint = "/login";
  const body =
    role === "faculty"
      ? { role, faculty_id: id, password }
      : { role, SAP_ID: id, password };

  const response = await api.post(endpoint, body);
  console.log("🔍 Parsed Login Response:", response);
  return response;
};

// -------------------- FACULTY API --------------------
export const getFacultyDetails = (faculty_id: string) =>
  api.get("/get-faculty-details", { faculty_id });

export const getFacultyTimetable = (faculty_id: string) =>
  api.get("/timetable", { faculty_id });

export const getEnrolledStudents = async (params: {
  class_id: string;
  subject: string;
}) => {
  try {
    const endpoint = "/get-enrolled-students";
    const res = await api.get<any>(endpoint, params);

    let parsedData: any[] = [];

    if (Array.isArray(res)) parsedData = res;
    else if (typeof res === "string") {
      try {
        parsedData = JSON.parse(res);
      } catch {
        console.warn("Could not parse string response:", res);
      }
    } else if (res.body) {
      try {
        const parsed = JSON.parse(res.body);
        parsedData = Array.isArray(parsed) ? parsed : [];
      } catch {
        console.warn("Could not parse res.body:", res.body);
      }
    } else if (res.Items) parsedData = res.Items;

    if (!Array.isArray(parsedData)) parsedData = [];

    console.log("Enrolled Students Loaded:", parsedData);
    return parsedData;
  } catch (err) {
    console.error("Error fetching enrolled students:", err);
    return [];
  }
};

// -------------------- FACE RECOGNITION --------------------
export const verifyFace = async (payload: any) => {
  const response = await fetch(`${API_BASE_URL}/verify-face`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error("Failed to verify face");
  return await response.json();
};

// -------------------- STUDENT: ACTIVE SESSION --------------------
export const getActiveSession = async (sapId: string) => {
  try {
    const response = await api.get("/get_active_session", { sapId });
    console.log("🎓 Active session data:", response);
    return response;
  } catch (err) {
    console.error("Error fetching active session:", err);
    return null;
  }
};

// -------------------- STUDENT: ATTENDANCE SUMMARY --------------------
export const getStudentAttendanceSummary = async (SAP_ID: string) => {
  try {
    const endpoint = "/get_student_attendance_summary";
    const response = await api.post<any>(endpoint, { SAP_ID });

    console.log("📘 Attendance summary:", response);
    return response;
  } catch (err) {
    console.error("Error fetching student attendance summary:", err);
    return { success: false, attendance: [] };
  }
};

// -------------------- STUDENT: LATE QUERIES --------------------
export const getStudentLateQueries = async (sapId: string) => {
  try {
    const response = await api.get("/queries", { sapId });
    const resJson = Array.isArray(response) ? response : response.Items || [];
    return resJson;
  } catch (err) {
    console.error("Error fetching late queries:", err);
    return [];
  }
};

// -------------------- STUDENT: SUBMIT QUERY --------------------
export const submitLateQuery = async (
  sapId: string,
  name: string,
  session: string,
  reason: string
) => {
  try {
    const body = {
      SAP_ID: sapId,
      name,
      session,
      reason,
      timestamp: new Date().toISOString(),
    };
    const response = await api.post("/queries", body);
    return response;
  } catch (err) {
    console.error("Error submitting late query:", err);
    throw err;
  }
};

// -------------------- RECORD ATTENDANCE (Mark Present) --------------------
export const recordAttendance = async (payload: {
  SAP_ID: string;
  Subject: string;
  Class_ID: string;
  Faculty_ID: string;
  Confidence?: number;
  Time?: string;
}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recordAttendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const text = await response.text();
      console.error("recordAttendance failed:", text);
      throw new Error(text);
    }
    return await response.json();
  } catch (err) {
    console.error("recordAttendance error:", err);
    throw err;
  }
};

// -------------------- CLOSE SESSION (Mark Absentees) --------------------
export const closeAttendanceSession = async (payload: {
  faculty_id: string;
  class_id: string;
  subject: string;
}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/closeSession`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("closeAttendanceSession failed:", text);
      throw new Error(text);
    }

    const result = await response.json();
    console.log("Session closed successfully:", result);
    return result;
  } catch (err) {
    console.error("closeAttendanceSession error:", err);
    throw err;
  }
};

export default api;
