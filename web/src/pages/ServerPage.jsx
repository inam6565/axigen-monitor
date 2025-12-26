import React, { useState, useEffect } from "react";
import { Download, Trash2 } from "lucide-react"; // Importing the Delete icon
import { useNavigate } from "react-router-dom"; // For redirection
import Papa from "papaparse"; // Import PapaParse for CSV export
import API_BASE_URL from "../config/api";

// Fetch data hook
const useApi = (endpoint) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}${endpoint}/`);
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

const ServerPage = () => {
  const { data: servers, loading: serversLoading } = useApi("/servers"); // Fetch servers list
  const [serverStats, setServerStats] = useState([]);
  const [statsLoading, setStatsLoading] = useState(true);

  const navigate = useNavigate(); // For navigation

  useEffect(() => {
    const fetchServerStats = async () => {
      if (!servers) return;

      setStatsLoading(true);
      const stats = await Promise.all(
        servers.map(async (server) => {
          try {
            const response = await fetch(`${API_BASE_URL}/domains/server/${server.id}/`);
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

  // Function to handle exporting data to CSV
  const handleExportCSV = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/report/`);
      if (!response.ok) {
        console.error("Failed to fetch report data. Status:", response.status);
        throw new Error("Failed to fetch report data");
      }

      const data = await response.json();
      const processedData = [];

      data.servers.forEach((server) => {
        server.domains.forEach((domain) => {
          domain.accounts.forEach((account) => {
            processedData.push({
              Server: server.name,
              Hostname: server.hostname,
              Domain: domain.name,
              Account: account.email,
              Status: account.status || "N/A",
              AssignedMB: account.assigned_mb,
              UsedMB: account.used_mb,
              FreeMB: account.free_mb,
            });
          });
        });
      });

      const csv = Papa.unparse(processedData);
      const blob = new Blob([csv], { type: "text/csv" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "server_report.csv";
      link.click();
    } catch (error) {
      console.error("Error exporting CSV:", error);
    }
  };

  // Function to delete a server
  const handleDeleteServer = async (hostname) => {
    const confirmed = window.confirm(`Are you sure you want to delete server ${hostname}?`);
    if (!confirmed) return;

    try {
      const response = await fetch(`${API_BASE_URL}/delete_server/`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ hostname }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to delete server");
      }

      alert(`Server ${hostname} deleted successfully!`);
      // Refetch the server data after deletion
      setServerStats((prevStats) => prevStats.filter((server) => server.hostname !== hostname));
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Server Overview Table */}
      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-900">Server Overview</h2>
          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-800"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
        </div>
        <div className="p-5">
          {serversLoading || statsLoading ? (
            <div className="text-center">Loading server data...</div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-200">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-600">
                    <tr className="[&>th]:px-4 [&>th]:py-3 [&>th]:text-left [&>th]:font-semibold">
                      <th>Server Name</th>
                      <th>Hostname</th>
                      <th>Domains</th>
                      <th>Accounts</th>
                      <th>Actions</th> {/* Added Actions column */}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {servers?.map((server) => {
                      const stats = serverStats.find((s) => s.name === server.name) || {
                        domains: 0,
                        accounts: 0,
                      };

                      return (
                        <tr key={server.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-slate-900">{server.name}</td>
                          <td className="px-4 py-3 text-slate-600">{server.hostname}</td>
                          <td className="px-4 py-3 text-slate-900">{stats.domains}</td>
                          <td className="px-4 py-3 text-emerald-600">{stats.accounts}</td>
                          <td className="px-4 py-3 flex space-x-2">
                            <a
                              href={`/server/${server.name}`}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              View Server
                            </a>
                            <button
                              onClick={() => handleDeleteServer(server.hostname)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <Trash2 className="h-5 w-5" />
                            </button>
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
      </section>
    </div>
  );
};

export default ServerPage;
