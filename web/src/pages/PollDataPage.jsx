import React, { useEffect, useMemo, useRef, useState } from "react";
import { Play, RefreshCw, Clock, Server, List, Activity } from "lucide-react";
import API_BASE_URL from "../config/api";


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

function StatusPill({ status }) {
  const styles = {
    PENDING: "bg-slate-100 text-slate-700",
    RUNNING: "bg-blue-100 text-blue-700",
    SUCCESS: "bg-emerald-100 text-emerald-700",
    FAILED: "bg-rose-100 text-rose-700",
    FINISHED: "bg-emerald-100 text-emerald-700",
  };
  const cls = styles[status] || "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${cls}`}>
      {status || "N/A"}
    </span>
  );
}

function formatDateTime(dt) {
  if (!dt) return "N/A";
  const d = new Date(dt);
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

async function apiJson(path, options) {
  const res = await fetch(`${API_BASE_URL}${path}`, options);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

const PollDataPage = () => {
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);

  const [activeJobId, setActiveJobId] = useState(null);
  const [jobDetail, setJobDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);

  const intervalRef = useRef(null);

  const activeJobStatus = jobDetail?.status;
  const isTerminal = useMemo(() => {
    // adjust if you have more statuses
    return ["FINISHED", "FAILED", "SUCCESS"].includes(activeJobStatus);
  }, [activeJobStatus]);

  const clearPolling = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = null;
    setIsPolling(false);
  };

  const fetchJobs = async () => {
    setJobsLoading(true);
    try {
      const data = await apiJson(`/jobs?limit=10`);
      setJobs(data || []);
    } catch (e) {
      setError(e.message || "Failed to load jobs");
    } finally {
      setJobsLoading(false);
    }
  };

  const fetchJobDetail = async (jobId) => {
    if (!jobId) return;
    setDetailLoading(true);
    try {
      const data = await apiJson(`/jobs/${jobId}`);
      setJobDetail(data);
      setLastUpdatedAt(new Date().toISOString());
      setError(null);
      return data;
    } catch (e) {
      setError(e.message || "Failed to load job detail");
    } finally {
      setDetailLoading(false);
    }
  };

  const startPollingJob = async (jobId) => {
    if (!jobId) return;

    // stop any previous polling
    clearPolling();
    setActiveJobId(jobId);

    // initial fetch
    const first = await fetchJobDetail(jobId);
    // keep jobs list fresh (optional)
    fetchJobs();

    // if it already ended, don't start interval
    const status = first?.status;
    const ended = ["FINISHED", "FAILED", "SUCCESS"].includes(status);
    if (ended) {
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    intervalRef.current = setInterval(async () => {
      // guard: if user switched job while interval is running
      setIsPolling(true);
      await fetchJobDetail(jobId);
      fetchJobs();
    }, 2000);
  };

  const handleRunPoll = async () => {
    setError(null);
    try {
      // You can pass ?max_parallel_servers=3 if you want:
      // const data = await apiJson(`/jobs/run?max_parallel_servers=3`, { method: "POST" });
      const data = await apiJson(`/jobs/run`, { method: "POST" });
      const newJobId = data?.job_id;
      if (!newJobId) throw new Error("Backend did not return job_id");
      await startPollingJob(newJobId);
    } catch (e) {
      setError(e.message || "Failed to run poll");
    }
  };

  const handleSelectJob = async (jobId) => {
    setError(null);
    await startPollingJob(jobId);
  };

  const handleRefreshNow = async () => {
    setError(null);
    await fetchJobs();
    if (activeJobId) await fetchJobDetail(activeJobId);
  };

  useEffect(() => {
    fetchJobs();
    return () => {
      clearPolling();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If the active job becomes terminal while polling, stop automatically
  useEffect(() => {
    if (isPolling && isTerminal) {
      clearPolling();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isTerminal]);

  return (
    <div className="space-y-6">
      {/* Runner */}
      <SectionCard
        title="Poll runner"
        right={
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefreshNow}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-900 hover:bg-slate-50"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>

            <button
              onClick={handleRunPoll}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-800"
            >
              <Play className="h-4 w-4" />
              Run Poll
            </button>
          </div>
        }
      >
        <div className="grid grid-cols-4 gap-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold">
              <Activity className="h-4 w-4" />
              Polling
            </div>
            <div className="mt-2 text-lg font-semibold text-slate-900">
              {isPolling ? "ON" : "OFF"}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold">
              <List className="h-4 w-4" />
              Active Job
            </div>
            <div className="mt-2 text-sm font-semibold text-slate-900 break-all">
              {activeJobId || "None"}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold">
              <Server className="h-4 w-4" />
              Status
            </div>
            <div className="mt-2">
              <StatusPill status={jobDetail?.status} />
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2 text-slate-600 text-xs font-semibold">
              <Clock className="h-4 w-4" />
              Last Updated
            </div>
            <div className="mt-2 text-sm font-semibold text-slate-900">
              {lastUpdatedAt ? formatDateTime(lastUpdatedAt) : "N/A"}
            </div>
          </div>
        </div>

        {error ? (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        {jobDetail ? (
          <div className="mt-4 grid grid-cols-4 gap-4">
            <div className="col-span-2 rounded-2xl border border-slate-200 bg-white p-4">
              <div className="text-xs font-semibold text-slate-600">Job Name</div>
              <div className="mt-1 text-sm font-semibold text-slate-900">{jobDetail.name}</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="text-xs font-semibold text-slate-600">Created</div>
              <div className="mt-1 text-sm font-semibold text-slate-900">{formatDateTime(jobDetail.created_at)}</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="text-xs font-semibold text-slate-600">Started / Finished</div>
              <div className="mt-1 text-xs font-semibold text-slate-900">
                {formatDateTime(jobDetail.started_at)} <span className="text-slate-500">→</span>{" "}
                {formatDateTime(jobDetail.finished_at)}
              </div>
            </div>
          </div>
        ) : null}
      </SectionCard>

      {/* Jobs list */}
      <SectionCard title="Jobs history">
        <div className="overflow-hidden rounded-xl border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr className="[&>th]:px-4 [&>th]:py-3 [&>th]:text-left [&>th]:font-semibold">
                  <th>Name</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Started</th>
                  <th>Finished</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {jobsLoading ? (
                  <tr>
                    <td colSpan="6" className="py-10 text-center">
                      <p className="text-sm text-slate-500">Loading jobs…</p>
                    </td>
                  </tr>
                ) : jobs?.length ? (
                  jobs.map((j) => {
                    const selected = j.job_id === activeJobId;
                    return (
                      <tr
                        key={j.job_id}
                        className={`transition-colors hover:bg-slate-50 ${selected ? "bg-slate-50" : ""}`}
                      >
                        <td className="px-4 py-3 font-medium text-slate-900">{j.name}</td>
                        <td className="px-4 py-3">
                          <StatusPill status={j.status} />
                        </td>
                        <td className="px-4 py-3 text-slate-600 tabular-nums">{formatDateTime(j.created_at)}</td>
                        <td className="px-4 py-3 text-slate-600 tabular-nums">{formatDateTime(j.started_at)}</td>
                        <td className="px-4 py-3 text-slate-600 tabular-nums">{formatDateTime(j.finished_at)}</td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleSelectJob(j.job_id)}
                            className="text-indigo-600 hover:text-indigo-900 font-semibold"
                          >
                            View / Poll
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="6" className="py-10 text-center">
                      <p className="text-sm text-slate-500">No jobs yet.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </SectionCard>

      {/* Logs */}
      <SectionCard
        title="Server logs"
        right={
          activeJobId ? (
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">
                {detailLoading ? "Updating…" : isPolling ? "Live" : "Idle"}
              </span>
              <StatusPill status={jobDetail?.status} />
            </div>
          ) : null
        }
      >
        {!activeJobId ? (
          <p className="text-sm text-slate-500">Run a poll or select a job to view logs.</p>
        ) : !jobDetail ? (
          <p className="text-sm text-slate-500">Loading job details…</p>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {(jobDetail.servers || []).map((s) => (
              <div
                key={s.server_id}
                className="rounded-2xl border border-slate-200 bg-white shadow-sm"
              >
                <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{s.server_name}</div>
                    <div className="mt-1 text-xs text-slate-500 tabular-nums">
                      {formatDateTime(s.started_at)} <span className="text-slate-400">→</span>{" "}
                      {formatDateTime(s.finished_at)}
                    </div>
                  </div>
                  <StatusPill status={s.status} />
                </div>

                <div className="p-4">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words text-xs text-slate-800 font-mono leading-relaxed">
                      {s.log_text || "Waiting for logs…"}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  );
};

export default PollDataPage;
