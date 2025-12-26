// src/components/StatCard.jsx
import React from "react";

const StatCard = ({ icon: Icon, label, value, loading }) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-slate-500">{label}</p>

          <p className="mt-2 text-3xl font-semibold tracking-tight tabular-nums text-slate-900">
            {loading ? "…" : value}
          </p>
        </div>

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900/5 text-slate-700">
          {Icon ? <Icon className="h-5 w-5" /> : null}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
