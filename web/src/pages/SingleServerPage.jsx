import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom"; // For dynamic server name in URL
import { Server, Monitor, File, User } from "lucide-react"; // Importing icons from lucide-react

import API_BASE_URL from "../config/api";

const ServerPage = () => {
  const { serverName } = useParams(); // Extract server name from URL
  const [server, setServer] = useState(null);
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch server and domains data on component mount or when serverName changes
  useEffect(() => {
    const fetchServerData = async () => {
      try {
        setLoading(true);
        // Fetch the list of servers
        const serverResponse = await fetch(`${API_BASE_URL}/servers/`);
        if (!serverResponse.ok) {
          throw new Error("Failed to fetch server list");
        }
        const servers = await serverResponse.json();

        // Find the selected server by name
        const selectedServer = servers.find((s) => s.name === serverName);
        if (!selectedServer) {
          throw new Error("Server not found");
        }

        setServer(selectedServer);

        // Fetch the domains for the specific server using the server ID
        const domainResponse = await fetch(`${API_BASE_URL}/domains/server/${selectedServer.id}/`);
        if (!domainResponse.ok) {
          throw new Error("Failed to fetch server domains");
        }
        const domainsData = await domainResponse.json();
        setDomains(domainsData);

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchServerData();
  }, [serverName]);

  if (loading) {
    return <div>Loading server details...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!server) {
    return <div>Server not found.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Server Overview with Domains and Accounts in Horizontal Layout */}
      <div className="flex space-x-6">
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <Server className="mr-2" /> Server Name
          </h2>
          <p>{server.name}</p>
        </div>
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <Monitor className="mr-2" /> Hostname
          </h2>
          <p>{server.hostname}</p>
        </div>
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <File className="mr-2" /> Total Domains
          </h2>
          <p>{domains.length}</p> {/* Number of domains */}
        </div>
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <User className="mr-2" /> Total Accounts
          </h2>
          <p>{domains.reduce((total, domain) => total + domain.total_accounts, 0)}</p> {/* Sum of all domain accounts */}
        </div>
      </div>

      {/* Domains Table */}
      <SectionCard title="Server Domains">
        <div className="overflow-hidden rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr className="[&>th]:px-4 [&>th]:py-3 [&>th]:text-left [&>th]:font-semibold">
                  <th>Domain Name</th>
                  <th>Status</th>
                  <th>Total Accounts</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {domains.map((domain) => (
                  <tr key={domain.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">{domain.name}</td>
                    <td className="px-4 py-3 text-slate-600">{domain.status}</td>
                    <td className="px-4 py-3 text-slate-900">{domain.total_accounts}</td>
                    <td className="px-4 py-3">
                      <a
                        href={`/domain/${domain.name}`}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        View Domain
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </SectionCard>
    </div>
  );
};

// SectionCard component for modularity
function SectionCard({ title, children }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="px-5 py-4 border-b border-slate-200">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

export default ServerPage;
