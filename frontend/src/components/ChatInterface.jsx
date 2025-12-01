import React, { useState } from "react";

function ChatInterface({ onSubmit, loading }) {
  const [value, setValue] = useState("");

  const handleSubmit = e => {
    e.preventDefault();
    if (!value.trim() || loading) return;
    onSubmit(value.trim());
  };

  return (
    <div className="panel panel-left h-100 d-flex flex-column">
      <div className="panel-header mb-3">
        <div className="badge-soft">PRO</div>

        <h1 className="panel-title">Real Estate Insight Chatbot</h1>

        <p className="panel-subtitle">
          Ask for area insights, demand trends, and price growth in a single natural query.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="chat-form mt-auto">
        <label className="form-label subtle-label">Type a query</label>

        <div className="input-wrapper mb-2">
          <input
            className="form-control chat-input"
            value={value}
            onChange={e => setValue(e.target.value)}
            placeholder="Example: Compare Ambegaon Budruk and Aundh price trends"
          />
        </div>

        <button className="btn btn-primary w-100 chat-submit" disabled={loading}>
          {loading ? "Analyzing..." : "Generate Insights"}
        </button>

        <div className="quick-templates mt-3">
          {/* Single locality analysis */}
          <span
            className="template-pill"
            onClick={() => setValue("Give me analysis of Wakad")}
          >
            Analysis of Wakad
          </span>

          <span
            className="template-pill"
            onClick={() => setValue("Give me analysis of Akurdi")}
          >
            Analysis of Akurdi
          </span>

          <span
            className="template-pill"
            onClick={() => setValue("Give me analysis of Ambegaon Budruk")}
          >
            Analysis of Ambegaon Budruk
          </span>

          <span
            className="template-pill"
            onClick={() => setValue("Give me analysis of Aundh")}
          >
            Analysis of Aundh
          </span>

          {/* Comparisons */}
          <span
            className="template-pill"
            onClick={() =>
              setValue("Compare Ambegaon Budruk and Aundh demand trends")
            }
          >
            Ambegaon vs Aundh demand
          </span>

          <span
            className="template-pill"
            onClick={() =>
              setValue("Compare Wakad and Aundh price trends from 2020 to 2024")
            }
          >
            Wakad vs Aundh prices
          </span>

          <span
            className="template-pill"
            onClick={() =>
              setValue("Compare price and demand for Wakad, Aundh and Akurdi")
            }
          >
            Wakad · Aundh · Akurdi
          </span>

          <span
            className="template-pill"
            onClick={() =>
              setValue(
                "Which locality has higher demand between Ambegaon Budruk and Wakad?"
              )
            }
          >
            Ambegaon vs Wakad demand
          </span>

          {/* Trends / growth */}
          <span
            className="template-pill"
            onClick={() =>
              setValue("Show 5-year price trend for Akurdi")
            }
          >
            Akurdi 5-year trend
          </span>

          <span
            className="template-pill"
            onClick={() =>
              setValue("Show price growth for Ambegaon Budruk over the last 3 years")
            }
          >
            Ambegaon price growth
          </span>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
