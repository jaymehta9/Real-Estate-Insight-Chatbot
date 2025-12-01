import React from "react";

function DataTable({ rows }) {
  if (!rows || !rows.length) return null;

  const headers = Object.keys(rows[0] || {});

  const handleDownload = () => {
    const csvRows = [];
    csvRows.push(headers.join(","));
    rows.forEach(r => {
      const row = headers.map(h => {
        const raw = r[h] == null ? "" : String(r[h]);
        const escaped = raw.replace(/"/g, '""');
        if (
          escaped.includes(",") ||
          escaped.includes('"') ||
          escaped.includes("\n")
        ) {
          return `"${escaped}"`;
        }
        return escaped;
      });
      csvRows.push(row.join(","));
    });
    const blob = new Blob([csvRows.join("\n")], {
      type: "text/csv;charset=utf-8;"
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "filtered_data.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="table-card">
      <div className="table-header d-flex justify-content-between align-items-center">
        <div>
          <h2 className="section-title mb-0">Filtered dataset</h2>
          <p className="section-subtitle mb-0">
            Clean view of the matching rows from the Excel file.
          </p>
        </div>
        <button className="btn btn-outline-light btn-sm" onClick={handleDownload}>
          Download CSV
        </button>
      </div>
      <div className="table-responsive table-body mt-3">
        <table className="table table-sm align-middle mb-0">
          <thead>
            <tr>
              {headers.map(h => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx}>
                {headers.map(h => (
                  <td key={h}>{r[h]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
