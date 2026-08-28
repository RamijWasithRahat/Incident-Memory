import { useState } from "react";

import {
  searchSimilarIncidents,
} from "../api";


function SimilarSearchPage() {
  const [
    problemDescription,
    setProblemDescription,
  ] = useState("");

  const [service, setService] =
    useState("");

  const [severity, setSeverity] =
    useState("");

  const [topK, setTopK] =
    useState(5);

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleSearch(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data =
        await searchSimilarIncidents({
          problem_description:
            problemDescription.trim(),

          service:
            service.trim() || null,

          severity:
            severity || null,

          date_from: null,
          date_to: null,

          top_k:
            Number(topK),
        });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            SEMANTIC RETRIEVAL
          </p>

          <h2>
            Find similar historical incidents
          </h2>

          <p className="page-description">
            Describe a current failure in
            natural language. pgvector ranks
            related historical incidents by
            semantic similarity.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      <div className="search-layout">
        <div className="panel search-panel">
          <form
            className="form-stack"
            onSubmit={handleSearch}
          >
            <label>
              Current problem

              <textarea
                value={problemDescription}
                onChange={(event) =>
                  setProblemDescription(
                    event.target.value,
                  )
                }
                rows="6"
                minLength="3"
                required
                placeholder="Payment requests became slow after deployment and logs show database connection timeouts..."
              />
            </label>

            <div className="form-grid three">
              <label>
                Service

                <input
                  value={service}
                  onChange={(event) =>
                    setService(
                      event.target.value,
                    )
                  }
                  placeholder="Optional"
                />
              </label>

              <label>
                Severity

                <select
                  value={severity}
                  onChange={(event) =>
                    setSeverity(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Any
                  </option>

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

              <label>
                Top K

                <select
                  value={topK}
                  onChange={(event) =>
                    setTopK(
                      event.target.value,
                    )
                  }
                >
                  <option value="3">
                    3
                  </option>

                  <option value="5">
                    5
                  </option>

                  <option value="10">
                    10
                  </option>
                </select>
              </label>
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading
                ? "Searching vectors..."
                : "Find similar incidents"}
            </button>
          </form>
        </div>

        {result && (
          <div className="results-section">
            <div className="section-heading">
              <div>
                <h3>
                  Search results
                </h3>

                <p>
                  {result.count}
                  {" "}
                  historical incidents found
                </p>
              </div>
            </div>

            {result.results.length === 0 ? (
              <div className="panel empty-state">
                No matching incidents found.
              </div>
            ) : (
              <div className="search-results">
                {result.results.map(
                  (
                    incident,
                    index,
                  ) => (
                    <article
                      key={
                        incident.incident_id
                      }
                      className="search-result-card"
                    >
                      <div className="result-rank">
                        {index + 1}
                      </div>

                      <div className="result-content">
                        <div className="result-header">
                          <div>
                            <div className="incident-meta-row">
                              <span className="code-badge">
                                {
                                  incident.incident_code
                                }
                              </span>

                              <span className="tag">
                                {
                                  incident.service
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

                            <h3>
                              {
                                incident.title
                              }
                            </h3>
                          </div>

                          <div className="similarity-score">
                            <strong>
                              {
                                (
                                  incident.similarity
                                  * 100
                                ).toFixed(1)
                              }
                              %
                            </strong>

                            <span>
                              similarity
                            </span>
                          </div>
                        </div>

                        <div className="evidence-grid">
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
                              Historical solution
                            </strong>

                            <p>
                              {
                                incident.solution
                              }
                            </p>
                          </div>
                        </div>

                        {incident.evidence.length > 0 && (
                          <div className="retrieval-evidence">
                            <strong>
                              Best matching evidence
                            </strong>

                            {incident.evidence.map(
                              (item) => (
                                <div
                                  key={
                                    item.chunk_id
                                  }
                                  className="evidence-snippet"
                                >
                                  <span className="tag">
                                    {
                                      item.section
                                    }
                                  </span>

                                  <span>
                                    {
                                      item.text
                                    }
                                  </span>
                                </div>
                              ),
                            )}
                          </div>
                        )}
                      </div>
                    </article>
                  ),
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}


export default SimilarSearchPage;