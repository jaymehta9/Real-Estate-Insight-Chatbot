import React from "react";
import TrendChart from "./TrendChart";
import DataTable from "./DataTable";

function ResultPanel({ data, loading, error }) {
  if (loading && !data) {
    return (
      <div className="panel panel-right h-100 d-flex align-items-center justify-content-center">
        <div className="loader-pill">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel panel-right h-100 d-flex align-items-center justify-content-center">
        <div className="text-center">
          <h2 className="section-title mb-2">Something went wrong</h2>
          <p className="section-subtitle mb-0">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel panel-right h-100 d-flex align-items-center justify-content-center">
        <div className="text-center">
          <h2 className="section-title mb-2">No insights yet</h2>
          <p className="section-subtitle mb-0">
            Ask about a locality to see rich charts, summaries, and the filtered dataset.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel panel-right h-100 d-flex flex-column">

      {/* SUMMARY CARD */}
      <div className="summary-card mb-3">
        <div className="summary-pill">Insight summary</div>
        <p className="summary-text">{data.summary}</p>

        {/* POWERED BY OPENAI BADGE */}
        <div
          style={{
            display: "inline-block",
            marginTop: "6px",
            padding: "4px 10px",
            fontSize: "0.68rem",
            borderRadius: "999px",
            background: "#e0f2fe",
            color: "#0369a1",
            border: "1px solid #bae6fd",
            fontWeight: 500
          }}
        >
          Powered by OpenAI
        </div>

        <div className="summary-meta mt-3">
          <span className="meta-chip">
            Query
            <span className="meta-value">{data.query}</span>
          </span>
          <span className="meta-chip">
            Localities
            <span className="meta-value">{data.areas.join(", ")}</span>
          </span>
        </div>
      </div>

      <TrendChart chart={data.chart} />
      <DataTable rows={data.table} />
    </div>
  );
}

export default ResultPanel;
