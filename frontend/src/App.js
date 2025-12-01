import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./styles.css";
import ChatInterface from "./components/ChatInterface";
import ResultPanel from "./components/ResultPanel";

// This line is the ONLY functional change for deployment.
// It does NOT change the UI design.
const API_BASE =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleQuery = async (query) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/query/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "Server error");
      }

      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message || "Unable to connect to server");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-shell">
        <div className="row g-3">
          <div className="col-lg-4 col-12">
            <ChatInterface onSubmit={handleQuery} loading={loading} />
          </div>
          <div className="col-lg-8 col-12">
            <ResultPanel data={data} loading={loading} error={error} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
