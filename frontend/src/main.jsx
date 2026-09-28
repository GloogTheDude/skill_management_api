import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import AppLayout from "./components/AppLayout";
import PlaceholderPage from "./components/PlaceholderPage";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import MySkillsPage from "./pages/MySkillsPage";
import AvailableTrainingsPage from "./pages/AvailableTrainingsPage";
import "./styles.css";

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/app" element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="skills" element={<MySkillsPage />} />
            <Route path="available-trainings" element={<AvailableTrainingsPage />} />
            <Route path="trainings" element={<AvailableTrainingsPage />} />
            <Route path="training-requests" element={<PlaceholderPage title="Mes demandes de formation" />} />
            <Route path="employee-search" element={<PlaceholderPage title="Recherche employés" />} />
            <Route path="approvals" element={<PlaceholderPage title="Validations" />} />
            <Route path="employees" element={<PlaceholderPage title="Employees" />} />
            <Route path="training-admin" element={<PlaceholderPage title="Trainings" />} />
            <Route path="references" element={<PlaceholderPage title="Référentiels" />} />
            <Route path="participations" element={<PlaceholderPage title="Participations" />} />
            <Route path="skill-validations" element={<PlaceholderPage title="Skill validations" />} />
          </Route>
        </Route>
        <Route path="/" element={<Navigate to="/app" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>,
);
