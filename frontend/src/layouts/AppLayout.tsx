// src/layouts/AppLayout.tsx
import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import "../styles/pixel-theme.css";
import "../styles/layout.css";

function AppLayout() {
  return (
    <div className="pixel-app">
      <Sidebar />
      <main className="pixel-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AppLayout;