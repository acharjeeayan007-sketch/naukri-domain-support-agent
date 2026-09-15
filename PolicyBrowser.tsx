import React, { useState, useEffect } from "react";
import { BookOpen, Search, Tag, Building2, Calendar, FileText, ExternalLink } from "lucide-react";
import { PolicyDocument } from "../types";

export const PolicyBrowser: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedDoc, setSelectedDoc] = useState<PolicyDocument | null>(null);

  useEffect(() => {
    fetch("/api/policies")
      .then((res) => res.json())
      .then((data) => {
        if (data.policies) {
          setPolicies(data.policies);
          setSelectedDoc(data.policies[0]);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filtered = policies.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      p.doc_id.toLowerCase().includes(q) ||
      p.title.toLowerCase().includes(q) ||
      p.topic.toLowerCase().includes(q) ||
      p.content.toLowerCase().includes(q)
    );
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[720px]">
      {/* Left List of Documents */}
      <div className="lg:col-span-5 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col overflow-hidden">
        <div className="p-4 border-b border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              Naukri HR Knowledge Base
            </h3>
            <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full font-medium">
              {policies.length} Policies
            </span>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              id="policy-search-input"
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search policies, topics, or keywords..."
              className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-2">
          {loading ? (
            <div className="p-8 text-center text-slate-400 text-xs">Loading Knowledge Base...</div>
          ) : filtered.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">No matching policy documents found.</div>
          ) : (
            filtered.map((doc) => {
              const isSelected = selectedDoc?.doc_id === doc.doc_id;
              return (
                <div
                  key={doc.doc_id}
                  id={`policy-item-${doc.doc_id}`}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    isSelected
                      ? "bg-blue-50 border border-blue-200"
                      : "hover:bg-slate-50 border border-transparent"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-mono text-xs font-bold text-blue-700 bg-blue-100/70 px-1.5 py-0.5 rounded">
                      {doc.doc_id}
                    </span>
                    <span className="text-[11px] text-slate-400">{doc.metadata.department}</span>
                  </div>
                  <h4 className="text-xs font-semibold text-slate-800 leading-snug line-clamp-1">{doc.title}</h4>
                  <p className="text-[11px] text-slate-500 line-clamp-2 mt-1">{doc.content}</p>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right Document Full View */}
      <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl shadow-xs p-6 overflow-y-auto flex flex-col justify-between">
        {selectedDoc ? (
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-xs font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
                  {selectedDoc.doc_id}
                </span>
                <span className="text-xs px-2.5 py-0.5 bg-slate-100 text-slate-700 rounded-full font-medium flex items-center gap-1">
                  <Tag className="w-3 h-3 text-slate-400" />
                  {selectedDoc.topic}
                </span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 leading-tight">{selectedDoc.title}</h2>
            </div>

            <div className="flex flex-wrap gap-4 py-3 border-y border-slate-100 text-xs text-slate-600">
              <div className="flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Department: <strong>{selectedDoc.metadata.department}</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Version: <strong>{selectedDoc.metadata.version}</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                <span>Category: <strong>{selectedDoc.metadata.category}</strong></span>
              </div>
            </div>

            <div>
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Official Policy Provision (Canon)
              </h3>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm leading-relaxed text-slate-800 font-serif">
                {selectedDoc.content}
              </div>
            </div>

            <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-xl text-xs space-y-2">
              <div className="font-semibold text-blue-900 flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                RAG Embedding & Vector Indexing Diagnostics
              </div>
              <p className="text-blue-800/80">
                This document is indexed in both <strong>Fixed-Size (180 chars, 40 overlap)</strong> and{" "}
                <strong>Sentence-Based</strong> ChromaDB vector stores with 384-dimensional dense projections.
                The Grounded Answer Generator queries this text using a calibrated cosine similarity cutoff of <strong>0.1800</strong>.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
            <BookOpen className="w-10 h-10 mb-2 text-slate-300" />
            <p>Select a policy document to view full provisions and indexing parameters.</p>
          </div>
        )}
      </div>
    </div>
  );
};
