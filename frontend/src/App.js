import React, { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import ResultPanel from "./components/ResultPanel";

function App() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const handleQuery = async query => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const res = await fetch("/api/query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body.error || "Something went wrong");
      } else {
        setData(body);
      }
    } catch (e) {
      setError("Unable to connect to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <div className="app-shell container">
        <div className="row g-4 align-items-stretch">
          <div className="col-lg-4">
            <ChatInterface onSubmit={handleQuery} loading={loading} />
          </div>
          <div className="col-lg-8">
            <ResultPanel data={data} loading={loading} error={error} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
