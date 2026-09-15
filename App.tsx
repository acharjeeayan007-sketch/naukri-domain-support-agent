import React, { useState } from "react";
import { Bot, Users, BookOpen, Shield, BarChart3, Building2, CheckCircle2, ShieldAlert } from "lucide-react";
import { ChatConsole } from "./components/ChatConsole";
import { ApplicationTracker } from "./components/ApplicationTracker";
import { PolicyBrowser } from "./components/PolicyBrowser";
import { GuardrailsWorkbench } from "./components/GuardrailsWorkbench";
import { EvaluationDashboard } from "./components/EvaluationDashboard";

type ActiveTab = "chat" | "applications" | "policies" | "guardrails" | "evaluation";

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("chat");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-20 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-xs">
                <span className="text-xl tracking-tighter">N</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-base font-bold text-slate-900 leading-none">
                    Naukri.com Domain Support Agent
                  </h1>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                    HR & Recruitment
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Deterministic RAG &bull; CrewAI Multi-Agent &bull; Independent Compliance Review
                </p>
              </div>
            </div>

            {/* System Status Pills */}
            <div className="hidden md:flex items-center gap-2 text-xs">
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Deterministic 384-d RAG
              </span>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-medium flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                CrewAI Sequential Pipeline
              </span>
              <span className="px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-medium flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-indigo-600" />
                Compliance Review Team
              </span>
            </div>
          </div>

          {/* Sub-header Navigation Tabs */}
          <div className="flex space-x-1 overflow-x-auto py-1 border-t border-slate-100">
            <button
              id="tab-chat"
              onClick={() => setActiveTab("chat")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "chat"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Agent Chat & Governance</span>
            </button>

            <button
              id="tab-applications"
              onClick={() => setActiveTab("applications")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "applications"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Candidate Applications (50)</span>
            </button>

            <button
              id="tab-policies"
              onClick={() => setActiveTab("policies")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "policies"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Knowledge Base (12 Policies)</span>
            </button>

            <button
              id="tab-guardrails"
              onClick={() => setActiveTab("guardrails")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "guardrails"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Security & Guardrails Lab</span>
            </button>

            <button
              id="tab-evaluation"
              onClick={() => setActiveTab("evaluation")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "evaluation"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>RAG Chunking Benchmark</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === "chat" && <ChatConsole />}
        {activeTab === "applications" && <ApplicationTracker />}
        {activeTab === "policies" && <PolicyBrowser />}
        {activeTab === "guardrails" && <GuardrailsWorkbench />}
        {activeTab === "evaluation" && <EvaluationDashboard />}
      </main>

      {/* Persistent Footer */}
      <footer className="bg-white border-t border-slate-200 py-3 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-2">
          <div>Naukri.com Domain Support Agent &bull; Capstone Production Architecture</div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Escalation Cutoff: 0.6400</span>
            <span>RAG Grounding Cutoff: 0.1800</span>
            <span>Independent Compliance: Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
