import React, { useState, useEffect } from "react";
import { BarChart3, Award, TrendingUp, CheckCircle, HelpCircle, Layers, ArrowRight, RefreshCw } from "lucide-react";
import { ChunkingComparison } from "../types";

export const EvaluationDashboard: React.FC = () => {
  const [data, setData] = useState<ChunkingComparison | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchEvaluation = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/evaluation");
      const json = await res.json();
      if (json.evaluation) {
        setData(json.evaluation);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvaluation();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header and Recommendation Banner */}
      <div className="p-6 bg-white border border-slate-200 rounded-xl shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-blue-100 text-blue-700 rounded-lg">
                <BarChart3 className="w-5 h-5" />
              </span>
              <h2 className="text-lg font-bold text-slate-900">
                RAG Chunking Strategy Comparative Benchmark
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Empirical document-level benchmark comparing <strong>Fixed-Size with Overlap</strong> (180 chars, 40 overlap)
              against <strong>Sentence-Based Chunking</strong> across official Naukri policy queries.
            </p>
          </div>

          <button
            onClick={fetchEvaluation}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Re-run Benchmark
          </button>
        </div>

        {data && (
          <div className="mt-4 p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-3">
            <Award className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            <div className="text-xs text-emerald-900">
              <span className="font-bold text-sm block mb-0.5">Deployment Recommendation:</span>
              <p className="leading-relaxed">{data.recommendation}</p>
            </div>
          </div>
        )}
      </div>

      {/* Mean Metric Comparison Cards */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Fixed-Size Strategy Card */}
          <div className="p-5 bg-white border-2 border-blue-500 rounded-xl shadow-xs relative overflow-hidden">
            <div className="absolute top-3 right-3 px-2 py-0.5 bg-blue-600 text-white rounded text-[11px] font-bold uppercase tracking-wider">
              Selected Strategy
            </div>

            <div className="text-xs font-bold text-blue-600 uppercase tracking-wider">Strategy A</div>
            <h3 className="text-base font-bold text-slate-900 mt-0.5">Fixed-Size with Overlap (180/40)</h3>
            <div className="text-xs text-slate-400 mt-0.5">Collection: <code className="font-mono">naukri_fixed_chunks</code> ({data.fixed_strategy.chunk_count} chunks)</div>

            <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100">
              <div>
                <div className="text-xs text-slate-500">Document-Level Mean Precision</div>
                <div className="text-3xl font-black text-blue-600 mt-1">
                  {(data.fixed_strategy.mean_precision * 100).toFixed(1)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">Score: {data.fixed_strategy.mean_precision.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Document-Level Mean Recall</div>
                <div className="text-3xl font-black text-emerald-600 mt-1">
                  {(data.fixed_strategy.mean_recall * 100).toFixed(1)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">Score: {data.fixed_strategy.mean_recall.toFixed(4)}</div>
              </div>
            </div>
          </div>

          {/* Sentence-Based Strategy Card */}
          <div className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Strategy B</div>
            <h3 className="text-base font-bold text-slate-700 mt-0.5">Sentence-Based Boundary Chunking</h3>
            <div className="text-xs text-slate-400 mt-0.5">Collection: <code className="font-mono">naukri_sentence_chunks</code> ({data.sentence_strategy.chunk_count} chunks)</div>

            <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100">
              <div>
                <div className="text-xs text-slate-500">Document-Level Mean Precision</div>
                <div className="text-3xl font-black text-slate-600 mt-1">
                  {(data.sentence_strategy.mean_precision * 100).toFixed(1)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">Score: {data.sentence_strategy.mean_precision.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Document-Level Mean Recall</div>
                <div className="text-3xl font-black text-emerald-600 mt-1">
                  {(data.sentence_strategy.mean_recall * 100).toFixed(1)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">Score: {data.sentence_strategy.mean_recall.toFixed(4)}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Per-Query Arithmetic Breakdown Table */}
      {data && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-200">
            <h3 className="text-sm font-bold text-slate-900">
              Per-Query Document-Level Precision & Recall Arithmetic
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Deduplicates parent document IDs from the top-3 retrieved chunks and calculates exact fractions.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="p-3">Query ID & Prompt</th>
                  <th className="p-3">Ground Truth</th>
                  <th className="p-3">Fixed Retrieved</th>
                  <th className="p-3 text-blue-700">Fixed (P / R)</th>
                  <th className="p-3">Sentence Retrieved</th>
                  <th className="p-3 text-slate-700">Sentence (P / R)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.fixed_strategy.query_results.map((fRes, idx) => {
                  const sRes = data.sentence_strategy.query_results[idx];
                  return (
                    <tr key={fRes.query_id} className="hover:bg-slate-50">
                      <td className="p-3 max-w-xs">
                        <div className="font-mono font-bold text-slate-800">{fRes.query_id}</div>
                        <div className="text-slate-600 truncate mt-0.5">{fRes.query}</div>
                      </td>
                      <td className="p-3">
                        <span className="px-1.5 py-0.5 bg-slate-100 rounded font-mono text-[11px] text-slate-800">
                          {fRes.ground_truth.join(", ")}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-[11px]">
                        {fRes.retrieved_parent_docs.join(", ")}
                      </td>
                      <td className="p-3 font-mono font-bold text-blue-700">
                        P: {fRes.arithmetic_precision} | R: {fRes.arithmetic_recall}
                      </td>
                      <td className="p-3 font-mono text-[11px]">
                        {sRes.retrieved_parent_docs.join(", ")}
                      </td>
                      <td className="p-3 font-mono text-slate-700">
                        P: {sRes.arithmetic_precision} | R: {sRes.arithmetic_recall}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
