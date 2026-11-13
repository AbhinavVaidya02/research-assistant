import { useState } from "react";
import ReactMarkdown from "react-markdown";

const BACKEND_URL = "http://localhost:8000";

// Friendly labels for the agent names sent by the backend
const AGENT_LABELS = {
  research_planner_agent: "📝 Research Planner",
  web_researcher_agent: "🔎 Web Researcher",
  research_critic_agent: "🧐 Research Critic",
  report_writer_agent: "✍️ Report Writer",
};

export default function App() {
  const [topic, setTopic] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [timeline, setTimeline] = useState([]); // one entry per finished agent
  const [report, setReport] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  function startResearch() {
    setIsRunning(true);
    setTimeline([]);
    setReport("");
    setErrorMessage("");

    // EventSource = the browser's built-in client for Server-Sent Events.
    const eventSource = new EventSource(
      `${BACKEND_URL}/research/stream?topic=${encodeURIComponent(topic)}`
    );

    // Backend sends "agent_finished" every time one agent completes.
    eventSource.addEventListener("agent_finished", (event) => {
      const data = JSON.parse(event.data);
      setTimeline((previous) => [...previous, data]);
    });

    eventSource.addEventListener("final_report", (event) => {
      setReport(JSON.parse(event.data).report);
    });

    eventSource.addEventListener("error", (event) => {
      // Our backend's "error" event carries data. A dropped connection does not.
      if (event.data) setErrorMessage(JSON.parse(event.data).message);
    });

    eventSource.addEventListener("done", () => {
      eventSource.close(); // important: otherwise the browser auto-reconnects
      setIsRunning(false);
    });

    eventSource.onerror = () => {
      eventSource.close();
      setIsRunning(false);
    };
  }

  return (
    <div className="page">
      <h1>Research Assistant</h1>
      <p className="subtitle">4 agents · LangGraph · MCP tools · Gemini</p>

      <div className="input-row">
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. How do vector databases work?"
          disabled={isRunning}
        />
        <button onClick={startResearch} disabled={isRunning || !topic.trim()}>
          {isRunning ? "Researching..." : "Research"}
        </button>
      </div>

      {errorMessage && <div className="error">⚠️ {errorMessage}</div>}

      <div className="timeline">
        {timeline.map((step, index) => (
          <div className="step" key={index}>
            <strong>{AGENT_LABELS[step.agent] || step.agent}</strong>
            <pre>{step.message}</pre>
          </div>
        ))}
        {isRunning && <div className="step working">Agents are working…</div>}
      </div>

      {report && (
        <div className="report">
          <ReactMarkdown>{report}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
