
import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";

interface User {
  faculty_id?: string;
  SAP_ID?: string;
  name: string;
  role: "faculty" | "student";
  class_id?: string;
  subject?: string;
  image_key?: string;
}

interface AuthContextType {
  user: User | null;
  faculty: User | null;
  login: (userData: any) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const saved = localStorage.getItem("user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  const login = (userData: any) => {
    const normalizedUser: User = {
      faculty_id: userData.faculty_id,
      SAP_ID: userData.SAP_ID,
      name: userData.name,
      role: userData.role || "student",
      class_id: userData.class_id,
      subject: userData.subject,
      image_key: userData.image_key,
    };
    setUser(normalizedUser);
    localStorage.setItem("user", JSON.stringify(normalizedUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
    sessionStorage.clear();
  };

  const faculty = user?.role === "faculty" ? user : null;

  return <AuthContext.Provider value={{ user, faculty, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};
