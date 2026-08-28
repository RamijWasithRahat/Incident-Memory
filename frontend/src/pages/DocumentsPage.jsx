import {
  useEffect,
  useState,
} from "react";

import {
  listIncidents,
  uploadDocument,
} from "../api";


function DocumentsPage() {
  const [incidents, setIncidents] =
    useState([]);

  const [file, setFile] =
    useState(null);

  const [title, setTitle] =
    useState("");

  const [
    documentType,
    setDocumentType,
  ] = useState("runbook");

  const [
    incidentId,
    setIncidentId,
  ] = useState("");

  const [service, setService] =
    useState("");

  const [uploading, setUploading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [result, setResult] =
    useState(null);


  useEffect(() => {
    async function load() {
      try {
        const data =
          await listIncidents();

        setIncidents(data);
      } catch (err) {
        setError(err.message);
      }
    }

    load();
  }, []);


  async function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setError(
        "Select a .txt or .md file.",
      );

      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const response =
        await uploadDocument({
          file,
          title,
          documentType,
          incidentId,
          service,
        });

      setResult(response);

      setFile(null);
      setTitle("");
      setIncidentId("");
      setService("");

      event.target.reset();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }


  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            KNOWLEDGE INGESTION
          </p>

          <h2>
            Upload operational documents
          </h2>

          <p className="page-description">
            Add Markdown or plain-text
            runbooks. Incident Memory will
            parse, chunk, embed, and store
            them in pgvector.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      <div className="two-column-layout document-layout">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>
                Upload document
              </h3>

              <p>
                Supported formats:
                .md and .txt
              </p>
            </div>
          </div>

          <form
            className="form-stack"
            onSubmit={handleSubmit}
          >
            <label className="file-drop">
              <strong>
                Choose runbook
              </strong>

              <span>
                Maximum size: 2 MB
              </span>

              <input
                type="file"
                accept=".md,.txt,text/plain,text/markdown"
                onChange={(event) =>
                  setFile(
                    event.target.files?.[0]
                    || null,
                  )
                }
              />

              {file && (
                <span className="selected-file">
                  {file.name}
                </span>
              )}
            </label>

            <label>
              Display title

              <input
                value={title}
                onChange={(event) =>
                  setTitle(
                    event.target.value,
                  )
                }
                placeholder="Database Timeout Runbook"
              />
            </label>

            <label>
              Document type

              <input
                value={documentType}
                onChange={(event) =>
                  setDocumentType(
                    event.target.value,
                  )
                }
                placeholder="runbook"
              />
            </label>

            <label>
              Related incident

              <select
                value={incidentId}
                onChange={(event) =>
                  setIncidentId(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  No related incident
                </option>

                {incidents.map(
                  (incident) => (
                    <option
                      key={incident.id}
                      value={incident.id}
                    >
                      {
                        incident.incident_code
                      }
                      {" — "}
                      {
                        incident.title
                      }
                    </option>
                  ),
                )}
              </select>
            </label>

            <label>
              Service

              <input
                value={service}
                onChange={(event) =>
                  setService(
                    event.target.value,
                  )
                }
                placeholder="database"
              />
            </label>

            <button
              type="submit"
              className="primary-button"
              disabled={uploading}
            >
              {uploading
                ? "Parsing and embedding..."
                : "Upload document"}
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>
                Ingestion result
              </h3>

              <p>
                Document processing summary
              </p>
            </div>
          </div>

          {!result ? (
            <div className="empty-state tall">
              Upload a document to see
              its ingestion details.
            </div>
          ) : (
            <div className="result-summary">
              <span className="success-icon">
                ✓
              </span>

              <h3>
                Document indexed
              </h3>

              <p>
                {result.title}
              </p>

              <dl className="definition-list">
                <div>
                  <dt>
                    File
                  </dt>

                  <dd>
                    {
                      result.original_filename
                    }
                  </dd>
                </div>

                <div>
                  <dt>
                    Type
                  </dt>

                  <dd>
                    {
                      result.document_type
                    }
                  </dd>
                </div>

                <div>
                  <dt>
                    Chunks
                  </dt>

                  <dd>
                    {
                      result.chunk_count
                    }
                  </dd>
                </div>

                <div>
                  <dt>
                    Service
                  </dt>

                  <dd>
                    {
                      result.service
                      || "Not specified"
                    }
                  </dd>
                </div>
              </dl>

              <div className="tag-list">
                {result.sections.map(
                  (section) => (
                    <span
                      key={section}
                      className="tag"
                    >
                      {section}
                    </span>
                  ),
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


export default DocumentsPage;