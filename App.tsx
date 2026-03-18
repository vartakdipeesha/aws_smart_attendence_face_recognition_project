import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import FacultyDashboard from './pages/FacultyDashboard';
import StudentDashboard from './pages/StudentDashboard';
import { Toaster } from 'react-hot-toast'; 

// -------------------- ROUTES --------------------
const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Default route */}
      <Route path="/" element={<LoginPage />} />

      {/* Role-based protection */}
      <Route
        path="/faculty-dashboard"
        element={
          user && user.role === 'faculty' ? (
            <FacultyDashboard />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/student-dashboard"
        element={
          user && user.role === 'student' ? (
            <StudentDashboard />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      {/* Fallback for unknown paths */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

// -------------------- APP WRAPPER --------------------
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        {/* Global Toaster */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#1a1a1a',
              color: '#00ff99',
              fontWeight: 'bold',
              border: '1px solid #00ff99',
            },
          }}
        />

        <AppRoutes />
      </Router>
    </AuthProvider>
  );
};

export default App;
