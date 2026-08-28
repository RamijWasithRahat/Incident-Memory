import { useState } from "react";

import DashboardPage from "./pages/DashboardPage";
import IncidentsPage from "./pages/IncidentsPage";
import DocumentsPage from "./pages/DocumentsPage";
import SimilarSearchPage from "./pages/SimilarSearchPage";
import RagPage from "./pages/RagPage";


const navigation = [
  {
    id: "dashboard",
    label: "Dashboard",
    shortLabel: "Home",
  },
  {
    id: "incidents",
    label: "Incidents",
    shortLabel: "Incidents",
  },
  {
    id: "documents",
    label: "Documents",
    shortLabel: "Upload",
  },
  {
    id: "similar",
    label: "Similar Incidents",
    shortLabel: "Search",
  },
  {
    id: "rag",
    label: "RAG Assistant",
    shortLabel: "Ask AI",
  },
];


function App() {
  const [activePage, setActivePage] =
    useState("dashboard");

  function renderPage() {
    switch (activePage) {
      case "incidents":
        return <IncidentsPage />;

      case "documents":
        return <DocumentsPage />;

      case "similar":
        return <SimilarSearchPage />;

      case "rag":
        return <RagPage />;

      default:
        return (
          <DashboardPage
            navigate={setActivePage}
          />
        );
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            IM
          </div>

          <div>
            <h1>Incident Memory</h1>
            <p>Historical RAG Assistant</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <button
              key={item.id}
              type="button"
              className={
                activePage === item.id
                  ? "nav-button active"
                  : "nav-button"
              }
              onClick={() =>
                setActivePage(item.id)
              }
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />

          <span>
            Local AI + pgvector
          </span>
        </div>
      </aside>

      <div className="content-shell">
        <header className="mobile-header">
          <strong>
            Incident Memory
          </strong>
        </header>

        <main className="main-content">
          {renderPage()}
        </main>

        <nav className="mobile-nav">
          {navigation.map((item) => (
            <button
              key={item.id}
              type="button"
              className={
                activePage === item.id
                  ? "mobile-nav-button active"
                  : "mobile-nav-button"
              }
              onClick={() =>
                setActivePage(item.id)
              }
            >
              {item.shortLabel}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}


export default App;