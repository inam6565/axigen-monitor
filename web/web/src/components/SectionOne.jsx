import React from "react";
import {
  getServers,
  getDomainsByServer,
  getAccountsByDomain,
} from "../api/axigen";

// --- helpers ---
function toDateSafe(value) {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

function formatUTC(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(
    d.getUTCDate()
  )} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())} UTC`;
}

function hoursBetween(a, b) {
  return Math.abs(a.getTime() - b.getTime()) / (1000 * 60 * 60);
}

function pickId(obj) {
  return obj?.id ?? obj?.server_id ?? obj?.domain_id ?? obj?.uuid ?? obj?._id;
}

function pickSnapshot(obj) {
  return (
    obj?.snapshot_at ??
    obj?.snapshotAt ??
    obj?.last_snapshot ??
    obj?.lastSnapshot ??
    obj?.snapshot_time ??
    obj?.snapshotTime ??
    null
  );
}

export default function SectionOne() {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");
  const [stats, setStats] = React.useState({
    totalServers: 0,
    totalDomains: 0,
    totalAccounts: 0,
    lastSnapshotAt: null, // Date | null
  });

  const load = React.useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const servers = await getServers();

      const domainsByServer = await Promise.all(
        (servers ?? []).map(async (s) => {
          const serverId = pickId(s);
          if (!serverId) return [];
          const domains = await getDomainsByServer(serverId);
          return Array.isArray(domains) ? domains : [];
        })
      );

      const allDomains = domainsByServer.flat();

      const accountsByDomain = await Promise.all(
        allDomains.map(async (d) => {
          const domainId = pickId(d);
          if (!domainId) return [];
          const accounts = await getAccountsByDomain(domainId);
          return Array.isArray(accounts) ? accounts : [];
        })
      );

      const allAccounts = accountsByDomain.flat();

      // find latest snapshot across servers/domains/accounts
      const snapshotCandidates = [
        ...(servers ?? []).map((x) => toDateSafe(pickSnapshot(x))),
        ...(allDomains ?? []).map((x) => toDateSafe(pickSnapshot(x))),
        ...(allAccounts ?? []).map((x) => toDateSafe(pickSnapshot(x))),
      ].filter(Boolean);

      const lastSnapshotAt =
        snapshotCandidates.length > 0
          ? new Date(
              Math.max(...snapshotCandidates.map((d) => d.getTime()))
            )
          : null;

      setStats({
        totalServers: (servers ?? []).length,
        totalDomains: allDomains.length,
        totalAccounts: allAccounts.length,
        lastSnapshotAt,
      });
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "Failed to load stats";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const now = new Date();
  const isFresh =
    stats.lastSnapshotAt ? hoursBetween(now, stats.lastSnapshotAt) < 24 : false;

  return (
    <div className="w-full">
      {/* TOP NAVBAR */}
      <div className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-primary/20" />
            <div className="font-semibold tracking-tight">Axigen Monitor</div>
          </div>

          <div className="flex items-center gap-2">
            {/* Theme toggle placeholder (wire later) */}
            <button
              className="inline-flex items-center rounded-md border px-3 py-1.5 text-sm hover:bg-accent"
              type="button"
              title="Theme toggle (wire later)"
            >
              Theme
            </button>

            <button
              className="inline-flex items-center rounded-md border px-3 py-1.5 text-sm hover:bg-accent disabled:opacity-50"
              type="button"
              onClick={load}
              disabled={loading}
              title="Refresh stats"
            >
              {loading ? "Refreshing…" : "Refresh"}
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 1 — STATS */}
      <div className="mx-auto max-w-6xl px-4 py-6">
        {error ? (
          <div className="mb-4 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm">
            {error}
          </div>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Servers" value={stats.totalServers} loading={loading} />
          <StatCard title="Total Domains" value={stats.totalDomains} loading={loading} />
          <StatCard title="Total Accounts" value={stats.totalAccounts} loading={loading} />
          <SnapshotCard
            title="Last Snapshot"
            date={stats.lastSnapshotAt}
            fresh={isFresh}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, loading }) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="mt-2 text-2xl font-semibold">
        {loading ? <span className="opacity-60">—</span> : value}
      </div>
    </div>
  );
}

function SnapshotCard({ title, date, fresh, loading }) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">{title}</div>

        <span
          className={[
            "inline-block h-2.5 w-2.5 rounded-full",
            loading || !date ? "bg-muted" : fresh ? "bg-emerald-500" : "bg-red-500",
          ].join(" ")}
          title={loading || !date ? "Unknown" : fresh ? "Fresh (< 24h)" : "Stale (>= 24h)"}
        />
      </div>

      <div className="mt-2 text-sm">
        {loading ? (
          <span className="opacity-60">Loading…</span>
        ) : date ? (
          <span className="font-medium">{formatUTC(date)}</span>
        ) : (
          <span className="opacity-60">No snapshot found</span>
        )}
      </div>
    </div>
  );
}
