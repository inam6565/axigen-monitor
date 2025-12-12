import { useEffect, useState } from "react";
import api from "../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/stats")
      .then(res => setStats(res.data))
      .catch(() => console.log("Error fetching stats"));
  }, []);

  if (!stats) return <p>Loading...</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Axigen Dashboard</h2>

      <ul>
        <li>Servers: {stats.servers}</li>
        <li>Domains: {stats.domains}</li>
        <li>Accounts: {stats.accounts}</li>
      </ul>
    </div>
  );
}
