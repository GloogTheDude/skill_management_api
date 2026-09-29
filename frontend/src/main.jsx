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
import MyTrainingRequestsPage from "./pages/MyTrainingRequestsPage";
import ManageTrainingRequestsPage from "./pages/ManageTrainingRequestsPage";
import EmployeeSkillSearchPage from "./pages/EmployeeSkillSearchPage";
import EmployeeSkillProfilePage from "./pages/EmployeeSkillProfilePage";
import ParticipationsPage from "./pages/ParticipationsPage";
import TrainingAdminPage from "./pages/TrainingAdminPage";
import ReferenceAdminPage from "./pages/ReferenceAdminPage";
import EmployeeAdminPage from "./pages/EmployeeAdminPage";
import EmployeeAcquisitionsPage from "./pages/EmployeeAcquisitionsPage";
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
            <Route path="training-requests" element={<MyTrainingRequestsPage />} />
            <Route path="requests" element={<Navigate to="/app/training-requests" replace />} />
            <Route path="manage-requests" element={<ManageTrainingRequestsPage />} />
            <Route path="employee-search" element={<EmployeeSkillSearchPage />} />
            <Route path="employees/:idEmployee/skills" element={<EmployeeSkillProfilePage />} />
            <Route path="employees/:idEmployee/acquisitions" element={<EmployeeAcquisitionsPage />} />
            <Route path="approvals" element={<PlaceholderPage title="Validations" />} />
            <Route path="employees" element={<EmployeeAdminPage />} />
            <Route path="training-admin" element={<TrainingAdminPage />} />
            <Route path="references" element={<ReferenceAdminPage />} />
            <Route path="participations" element={<ParticipationsPage />} />
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
