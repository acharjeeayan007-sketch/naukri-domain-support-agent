import React, { useState, useEffect } from "react";
import { Search, AlertTriangle, CheckCircle, Clock, DollarSign, Filter, RefreshCw, Layers } from "lucide-react";
import { JobApplication } from "../types";

export const ApplicationTracker: React.FC = () => {
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [escalationOnly, setEscalationOnly] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<JobApplication | null>(null);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/applications");
      const data = await res.json();
      if (data.records) {
        // Also fetch escalation calculations for each
        const evaluated = await Promise.all(
          data.records.map(async (rec: any) => {
            const lookupRes = await fetch(`/api/applications/${rec.record_id}`);
            const lookupData = await lookupRes.json();
            return {
              ...rec,
              escalation_score: lookupData.result?.escalation_score,
              escalation_recommended: lookupData.result?.escalation_recommended,
              rationale: lookupData.result?.rationale,
            };
          })
        );
        setApplications(evaluated);
        if (evaluated.length > 0) setSelectedRecord(evaluated[0]);
      }
    } catch (err) {
      console.error("Failed to load applications", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const categories = ["all", ...Array.from(new Set(applications.map((a) => a.category)))];
  const statuses = ["all", ...Array.from(new Set(applications.map((a) => a.status)))];

  const filtered = applications.filter((app) => {
    if (categoryFilter !== "all" && app.category !== categoryFilter) return false;
    if (statusFilter !== "all" && app.status !== statusFilter) return false;
    if (escalationOnly && !app.escalation_recommended) return false;
    if (search) {
      const q = search.toLowerCase();
      const matchId = app.record_id.toLowerCase().includes(q);
      const matchCat = app.category.toLowerCase().includes(q);
      const matchStat = app.status.toLowerCase().includes(q);
      if (!matchId && !matchCat && !matchStat) return false;
    }
    return true;
  });

  const escalatedCount = applications.filter((a) => a.escalation_recommended).length;

  return (
    <div className="space-y-6">
      {/* Top metric summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase">Total Applications</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{applications.length}</div>
          <div className="text-xs text-slate-400 mt-1">Staged Candidate Pool</div>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase">Escalations Flagged</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{escalatedCount}</div>
          <div className="text-xs text-slate-400 mt-1">Score &ge; 0.6400 (80th percentile)</div>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase">Priority Review Flags</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {applications.filter((a) => a.flagged_priority_review).length}
          </div>
          <div className="text-xs text-slate-400 mt-1">Weight: 0.60 in formula</div>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase">Avg Days in Pipeline</div>
          <div className="text-2xl font-bold text-slate-800 mt-1">
            {applications.length ? (applications.reduce((acc, a) => acc + a.days_since_created, 0) / applications.length).toFixed(1) : 0} d
          </div>
          <div className="text-xs text-slate-400 mt-1">Weight: 0.40 in formula</div>
        </div>
      </div>

      {/* Filter and control bar */}
      <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1 min-w-[260px]">
          <Search className="w-4 h-4 text-slate-400 shrink-0" />
          <input
            id="app-search-input"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID (e.g. APP-1008), Category, or Status..."
            className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            id="category-filter"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All Categories" : c}
              </option>
            ))}
          </select>

          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none"
          >
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s === "all" ? "All Statuses" : s}
              </option>
            ))}
          </select>

          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-700 cursor-pointer bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200">
            <input
              id="escalation-filter-checkbox"
              type="checkbox"
              checked={escalationOnly}
              onChange={(e) => setEscalationOnly(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span>Escalated Only (&ge; 0.64)</span>
          </label>

          <button
            onClick={fetchApplications}
            className="p-1.5 text-slate-500 hover:text-blue-600 border border-slate-200 rounded-lg bg-slate-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Table + Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="overflow-x-auto max-h-[540px]">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider border-b border-slate-200 sticky top-0">
                <tr>
                  <th className="p-3">Record ID</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Salary (INR)</th>
                  <th className="p-3">Days</th>
                  <th className="p-3">Score</th>
                  <th className="p-3">Escalation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-slate-400">
                      Loading 50 deterministic application records...
                    </td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-slate-400">
                      No applications matched your filter criteria.
                    </td>
                  </tr>
                ) : (
                  filtered.map((app) => {
                    const isSelected = selectedRecord?.record_id === app.record_id;
                    return (
                      <tr
                        key={app.record_id}
                        id={`row-${app.record_id}`}
                        onClick={() => setSelectedRecord(app)}
                        className={`hover:bg-blue-50/50 cursor-pointer transition-colors ${
                          isSelected ? "bg-blue-50 font-medium" : ""
                        }`}
                      >
                        <td className="p-3 font-mono font-semibold text-slate-900">{app.record_id}</td>
                        <td className="p-3 text-slate-700">{app.category}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                            {app.status}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-slate-600">
                          ₹{app.expected_salary_inr.toLocaleString()}
                        </td>
                        <td className="p-3 text-slate-600">{app.days_since_created} d</td>
                        <td className="p-3 font-mono font-semibold text-slate-800">
                          {app.escalation_score !== undefined ? app.escalation_score.toFixed(4) : "--"}
                        </td>
                        <td className="p-3">
                          {app.escalation_recommended ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs font-semibold">
                              <AlertTriangle className="w-3 h-3" /> ESCALATE
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-xs">
                              <CheckCircle className="w-3 h-3" /> Normal
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Record Detail Panel */}
        <div className="lg:col-span-4 bg-white border border-slate-200 rounded-xl shadow-xs p-5 flex flex-col gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Escalation Formula Diagnostic
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Composite score: <code className="text-blue-600 font-mono">0.60 * priority + 0.40 * recency</code>
            </p>
          </div>

          {selectedRecord ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Record ID:</span>
                  <span className="font-mono font-bold text-sm text-slate-900">{selectedRecord.record_id}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Target Role:</span>
                  <span className="font-medium text-slate-800">{selectedRecord.category}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-800 font-medium">
                    {selectedRecord.status}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Expected Salary:</span>
                  <span className="font-mono font-semibold text-slate-800">
                    ₹{selectedRecord.expected_salary_inr.toLocaleString()} INR
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Days in Funnel:</span>
                  <span className="font-semibold text-slate-800">{selectedRecord.days_since_created} days</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Priority Review Flag:</span>
                  <span className={`font-semibold ${selectedRecord.flagged_priority_review ? "text-red-600" : "text-slate-600"}`}>
                    {selectedRecord.flagged_priority_review ? "TRUE (1.0)" : "FALSE (0.0)"}
                  </span>
                </div>
              </div>

              {/* Mathematical calculation breakdown */}
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                <div className="font-semibold text-slate-800">Calculated Escalation Score:</div>
                <div className="p-2 bg-white rounded border border-slate-200 font-mono text-[11px] space-y-1 text-slate-700">
                  <div>
                    Priority Component = 0.60 &times; {selectedRecord.flagged_priority_review ? "1.0" : "0.0"} ={" "}
                    <strong>{(0.6 * (selectedRecord.flagged_priority_review ? 1.0 : 0.0)).toFixed(4)}</strong>
                  </div>
                  <div>
                    Recency Component = 0.40 &times; ({selectedRecord.days_since_created} / 30) ={" "}
                    <strong>{(0.4 * (selectedRecord.days_since_created / 30.0)).toFixed(4)}</strong>
                  </div>
                  <div className="pt-1 border-t border-slate-200 text-blue-700 font-bold">
                    Composite Score = {selectedRecord.escalation_score?.toFixed(4)}
                  </div>
                </div>

                <div className="pt-1">
                  <div className="text-[11px] font-semibold text-slate-600">Threshold Rule:</div>
                  <div className="text-[11px] text-slate-600">
                    Score &ge; 0.6400 triggers immediate recruiter escalation alert.
                  </div>
                </div>

                <div className={`p-2.5 rounded-lg border font-semibold text-center ${
                  selectedRecord.escalation_recommended
                    ? "bg-amber-50 border-amber-200 text-amber-900"
                    : "bg-emerald-50 border-emerald-200 text-emerald-900"
                }`}>
                  {selectedRecord.escalation_recommended
                    ? "⚠️ ESCALATION MANDATED (Immediate Attention)"
                    : "✓ Standard Processing Cadence"}
                </div>
              </div>

              {selectedRecord.rationale && (
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="font-semibold text-slate-700 mb-1">Audit Rationale:</div>
                  <p className="text-slate-600 leading-relaxed">{selectedRecord.rationale}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400">
              Select an application record to inspect its escalation arithmetic.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
