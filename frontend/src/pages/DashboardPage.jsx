import {
  useEffect,
  useState,
} from "react";

import {
  getHealth,
  listIncidents,
} from "../api";


function DashboardPage({
  navigate,
}) {
  const [health, setHealth] =
    useState(null);

  const [incidentCount, setIncidentCount] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [
          healthResult,
          incidents,
        ] = await Promise.all([
          getHealth(),
          listIncidents(),
        ]);

        setHealth(healthResult);

        setIncidentCount(
          incidents.length,
        );
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            INCIDENT OPERATIONS
          </p>

          <h2>
            Historical incident intelligence
          </h2>

          <p className="page-description">
            Search previous failures, retrieve
            relevant evidence, and generate
            grounded answers using your local
            RAG pipeline.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      <div className="metric-grid">
        <article className="metric-card">
          <span className="metric-label">
            API
          </span>

          <strong>
            {loading
              ? "Checking..."
              : health?.api === "up"
                ? "Online"
                : "Unavailable"}
          </strong>

          <p>
            FastAPI backend
          </p>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            DATABASE
          </span>

          <strong>
            {loading
              ? "Checking..."
              : health?.database === "up"
                ? "Online"
                : "Unavailable"}
          </strong>

          <p>
            PostgreSQL + pgvector
          </p>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            INCIDENTS
          </span>

          <strong>
            {loading
              ? "..."
              : incidentCount ?? "—"}
          </strong>

          <p>
            Historical records
          </p>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            GENERATION
          </span>

          <strong>
            Local
          </strong>

          <p>
            Qwen2.5-0.5B-Instruct
          </p>
        </article>
      </div>

      <div className="section-heading">
        <div>
          <h3>
            Main workflows
          </h3>

          <p>
            Choose what you want to do.
          </p>
        </div>
      </div>

      <div className="workflow-grid">
        <button
          type="button"
          className="workflow-card"
          onClick={() =>
            navigate("incidents")
          }
        >
          <span className="workflow-number">
            01
          </span>

          <h3>
            Incident Memory
          </h3>

          <p>
            Add and review structured
            historical incident records.
          </p>

          <span className="workflow-link">
            Manage incidents →
          </span>
        </button>

        <button
          type="button"
          className="workflow-card"
          onClick={() =>
            navigate("documents")
          }
        >
          <span className="workflow-number">
            02
          </span>

          <h3>
            Runbook Ingestion
          </h3>

          <p>
            Upload Markdown or text
            operational documents.
          </p>

          <span className="workflow-link">
            Upload document →
          </span>
        </button>

        <button
          type="button"
          className="workflow-card"
          onClick={() =>
            navigate("similar")
          }
        >
          <span className="workflow-number">
            03
          </span>

          <h3>
            Similar Incidents
          </h3>

          <p>
            Find historical incidents by
            semantic similarity.
          </p>

          <span className="workflow-link">
            Search history →
          </span>
        </button>

        <button
          type="button"
          className="workflow-card featured"
          onClick={() =>
            navigate("rag")
          }
        >
          <span className="workflow-number">
            04
          </span>

          <h3>
            RAG Assistant
          </h3>

          <p>
            Ask operational questions and
            receive evidence-grounded answers.
          </p>

          <span className="workflow-link">
            Ask Incident Memory →
          </span>
        </button>
      </div>
    </section>
  );
}


export default DashboardPage;