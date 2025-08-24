const { useState } = React;
const { createRoot } = ReactDOM;

function Spinner() {
  return (
    <div style={{ display: "inline-block", marginLeft: 8 }}>
      <svg
        width="18"
        height="18"
        viewBox="0 0 38 38"
        xmlns="http://www.w3.org/2000/svg"
        stroke="#555"
      >
        <g fill="none" fillRule="evenodd">
          <g transform="translate(1 1)" strokeWidth="2">
            <circle strokeOpacity=".3" cx="18" cy="18" r="18" />
            <path d="M36 18c0-9.94-8.06-18-18-18">
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 18 18"
                to="360 18 18"
                dur="0.9s"
                repeatCount="indefinite"
              />
            </path>
          </g>
        </g>
      </svg>
    </div>
  );
}

function App() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [hits, setHits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [pdfName, setPdfName] = useState(null);
  const [targetPage, setTargetPage] = useState(null);
  const [highlightText, setHighlightText] = useState("");

  async function ask() {
    setLoading(true);
    setAnswer("");
    setHits([]);
    try {
      const res = await fetch(`/chat_explain?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setAnswer(data.answer || "");
      setHits(data.hits || []);
      if (data.hits && data.hits.length > 0) {
        const h = data.hits[0];
        setPdfName(h.doc);
        setTargetPage(h.page);
        const words = (h.text || "").split(/\s+/).slice(0, 8).join(" ");
        setHighlightText(words);
      }
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(file) {
    const fd = new FormData();
    fd.append("file", file);
    setStatus("Uploading...");
    const res = await fetch("/upload", { method: "POST", body: fd });
    const data = await res.json();
    setStatus(data.message || JSON.stringify(data));
  }

  const encodedHighlight = encodeURIComponent(highlightText || "");

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: 12, borderBottom: "1px solid #eee" }}>
        <h2 style={{ margin: 0 }}>Financial RAG Bot</h2>
      </div>

      <div style={{ flex: 1, display: "flex" }}>
        <div style={{ flex: 1, padding: 16, overflow: "auto", borderRight: "1px solid #eee" }}>
          <div>
            <textarea
              placeholder="Ask a question..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              style={{ width: "100%", height: 120, padding: 10, fontSize: 16 }}
            />
            <div>
              <button onClick={ask} disabled={loading}>
                Ask {loading && <Spinner />}
              </button>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => e.target.files && uploadFile(e.target.files[0])}
            />
            <div style={{ marginTop: 8, color: "#555" }}>{status}</div>
          </div>
          <div style={{ marginTop: 16 }}>
            <div style={{ whiteSpace: "pre-wrap", border: "1px solid #ddd", padding: 10, borderRadius: 6 }}>
              {answer}
            </div>
            <div style={{ marginTop: 8 }}>
              <strong>Sources</strong>
              <ul>
                {hits.map((h, i) => (
                  <li key={i}>
                    <a
                      href={`#src-${i}`}
                      onClick={(e) => {
                        e.preventDefault();
                        setPdfName(h.doc);
                        setTargetPage(h.page);
                        const words = (h.text || "").split(/\s+/).slice(0, 8).join(" ");
                        setHighlightText(words);
                      }}
                      title={`Open ${h.doc} page ${h.page}`}
                    >
                      [{h.doc} p.{h.page}]
                    </a>
                    {typeof h.score === 'number' ? ` score=${h.score.toFixed(2)}` : ''}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div style={{ flex: 1, padding: 16, overflow: "hidden" }}>
          {pdfName ? (
            <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
              <div style={{ marginBottom: 8, color: "#555" }}>
                Viewing: {pdfName} {highlightText && `(highlighting match)`}
              </div>
              <iframe
                title="pdf"
                src={`/static/app/pdf.html?name=${encodeURIComponent(pdfName)}&page=${encodeURIComponent(
                  targetPage || ''
                )}&text=${encodedHighlight}`}
                style={{ width: "100%", height: "100%", border: "1px solid #ddd", borderRadius: 6 }}
              />
            </div>
          ) : (
            <div style={{ color: "#888" }}>Ask a question to view related PDF pages.</div>
          )}
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);


