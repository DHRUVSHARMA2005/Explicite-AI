import { useEffect, useState } from "react"
import { useNav } from "../App"
import SeverityBadge from "../components/SeverityBadge"
import { apiGetIssues, type ApiIssueSummary, ApiError } from "../lib/api"

const SEVERITY_ORDER: Record<string, number> = { Critical: 0, High: 1, Medium: 2, Low: 3 }

function sortIssues(items: ApiIssueSummary[], sortBy: string): ApiIssueSummary[] {
  const copy = [...items]
  if (sortBy === "Severity (highest first)") {
    copy.sort((a, b) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9))
  } else if (sortBy === "Date detected") {
    copy.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  } else if (sortBy === "File name") {
    copy.sort((a, b) => (a.file ?? "").localeCompare(b.file ?? ""))
  }
  return copy
}

function statusStyle(s: string): { color: string; bg: string } {
  if (s === "Open") return { color: "var(--xm-tx-secondary)", bg: "var(--xm-bg-elevated)" }
  if (s === "In Review") return { color: "var(--xm-info)", bg: "var(--xm-info-sub)" }
  if (s === "Resolved") return { color: "var(--xm-ok)", bg: "var(--xm-ok-sub)" }
  return { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)" }
}

function riskColor(risk: string): string {
  if (risk === "High") return "var(--xm-err)"
  if (risk === "Medium") return "var(--xm-medium)"
  return "var(--xm-tx-muted)"
}

function accentLeft(severity: string): string {
  if (severity === "Critical") return "var(--xm-critical)"
  if (severity === "High") return "var(--xm-high)"
  if (severity === "Medium") return "var(--xm-medium)"
  return "var(--xm-border)"
}

export default function Issues() {
  const { token, selectedProjectId, openIssue, navigate, logout, preferences } = useNav()
  const [severity, setSeverity] = useState("All")
  const [type, setType] = useState("All")
  const [status, setStatus] = useState("All")
  const [search, setSearch] = useState("")
  const [sortBy, setSortBy] = useState(preferences.default_issue_sort)
  const [issues, setIssues] = useState<ApiIssueSummary[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => { setSortBy(preferences.default_issue_sort) }, [preferences.default_issue_sort])

  useEffect(() => {
    if (!token) { logout(); return }
    if (!selectedProjectId) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    apiGetIssues(token, selectedProjectId, { severity, type, status, q: search })
      .then(res => {
        if (cancelled) return
        setIssues(res.items)
        setTotal(res.total)
        setLoading(false)
      })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load issues")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [token, selectedProjectId, severity, type, status, search])

  if (!selectedProjectId) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <div
          className="max-w-sm text-center px-8 py-12 rounded-xl"
          style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
        >
          <div className="text-sm mb-4" style={{ color: "var(--xm-tx-muted)" }}>
            Select a project from the{" "}
            <button
              onClick={() => navigate("projects")}
              className="underline"
              style={{ color: "var(--xm-accent)" }}
            >
              Projects
            </button>{" "}
            page.
          </div>
        </div>
      </div>
    )
  }

  const sorted = sortIssues(issues, sortBy)
  const criticalCount = issues.filter(i => i.severity === "Critical").length
  const highCount = issues.filter(i => i.severity === "High").length

  return (
    <div className="p-6 max-w-full">
      <div className="flex items-start justify-between mb-5">
        <div>
          <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>Findings</h2>
          <p className="text-sm mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
            {loading ? "Loading…" : `${total} issue${total !== 1 ? "s" : ""} · sorted by ${sortBy.toLowerCase()}`}
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 text-sm rounded-lg px-4 py-3" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          {error}
        </div>
      )}

      {!loading && !error && (criticalCount > 0 || highCount > 0) && (
        <div
          className="flex items-center gap-3 mb-4 px-4 py-2.5 rounded-lg flex-wrap"
          style={{ backgroundColor: "var(--xm-err-sub)", border: "1px solid color-mix(in srgb, var(--xm-err) 30%, transparent)" }}
        >
          <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--xm-err)" }}>Fix first:</span>
          {criticalCount > 0 && (
            <span className="text-xs px-2 py-0.5 rounded font-medium" style={{ backgroundColor: "var(--xm-critical-bg)", color: "var(--xm-critical)" }}>
              {criticalCount} Critical
            </span>
          )}
          {highCount > 0 && (
            <span className="text-xs px-2 py-0.5 rounded font-medium" style={{ backgroundColor: "var(--xm-high-bg)", color: "var(--xm-high)" }}>
              {highCount} High
            </span>
          )}
          <span className="text-xs" style={{ color: "var(--xm-err)" }}>
            {criticalCount + highCount} issue{criticalCount + highCount !== 1 ? "s" : ""} require immediate attention
          </span>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-2.5 mb-4 flex-wrap">
        <input
          type="text"
          placeholder="Search issues or files…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="xm-input"
          style={{ width: "15rem" }}
        />
        {[
          { value: severity, set: setSeverity, opts: ["All", "Critical", "High", "Medium", "Low"] },
          { value: type, set: setType, opts: ["All", "Vulnerability", "Bug", "Code Smell", "Security Hotspot"] },
          { value: status, set: setStatus, opts: ["All", "Open", "In Review", "Resolved"] },
        ].map((f, i) => (
          <select key={i} value={f.value} onChange={e => f.set(e.target.value)} className="xm-select">
            {f.opts.map(o => <option key={o}>{o}</option>)}
          </select>
        ))}
        <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="xm-select ml-auto">
          {["Severity (highest first)", "Date detected", "File name"].map(o => (
            <option key={o}>{o}</option>
          ))}
        </select>
      </div>

      <div
        className="rounded-lg overflow-hidden"
        style={{ border: "1px solid var(--xm-border)" }}
      >
        {loading ? (
          <div className="p-8 text-center">
            <div className="space-y-2 max-w-2xl mx-auto">
              {[...Array(5)].map((_, i) => <div key={i} className="xm-skeleton h-12 rounded" />)}
            </div>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}>
                <th className="w-1 p-0" />
                {["Severity", "Issue", "Rule", "File", "Line", "Risk", "Status", ""].map(h => (
                  <th key={h} className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--xm-tx-muted)" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map((issue, idx) => {
                const ss = statusStyle(issue.status)
                return (
                  <tr
                    key={issue.id}
                    className="cursor-pointer transition-colors"
                    style={{
                      backgroundColor: "var(--xm-bg-surface)",
                      borderBottom: idx < sorted.length - 1 ? "1px solid var(--xm-border-sub)" : "none",
                      borderLeft: `2px solid ${accentLeft(issue.severity)}`,
                    }}
                    onClick={() => openIssue(issue.id, issue)}
                    onMouseEnter={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "var(--xm-bg-hover)" }}
                    onMouseLeave={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "var(--xm-bg-surface)" }}
                  >
                    <td />
                    <td className="px-4 py-3"><SeverityBadge severity={issue.severity} /></td>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{issue.title}</div>
                      <div className="text-xs mt-0.5" style={{ color: "var(--xm-tx-muted)" }}>{issue.type}</div>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs" style={{ color: "var(--xm-tx-muted)" }}>{issue.rule ?? "—"}</td>
                    <td className="px-4 py-3 font-mono text-xs" style={{ color: "var(--xm-tx-secondary)" }}>{issue.file ?? "—"}</td>
                    <td className="px-4 py-3 text-sm" style={{ color: "var(--xm-tx-secondary)" }}>{issue.line ?? "—"}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-semibold" style={{ color: riskColor(issue.risk) }}>{issue.risk}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        style={{ color: ss.color, backgroundColor: ss.bg }}
                      >
                        {issue.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        className="text-xs transition-colors"
                        style={{ color: "var(--xm-accent)" }}
                        onClick={e => { e.stopPropagation(); openIssue(issue.id, issue) }}
                        onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent-hover)" }}
                        onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
        {!loading && !error && issues.length === 0 && (
          <div className="p-10 text-center text-sm" style={{ color: "var(--xm-tx-muted)", backgroundColor: "var(--xm-bg-surface)" }}>
            No issues match the current filters.
          </div>
        )}
      </div>
    </div>
  )
}
