import React, { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router-dom"; // For dynamic domain and account params
import { Server, CheckCircle, User } from "lucide-react"; // Importing icons from lucide-react

import API_BASE_URL from "../config/api";

const DomainPage = () => {
  const { domain } = useParams(); // Extract domain from URL
  const { search } = useLocation(); // Get query parameters (e.g., account=email@example.com)
  const accountEmail = new URLSearchParams(search).get("account");

  const [domainData, setDomainData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch domain and account data on component mount or when domain/account changes
  useEffect(() => {
    const fetchDomainData = async () => {
      let endpoint = `${API_BASE_URL}/report/?domain=${domain}/`;

      if (accountEmail) {
        endpoint = `${API_BASE_URL}/report/?account=${accountEmail}/`;
      }

      console.log("Fetching data from endpoint:", endpoint); // Debugging line

      try {
        setLoading(true);
        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error("Failed to fetch domain data");
        }
        const domainDetails = await response.json();
        console.log("Fetched domain data:", domainDetails); // Debugging line

        // If the response contains data
        if (domainDetails) {
          setDomainData(domainDetails);
        } else {
          throw new Error("No data found for this domain or account.");
        }
      } catch (err) {
        console.error("Error fetching domain data:", err); // Debugging line
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDomainData();
  }, [domain, accountEmail]); // Re-fetch if domain or account changes

  // Debugging rendering
  if (loading) {
    return <div>Loading domain details...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!domainData) {
    return <div>Domain not found.</div>;
  }

  console.log("Domain data after fetch:", domainData); // Debugging line

  return (
    <div className="space-y-6">
      {/* Domain Overview */}
      <div className="flex space-x-6">
        {/* Domain Name Card */}
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <Server className="mr-2" /> Domain Name
          </h2>
          <p>{domainData.name}</p>
        </div>

        {/* Status Card */}
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <CheckCircle className="mr-2" /> Status
          </h2>
          <p>{domainData.status}</p>
        </div>

        {/* Total Accounts Card */}
        <div className="p-4 bg-white rounded-xl shadow-sm flex-1">
          <h2 className="text-lg font-semibold flex items-center">
            <User className="mr-2" /> Total Accounts
          </h2>
          <p>{domainData.total_accounts}</p>
        </div>
      </div>

      {/* Accounts Table */}
      <SectionCard title={`Accounts for ${domainData.name}`}>
        <div className="overflow-hidden rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr className="[&>th]:px-4 [&>th]:py-3 [&>th]:text-left [&>th]:font-semibold">
                  <th>Email</th>
                  <th>Assigned (MB/GB)</th>
                  <th>Used (MB/GB)</th>
                  <th>Free (MB/GB)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {domainData.accounts.map((account, index) => {
                  if (accountEmail && account.email !== accountEmail) return null; // Filter if specific account is searched
                  return (
                    <tr key={index} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-slate-900">{account.email}</td>
                      <td className="px-4 py-3 text-slate-600">{formatMB(account.assigned_mb)}</td>
                      <td className="px-4 py-3 text-slate-900">{formatMB(account.used_mb)}</td>
                      <td className="px-4 py-3 text-slate-600">{formatMB(account.free_mb)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </SectionCard>
    </div>
  );
};

// Helper function to format MB/GB
const formatMB = (mb) => {
  mb = mb ?? 0; // if mb is null or undefined, set it to 0
  const gb = mb / 1024;
  return gb >= 1 ? `${gb.toFixed(2)} GB` : `${mb} MB`;
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

export default DomainPage;
