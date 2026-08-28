import {
  useEffect,
  useState,
} from "react";

import {
  createIncident,
  deleteIncident,
  listIncidents,
} from "../api";


const emptyForm = {
  incident_code: "",
  title: "",
  service: "",
  severity: "SEV-2",
  incident_date: "",
  symptoms: "",
  root_cause: "",
  solution: "",
  notes: "",
};


function IncidentsPage() {
  const [incidents, setIncidents] =
    useState([]);

  const [form, setForm] =
    useState(emptyForm);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [expandedId, setExpandedId] =
    useState(null);


  async function loadIncidents() {
    setLoading(true);
    setError("");

    try {
      const data =
        await listIncidents();

      setIncidents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadIncidents();
  }, []);


  function updateForm(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }


  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    const payload = {
      ...form,

      incident_code:
        form.incident_code.trim(),

      title:
        form.title.trim(),

      service:
        form.service.trim(),

      severity:
        form.severity.trim(),

      symptoms:
        form.symptoms.trim(),

      root_cause:
        form.root_cause.trim(),

      solution:
        form.solution.trim(),

      notes:
        form.notes.trim() || null,
    };

    try {
      const created =
        await createIncident(payload);

      setSuccess(
        `${created.incident_code} was created and indexed successfully.`,
      );

      setForm(emptyForm);

      await loadIncidents();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(
    incident,
  ) {
    const confirmed =
      window.confirm(
        `Delete ${incident.incident_code}?`,
      );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await deleteIncident(
        incident.id,
      );

      setSuccess(
        `${incident.incident_code} was deleted.`,
      );

      setExpandedId(null);

      await loadIncidents();
    } catch (err) {
      setError(err.message);
    }
  }


  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            INCIDENT MEMORY
          </p>

          <h2>
            Historical incidents
          </h2>

          <p className="page-description">
            Store structured incidents.
            New records are automatically
            embedded for semantic retrieval.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadIncidents}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      {success && (
        <div className="alert success">
          {success}
        </div>
      )}

      <div className="two-column-layout">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>
                Add incident
              </h3>

              <p>
                Create a historical failure
                record.
              </p>
            </div>
          </div>

          <form
            className="form-stack"
            onSubmit={handleSubmit}
          >
            <div className="form-grid">
              <label>
                Incident code

                <input
                  name="incident_code"
                  value={
                    form.incident_code
                  }
                  onChange={updateForm}
                  placeholder="INC-042"
                  required
                />
              </label>

              <label>
                Severity

                <select
                  name="severity"
                  value={form.severity}
                  onChange={updateForm}
                  required
                >
                  <option value="SEV-1">
                    SEV-1
                  </option>

                  <option value="SEV-2">
                    SEV-2
                  </option>

                  <option value="SEV-3">
                    SEV-3
                  </option>

                  <option value="SEV-4">
                    SEV-4
                  </option>
                </select>
              </label>
            </div>

            <label>
              Title

              <input
                name="title"
                value={form.title}
                onChange={updateForm}
                placeholder="Payment API database timeout"
                required
              />
            </label>

            <div className="form-grid">
              <label>
                Service

                <input
                  name="service"
                  value={form.service}
                  onChange={updateForm}
                  placeholder="payment-service"
                  required
                />
              </label>

              <label>
                Incident date

                <input
                  type="date"
                  name="incident_date"
                  value={
                    form.incident_date
                  }
                  onChange={updateForm}
                  required
                />
              </label>
            </div>

            <label>
              Symptoms

              <textarea
                name="symptoms"
                value={form.symptoms}
                onChange={updateForm}
                rows="4"
                placeholder="What was observed?"
                required
              />
            </label>

            <label>
              Root cause

              <textarea
                name="root_cause"
                value={
                  form.root_cause
                }
                onChange={updateForm}
                rows="4"
                placeholder="What caused the historical incident?"
                required
              />
            </label>

            <label>
              Solution

              <textarea
                name="solution"
                value={form.solution}
                onChange={updateForm}
                rows="4"
                placeholder="How was it resolved?"
                required
              />
            </label>

            <label>
              Notes

              <textarea
                name="notes"
                value={form.notes}
                onChange={updateForm}
                rows="3"
                placeholder="Optional notes"
              />
            </label>

            <button
              className="primary-button"
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Creating and embedding..."
                : "Create incident"}
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>
                Incident library
              </h3>

              <p>
                {incidents.length}
                {" "}
                records
              </p>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              Loading incidents...
            </div>
          ) : incidents.length === 0 ? (
            <div className="empty-state">
              No incidents have been
              stored yet.
            </div>
          ) : (
            <div className="incident-list">
              {incidents.map(
                (incident) => {
                  const expanded =
                    expandedId
                    === incident.id;

                  return (
                    <article
                      key={incident.id}
                      className="incident-card"
                    >
                      <button
                        type="button"
                        className="incident-summary"
                        onClick={() =>
                          setExpandedId(
                            expanded
                              ? null
                              : incident.id,
                          )
                        }
                      >
                        <div>
                          <div className="incident-meta-row">
                            <span className="code-badge">
                              {
                                incident.incident_code
                              }
                            </span>

                            <span
                              className={
                                `severity-badge ${incident.severity.toLowerCase()}`
                              }
                            >
                              {
                                incident.severity
                              }
                            </span>
                          </div>

                          <h4>
                            {
                              incident.title
                            }
                          </h4>

                          <p>
                            {
                              incident.service
                            }
                            {" · "}
                            {
                              incident.incident_date
                            }
                          </p>
                        </div>

                        <span>
                          {expanded
                            ? "−"
                            : "+"}
                        </span>
                      </button>

                      {expanded && (
                        <div className="incident-details">
                          <div>
                            <strong>
                              Symptoms
                            </strong>

                            <p>
                              {
                                incident.symptoms
                              }
                            </p>
                          </div>

                          <div>
                            <strong>
                              Root cause
                            </strong>

                            <p>
                              {
                                incident.root_cause
                              }
                            </p>
                          </div>

                          <div>
                            <strong>
                              Solution
                            </strong>

                            <p>
                              {
                                incident.solution
                              }
                            </p>
                          </div>

                          {incident.notes && (
                            <div>
                              <strong>
                                Notes
                              </strong>

                              <p>
                                {
                                  incident.notes
                                }
                              </p>
                            </div>
                          )}

                          <button
                            type="button"
                            className="danger-button"
                            onClick={() =>
                              handleDelete(
                                incident,
                              )
                            }
                          >
                            Delete incident
                          </button>
                        </div>
                      )}
                    </article>
                  );
                },
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


export default IncidentsPage;