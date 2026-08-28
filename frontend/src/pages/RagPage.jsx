import { useState } from "react";

import {
  askRag,
} from "../api";


function RagPage() {
  const [question, setQuestion] =
    useState("");

  const [service, setService] =
    useState("");

  const [severity, setSeverity] =
    useState("");

  const [section, setSection] =
    useState("");

  const [topK, setTopK] =
    useState(5);

  const [response, setResponse] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleAsk(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const data = await askRag({
        question:
          question.trim(),

        service:
          service.trim() || null,

        severity:
          severity || null,

        section:
          section.trim() || null,

        date_from: null,
        date_to: null,

        top_k:
          Number(topK),
      });

      setResponse(data);
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
            GROUNDED RAG
          </p>

          <h2>
            Ask Incident Memory
          </h2>

          <p className="page-description">
            Answers are generated locally by
            Qwen using only evidence retrieved
            from your historical incident
            knowledge base.
          </p>
        </div>

        <span className="local-model-badge">
          Local model · Free
        </span>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      <div className="rag-layout">
        <div className="panel">
          <form
            className="form-stack"
            onSubmit={handleAsk}
          >
            <label>
              Question

              <textarea
                rows="5"
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value,
                  )
                }
                minLength="3"
                required
                placeholder="Have we seen payment database timeout after deployment before?"
              />
            </label>

            <div className="form-grid">
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
            </div>

            <div className="form-grid">
              <label>
                Section

                <select
                  value={section}
                  onChange={(event) =>
                    setSection(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Any section
                  </option>

                  <option value="summary">
                    Summary
                  </option>

                  <option value="symptoms">
                    Symptoms
                  </option>

                  <option value="root_cause">
                    Root cause
                  </option>

                  <option value="solution">
                    Solution
                  </option>

                  <option value="checks">
                    Checks
                  </option>

                  <option value="resolution">
                    Resolution
                  </option>

                  <option value="prevention">
                    Prevention
                  </option>
                </select>
              </label>

              <label>
                Top K evidence

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
                ? "Retrieving evidence and generating..."
                : "Ask Incident Memory"}
            </button>

            {loading && (
              <p className="form-help">
                Qwen runs locally on CPU,
                so generation can take a
                little longer than a cloud API.
              </p>
            )}
          </form>
        </div>

        <div className="panel answer-panel">
          {!response ? (
            <div className="empty-state tall">
              <div className="empty-icon">
                RAG
              </div>

              <strong>
                No investigation yet
              </strong>

              <p>
                Ask a question to retrieve
                evidence and generate a
                grounded response.
              </p>
            </div>
          ) : (
            <>
              <div className="answer-heading">
                <div>
                  <span className="metric-label">
                    ANSWER
                  </span>

                  <h3>
                    Incident Memory response
                  </h3>
                </div>

                {response.insufficient_evidence ? (
                  <span className="warning-badge">
                    Insufficient evidence
                  </span>
                ) : (
                  <span className="grounded-badge">
                    Evidence grounded
                  </span>
                )}
              </div>

              <div
                className={
                  response.insufficient_evidence
                    ? "answer-text insufficient"
                    : "answer-text"
                }
              >
                {response.answer}
              </div>

              <div className="answer-metadata">
                <span>
                  Model:
                  {" "}
                  {
                    response.model
                    || "No generation"
                  }
                </span>

                <span>
                  Evidence:
                  {" "}
                  {
                    response.evidence_count
                  }
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {response?.sources?.length > 0 && (
        <section className="sources-section">
          <div className="section-heading">
            <div>
              <h3>
                Retrieved sources
              </h3>

              <p>
                Evidence supplied to the
                local language model.
              </p>
            </div>
          </div>

          <div className="sources-grid">
            {response.sources.map(
              (source) => (
                <article
                  key={
                    source.source_id
                  }
                  className="source-card"
                >
                  <div className="source-header">
                    <span className="source-id">
                      [
                      {
                        source.source_id
                      }
                      ]
                    </span>

                    <span className="similarity-pill">
                      {
                        (
                          source.similarity
                          * 100
                        ).toFixed(1)
                      }
                      %
                    </span>
                  </div>

                  <h4>
                    {
                      source.incident_code
                      || source.document_title
                    }
                  </h4>

                  <div className="tag-list">
                    <span className="tag">
                      {
                        source.section
                      }
                    </span>

                    {source.service && (
                      <span className="tag">
                        {
                          source.service
                        }
                      </span>
                    )}

                    {source.severity && (
                      <span className="tag">
                        {
                          source.severity
                        }
                      </span>
                    )}
                  </div>

                  <p className="source-text">
                    {source.text}
                  </p>

                  <div className="source-footer">
                    {
                      source.document_title
                    }
                  </div>
                </article>
              ),
            )}
          </div>
        </section>
      )}
    </section>
  );
}


export default RagPage;