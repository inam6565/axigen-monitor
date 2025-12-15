import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Server, Database, Users, Clock, Download } from "lucide-react";
import StatCard from "../components/StatCard";

const API_BASE_URL = "http://127.0.0.1:8000";

const useApi = (endpoint) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) throw new Error("Failed to fetch");
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [endpoint]);

  return { data, loading, error, refetch: fetchData };
};

function SectionCard({ title, right, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
        {right}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

const DashboardPage = () => {
  const { data: summary, loading: summaryLoading } = useApi("/summary");
  const { data: servers, loading: serversLoading } = useApi("/servers");
  const [serverStats, setServerStats] = useState([]);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchServerStats = async () => {
      if (!servers) return;

      setStatsLoading(true);
      const stats = await Promise.all(
        servers.map(async (server) => {
          try {
            const response = await fetch(
              `${API_BASE_URL}/domains/server/${server.id}`
            );
            const domains = await response.json();
            const totalAccounts = domains.reduce(
              (sum, domain) => sum + domain.total_accounts,
              0
            );

            return {
              name: server.name,
              domains: domains.length,
              accounts: totalAccounts,
            };
          } catch (error) {
            console.error("Error fetching domain stats:", error);
            return { name: server.name, domains: 0, accounts: 0 };
          }
        })
      );

      setServerStats(stats);
      setStatsLoading(false);
    };

    fetchServerStats();
  }, [servers]);

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
        icon={Server}
        label="Connected Servers"
        value={summary?.servers_count || 0}
        loading={summaryLoading}
        />
        <StatCard
        icon={Database}
        label="Total Domains"
        value={summary?.domains_count || 0}
        loading={summaryLoading}
        />
        <StatCard
        icon={Users}
        label="Total Accounts"
        value={summary?.accounts_count || 0}
        loading={summaryLoading}
        />
        <StatCard
        icon={Clock}
        label="Last Snapshot"
        value={formatDate(summary?.last_snapshot_time)}
        loading={summaryLoading}
        />
    </div>

      {/* Chart */}
      <SectionCard title="Domains distribution by server">
        {statsLoading ? (
          <div className="h-72 flex items-center justify-center">
            <p className="text-sm text-slate-500">Loading chart…</p>
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serverStats}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e2e8f0"
                  vertical={false}
                />
                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                  tick={{ fill: "#64748b", fontSize: 12 }}
                  axisLine={{ stroke: "#e2e8f0" }}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: "#64748b", fontSize: 12 }}
                  axisLine={{ stroke: "#e2e8f0" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    boxShadow: "0 10px 20px rgba(0,0,0,0.06)",
                  }}
                  cursor={{ fill: "#f1f5f9", opacity: 0.7 }}
                />
                <Bar
                  dataKey="domains"
                  fill="#3b82f6"
                  radius={[8, 8, 0, 0]}
                  maxBarSize={56}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </SectionCard>

      {/* Server Overview Table */}
      <SectionCard
        title="Server overview"
        right={
          <button className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-800">
            <Download className="h-4 w-4" />
            Export CSV
          </button>
        }
      >
        <div className="overflow-hidden rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr className="[&>th]:px-4 [&>th]:py-3 [&>th]:text-left [&>th]:font-semibold">
                  <th>Server Name</th>
                  <th>Hostname</th>
                  <th>Domains</th>
                  <th>Accounts</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {serversLoading || statsLoading ? (
                  <tr>
                    <td colSpan="4" className="py-10 text-center">
                      <p className="text-sm text-slate-500">Loading servers…</p>
                    </td>
                  </tr>
                ) : (
                  servers?.map((server) => {
                    const stats =
                      serverStats.find((s) => s.name === server.name) || {
                        domains: 0,
                        accounts: 0,
                      };

                    return (
                      <tr
                        key={server.id}
                        className="hover:bg-slate-50 transition-colors"
                      >
                        <td className="px-4 py-3 font-medium text-slate-900">
                          {server.name}
                        </td>
                        <td className="px-4 py-3 text-slate-600 tabular-nums font-mono">
                          {server.hostname}
                        </td>
                        <td className="px-4 py-3 tabular-nums font-semibold text-slate-900">
                          {stats.domains}
                        </td>
                        <td className="px-4 py-3 tabular-nums font-semibold text-emerald-600">
                          {stats.accounts}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </SectionCard>
    </div>
  );
};

export default DashboardPage;
