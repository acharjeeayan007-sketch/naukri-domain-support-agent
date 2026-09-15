import express from "express";
import path from "path";
import { spawn } from "child_process";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;

app.use(express.json());

// Helper to execute Python agent bridge
function callAgentBridge(payload: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", ["agent_bridge.py"]);
    let stdoutData = "";
    let stderrData = "";

    pythonProcess.stdout.on("data", (data) => {
      stdoutData += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      stderrData += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error("Python process exited with error:", stderrData);
        return reject(new Error(`Agent bridge failed (exit code ${code}): ${stderrData}`));
      }
      try {
        const parsed = JSON.parse(stdoutData.trim());
        resolve(parsed);
      } catch (err) {
        console.error("Failed to parse agent bridge output:", stdoutData);
        reject(new Error("Invalid JSON response from agent bridge"));
      }
    });

    pythonProcess.stdin.write(JSON.stringify(payload));
    pythonProcess.stdin.end();
  });
}

// ================= API ROUTES =================

// Health check
app.get("/api/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "Naukri Domain Support Agent",
    version: "1.0.0",
    engine: "CrewAI Multi-Agent + RAG + Independent Compliance Review",
  });
});

// Chat endpoint
app.post("/api/chat", async (req, res) => {
  try {
    const { query } = req.body;
    if (!query || typeof query !== "string" || !query.trim()) {
      return res.status(400).json({ error: "Query is required." });
    }
    const result = await callAgentBridge({ action: "chat", query: query.trim() });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Applications dataset list & evaluation
app.get("/api/applications", async (req, res) => {
  try {
    const result = await callAgentBridge({ action: "dataset" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Single application lookup
app.get("/api/applications/:id", async (req, res) => {
  try {
    const recordId = req.params.id;
    const result = await callAgentBridge({ action: "lookup", record_id: recordId });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Knowledge base policies
app.get("/api/policies", async (req, res) => {
  try {
    const result = await callAgentBridge({ action: "policies" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Guardrails interactive test
app.post("/api/guardrails/test", async (req, res) => {
  try {
    const { text, mode, context } = req.body;
    const result = await callAgentBridge({ action: "test_guardrail", text, mode, context });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// RAG Evaluation comparison
app.get("/api/evaluation", async (req, res) => {
  try {
    const result = await callAgentBridge({ action: "evaluate" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// ================= VITE MIDDLEWARE / SPA FALLBACK =================

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Naukri Domain Support Agent Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
