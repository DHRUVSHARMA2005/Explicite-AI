import { useEffect, useRef, useState } from "react"
import { useNav } from "../App"
import SeverityBadge from "../components/SeverityBadge"
import { CheckIcon, XIcon, ClockIcon, AnalyzeIcon, IssuesIcon, ChatIcon, BookIcon, UploadIcon } from "../components/Icons"
import {
  apiGetDashboard,
  apiSubmitAnalysis,
  apiGetAnalysisJob,
  type ApiDashboard,
  type ApiIssueSummary,
  type ApiAnalysisJob,
  ApiError,
} from "../lib/api"

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatAnalysisDate(iso: string | null): string {
  if (!iso) return "Never"
  try {
    return new Date(iso).toLocaleString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
  } catch { return iso }
}

// ── Metric card ───────────────────────────────────────────────────────────────

function MetricCard({ label, value, accent, sub }: {
  label: string
  value: string | number
  accent: string
  sub?: string
}) {
  return (
    <div
      className="rounded-lg p-4 flex flex-col gap-1"
      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
    >
      <div className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--xm-tx-muted)" }}>
        {label}
      </div>
      <div className="text-2xl font-bold" style={{ color: accent }}>
        {value}
      </div>
      {sub && (
        <div className="text-[11px]" style={{ color: "var(--xm-tx-muted)" }}>{sub}</div>
      )}
    </div>
  )
}

// ── Risk score card ───────────────────────────────────────────────────────────

function RiskCard({ score, version, openFindings }: { score: number | null; version: string | null; openFindings: number }) {
  if (score === null) {
    return (
      <div
        className="rounded-lg p-4 flex flex-col gap-1"
        style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
      >
        <div className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--xm-tx-muted)" }}>
          Project Risk Score
        </div>
        <div className="text-2xl font-bold" style={{ color: "var(--xm-tx-muted)" }}>—</div>
        <div className="text-[11px]" style={{ color: "var(--xm-tx-muted)" }}>No analysis yet</div>
      </div>
    )
  }

  const band =
    score >= 75 ? { label: "Critical Risk", color: "var(--xm-critical)", bar: "var(--xm-critical)" } :
    score >= 50 ? { label: "High Risk",     color: "var(--xm-high)",     bar: "var(--xm-high)" } :
    score >= 25 ? { label: "Moderate Risk", color: "var(--xm-medium)",   bar: "var(--xm-medium)" } :
                  { label: "Low Risk",      color: "var(--xm-ok)",       bar: "var(--xm-ok)" }

  return (
    <div
      className="rounded-lg p-4 flex flex-col gap-2"
      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
    >
      <div className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--xm-tx-muted)" }}>
        Project Risk Score
      </div>
      <div className="text-2xl font-bold" style={{ color: band.color }}>
        {score.toFixed(1)}
        <span className="text-sm font-normal ml-1" style={{ color: "var(--xm-tx-muted)" }}>/ 100</span>
      </div>
      <div
        className="h-1.5 rounded-full overflow-hidden"
        style={{ backgroundColor: "var(--xm-bg-elevated)" }}
      >
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${score}%`, backgroundColor: band.color }}
        />
      </div>
      <div className="text-[11px]" style={{ color: "var(--xm-tx-muted)" }}>
        {band.label} · {openFindings} unresolved{version ? ` · model ${version}` : ""}
      </div>
    </div>
  )
}

// ── Supporting metric card ────────────────────────────────────────────────────

function SupportCard({ label, value, sub, unavailable }: {
  label: string
  value: string
  sub?: string
  unavailable?: boolean
}) {
  return (
    <div
      className="rounded-lg px-4 py-3"
      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
    >
      <div className="text-[11px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--xm-tx-muted)" }}>
        {label}
      </div>
      <div
        className="text-base font-semibold"
        style={{ color: unavailable ? "var(--xm-tx-muted)" : "var(--xm-tx-primary)" }}
      >
        {value}
      </div>
      {sub && (
        <div className="text-[11px] mt-0.5 leading-relaxed" style={{ color: "var(--xm-tx-muted)" }}>{sub}</div>
      )}
    </div>
  )
}

// ── Analysis modal ────────────────────────────────────────────────────────────

function AnalysisModal({ onClose, onSubmit }: { onClose: () => void; onSubmit: (file: File) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-md mx-4 rounded-xl shadow-2xl"
        style={{ backgroundColor: "var(--xm-bg-elevated)", border: "1px solid var(--xm-border)" }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--xm-border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Run Analysis</h3>
          <button onClick={onClose} className="text-lg leading-none" style={{ color: "var(--xm-tx-muted)" }}>×</button>
        </div>
        <div className="p-5 space-y-4">
          <p className="text-sm" style={{ color: "var(--xm-tx-secondary)" }}>
            Upload a ZIP archive of your source files (max 10 MB). Supported: <span className="xm-mono">.py .java .js .ts .jsx .tsx</span>
          </p>
          <div
            className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors"
            style={{ borderColor: "var(--xm-border)" }}
            onClick={() => inputRef.current?.click()}
            onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-accent)"; (e.currentTarget as HTMLDivElement).style.backgroundColor = "var(--xm-accent-subtle)" }}
            onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-border)"; (e.currentTarget as HTMLDivElement).style.backgroundColor = "transparent" }}
          >
            {file ? (
              <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>
                {file.name} <span style={{ color: "var(--xm-tx-muted)" }}>({(file.size / 1024).toFixed(0)} KB)</span>
              </div>
            ) : (
              <>
                <UploadIcon className="w-8 h-8 mx-auto mb-2" style={{ color: "var(--xm-tx-muted)" } as React.CSSProperties} />
                <div className="text-sm" style={{ color: "var(--xm-tx-muted)" }}>Click to select a ZIP file</div>
                <div className="text-xs mt-1" style={{ color: "var(--xm-tx-muted)" }}>or drag and drop</div>
              </>
            )}
          </div>
          <input ref={inputRef} type="file" accept=".zip,application/zip" className="hidden" onChange={e => setFile(e.target.files?.[0] ?? null)} />
          <div className="flex gap-3 justify-end">
            <button onClick={onClose} className="xm-btn xm-btn-secondary">Cancel</button>
            <button
              disabled={!file}
              onClick={() => file && onSubmit(file)}
              className="xm-btn xm-btn-primary"
            >
              Start Analysis
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Job status banner ─────────────────────────────────────────────────────────

function JobBanner({ job, onDismiss }: { job: ApiAnalysisJob; onDismiss: () => void }) {
  const isTerminal = job.status === "completed" || job.status === "failed"
  const bg   = job.status === "completed" ? "var(--xm-ok-sub)"   : job.status === "failed" ? "var(--xm-err-sub)" : "var(--xm-info-sub)"
  const border = job.status === "completed" ? "var(--xm-ok)"     : job.status === "failed" ? "var(--xm-err)"     : "var(--xm-info)"
  const text   = job.status === "completed" ? "var(--xm-ok)"     : job.status === "failed" ? "var(--xm-err)"     : "var(--xm-info)"

  const label =
    job.status === "queued"    ? "Analysis queued…" :
    job.status === "running"   ? "Analysis running…" :
    job.status === "completed" ? `Analysis complete — ${job.findings_count ?? 0} finding${job.findings_count !== 1 ? "s" : ""}` :
                                 `Analysis failed: ${job.failure_reason ?? "unknown error"}`
  return (
    <div
      className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm mb-4"
      style={{ backgroundColor: bg, border: `1px solid color-mix(in srgb, ${border} 40%, transparent)`, color: text }}
    >
      {!isTerminal && (
        <svg className="xm-spin w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" aria-hidden>
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      )}
      <span className="flex-1">{label}</span>
      {isTerminal && (
        <button onClick={onDismiss} className="text-xs underline opacity-70 hover:opacity-100">Dismiss</button>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function Dashboard() {
  const { token, selectedProjectId, navigate, openIssue, logout } = useNav()
  const [data, setData] = useState<ApiDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [currentJob, setCurrentJob] = useState<ApiAnalysisJob | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) { logout(); return }
    if (!selectedProjectId) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    apiGetDashboard(token, selectedProjectId)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load dashboard")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [token, selectedProjectId])

  useEffect(() => {
    if (!currentJob || !token || !selectedProjectId) return
    if (currentJob.status === "completed" || currentJob.status === "failed") return
    let cancelled = false
    const interval = setInterval(() => {
      apiGetAnalysisJob(token, selectedProjectId, currentJob.id)
        .then(updated => {
          if (cancelled) return
          setCurrentJob(updated)
          if (updated.status === "completed") {
            apiGetDashboard(token, selectedProjectId)
              .then(d => { if (!cancelled) setData(d) })
              .catch(() => {})
          }
        })
        .catch(() => {})
    }, 2000)
    return () => { cancelled = true; clearInterval(interval) }
  }, [currentJob?.id, currentJob?.status, token, selectedProjectId])

  async function handleSubmit(file: File) {
    if (!token || !selectedProjectId) return
    setShowModal(false)
    setSubmitError(null)
    try {
      const job = await apiSubmitAnalysis(token, selectedProjectId, file)
      setCurrentJob(job)
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Failed to start analysis")
    }
  }

  function handleIssueClick(issue: ApiIssueSummary) { openIssue(issue.id, issue) }

  if (!selectedProjectId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <FolderEmptyState navigate={navigate} />
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="grid grid-cols-4 gap-4 mb-4">
          {[...Array(4)].map((_, i) => <div key={i} className="xm-skeleton h-24 rounded-lg" />)}
        </div>
        <div className="xm-skeleton h-48 rounded-lg mb-4" />
        <div className="xm-skeleton h-64 rounded-lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div
          className="text-sm rounded-lg px-4 py-3"
          style={{ backgroundColor: "var(--xm-err-sub)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)", color: "var(--xm-err)" }}
        >
          {error}
        </div>
      </div>
    )
  }

  if (!data) return null

  const { metrics: m, supporting_metrics: sm, quality_gate: qg } = data
  const vulnSub = m.critical_vulnerabilities > 0 || m.high_vulnerabilities > 0
    ? `${m.critical_vulnerabilities} critical · ${m.high_vulnerabilities} high`
    : undefined
  const jobRunning = currentJob && currentJob.status !== "completed" && currentJob.status !== "failed"

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {showModal && <AnalysisModal onClose={() => setShowModal(false)} onSubmit={handleSubmit} />}

      {/* Page header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>
            Code Intelligence
          </h2>
          <p className="text-sm mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
            {data.project_name}
            {data.last_analysis_at && (
              <span style={{ color: "var(--xm-tx-muted)" }}>
                {" "}· Last analysis {formatAnalysisDate(data.last_analysis_at)}
              </span>
            )}
          </p>
        </div>
        <button
          disabled={!!jobRunning}
          onClick={() => setShowModal(true)}
          className="xm-btn xm-btn-primary"
        >
          <AnalyzeIcon className="w-4 h-4" />
          {jobRunning ? "Analysing…" : "Run Analysis"}
        </button>
      </div>

      {submitError && (
        <div
          className="text-sm rounded-lg px-4 py-2.5 mb-4 flex items-center justify-between"
          style={{ backgroundColor: "var(--xm-err-sub)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)", color: "var(--xm-err)" }}
        >
          <span>{submitError}</span>
          <button onClick={() => setSubmitError(null)} className="text-xs underline ml-3">Dismiss</button>
        </div>
      )}
      {currentJob && <JobBanner job={currentJob} onDismiss={() => setCurrentJob(null)} />}

      {/* Quality gate strip */}
      <div
        className="rounded-lg px-5 py-4 mb-5 flex items-center gap-5 flex-wrap"
        style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ backgroundColor: qg.passed ? "var(--xm-ok-sub)" : "var(--xm-err-sub)" }}
          >
            {qg.passed
              ? <CheckIcon className="w-4 h-4" style={{ color: "var(--xm-ok)" } as React.CSSProperties} />
              : <XIcon className="w-4 h-4" style={{ color: "var(--xm-err)" } as React.CSSProperties} />}
          </div>
          <div>
            <div className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>
              Quality Gate: <span style={{ color: qg.passed ? "var(--xm-ok)" : "var(--xm-err)" }}>
                {qg.passed ? "Passed" : "Failed"}
              </span>
            </div>
            {qg.failed_conditions.length > 0 && (
              <div className="text-xs mt-0.5" style={{ color: "var(--xm-tx-muted)" }}>
                {qg.failed_conditions.length} condition{qg.failed_conditions.length !== 1 ? "s" : ""} failed — {qg.failed_conditions.join(", ")}
              </div>
            )}
          </div>
        </div>
        <div className="ml-auto flex items-center gap-8 shrink-0">
          {[
            { label: "Branch", value: data.branch, mono: true },
            { label: "Last analysis", value: formatAnalysisDate(data.last_analysis_at), mono: false },
          ].map(({ label, value, mono }) => (
            <div key={label} className="text-right">
              <div className="text-[11px] uppercase tracking-wider mb-0.5" style={{ color: "var(--xm-tx-muted)" }}>{label}</div>
              <div
                className={`text-sm font-medium ${mono ? "font-mono" : ""}`}
                style={{ color: "var(--xm-tx-primary)" }}
              >
                {value}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key metrics */}
      <div className="xm-section-label mb-3">Key Metrics</div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
        <MetricCard
          label="Bugs"
          value={m.bugs}
          accent={m.bugs > 0 ? "var(--xm-err)" : "var(--xm-tx-secondary)"}
          sub={m.bugs_delta !== null ? `${m.bugs_delta > 0 ? "+" : ""}${m.bugs_delta} since last` : undefined}
        />
        <MetricCard
          label="Vulnerabilities"
          value={m.vulnerabilities}
          accent={m.vulnerabilities > 0 ? "var(--xm-high)" : "var(--xm-tx-secondary)"}
          sub={vulnSub}
        />
        <MetricCard
          label="Code Smells"
          value={m.code_smells}
          accent={m.code_smells > 0 ? "var(--xm-medium)" : "var(--xm-tx-secondary)"}
          sub={m.technical_debt_display ? `~${m.technical_debt_display} debt` : undefined}
        />
        <MetricCard
          label="Security Hotspots"
          value={m.security_hotspots}
          accent={m.security_hotspots > 0 ? "var(--xm-info)" : "var(--xm-tx-secondary)"}
          sub={m.security_hotspots_needing_review > 0 ? `${m.security_hotspots_needing_review} need review` : undefined}
        />
      </div>

      {/* Risk + severity breakdown */}
      <div className="grid grid-cols-4 gap-3 mb-5">
        <RiskCard score={data.risk_score} version={data.risk_score_version} openFindings={data.open_findings} />
        {Object.keys(data.findings_by_severity).length > 0 && (
          <div
            className="col-span-3 rounded-lg p-4"
            style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
          >
            <div className="xm-section-label mb-3">Findings by Severity</div>
            <div className="flex gap-3 flex-wrap">
              {(["Critical","High","Medium","Low"] as const).map(sev => {
                const count = data.findings_by_severity[sev] ?? 0
                if (count === 0) return null
                const colorVar = sev === "Critical" ? "var(--xm-critical)" : sev === "High" ? "var(--xm-high)" : sev === "Medium" ? "var(--xm-medium)" : "var(--xm-low)"
                const bgVar = sev === "Critical" ? "var(--xm-critical-bg)" : sev === "High" ? "var(--xm-high-bg)" : sev === "Medium" ? "var(--xm-medium-bg)" : "var(--xm-low-bg)"
                return (
                  <div
                    key={sev}
                    className="px-3 py-2 rounded-lg text-sm font-semibold"
                    style={{ backgroundColor: bgVar, color: colorVar }}
                  >
                    {sev} <span className="font-mono ml-1">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Priority issues */}
      <div
        className="rounded-lg overflow-hidden mb-5"
        style={{ border: "1px solid var(--xm-border)" }}
      >
        <div
          className="px-5 py-3.5 flex items-center justify-between"
          style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-surface)" }}
        >
          <div>
            <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Priority Issues</h3>
            <p className="text-[11px] mt-0.5" style={{ color: "var(--xm-tx-muted)" }}>
              Critical and High severity findings requiring attention
            </p>
          </div>
          <button
            onClick={() => navigate("issues")}
            className="text-xs font-medium transition-colors"
            style={{ color: "var(--xm-accent)" }}
            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent-hover)" }}
            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
          >
            View all →
          </button>
        </div>
        {data.priority_issues.length === 0 ? (
          <div className="px-5 py-10 text-center text-sm" style={{ backgroundColor: "var(--xm-bg-surface)", color: "var(--xm-tx-muted)" }}>
            No open critical or high severity issues.
          </div>
        ) : (
          <table className="w-full" style={{ backgroundColor: "var(--xm-bg-surface)" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--xm-border)" }}>
                {["Severity", "Issue", "File", "Line", ""].map(h => (
                  <th key={h} className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--xm-tx-muted)" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.priority_issues.map((issue, idx) => (
                <tr
                  key={issue.id}
                  className="cursor-pointer transition-colors"
                  style={{ borderBottom: idx < data.priority_issues.length - 1 ? "1px solid var(--xm-border-sub)" : "none" }}
                  onClick={() => handleIssueClick(issue)}
                  onMouseEnter={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "var(--xm-bg-hover)" }}
                  onMouseLeave={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "transparent" }}
                >
                  <td className="px-5 py-3"><SeverityBadge severity={issue.severity} /></td>
                  <td className="px-5 py-3">
                    <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{issue.title}</div>
                    <div className="text-xs mt-0.5" style={{ color: "var(--xm-tx-muted)" }}>{issue.type}</div>
                  </td>
                  <td className="px-5 py-3">
                    <span className="font-mono text-xs" style={{ color: "var(--xm-tx-secondary)" }}>{issue.file ?? "—"}</span>
                  </td>
                  <td className="px-5 py-3 text-sm" style={{ color: "var(--xm-tx-secondary)" }}>{issue.line ?? "—"}</td>
                  <td className="px-5 py-3">
                    <button
                      className="text-xs font-medium transition-colors"
                      style={{ color: "var(--xm-accent)" }}
                      onClick={e => { e.stopPropagation(); handleIssueClick(issue) }}
                      onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent-hover)" }}
                      onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                    >
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Supporting metrics */}
      <div className="xm-section-label mb-3">Supporting Metrics</div>
      <div className="grid grid-cols-3 gap-3 mb-5">
        <SupportCard
          label="Coverage"
          value={sm.coverage_pct !== null ? `${sm.coverage_pct.toFixed(1)}%` : "Not available"}
          unavailable={sm.coverage_pct === null}
          sub={sm.coverage_pct !== null
            ? sm.coverage_target_pct != null ? `Target: ${sm.coverage_target_pct}%` : undefined
            : sm.coverage_message ?? "Requires a test coverage report"}
        />
        <SupportCard
          label="Duplications"
          value={sm.duplications_pct !== null ? `${sm.duplications_pct.toFixed(1)}%` : "Not available"}
          unavailable={sm.duplications_pct === null}
          sub={sm.duplications_pct !== null ? "Source-level block detection" : sm.duplications_message ?? "No duplication data"}
        />
        <SupportCard
          label="Technical Debt"
          value={sm.technical_debt_display ?? "Not available"}
          unavailable={!sm.technical_debt_display}
          sub={sm.technical_debt_display
            ? sm.technical_debt_is_estimate ? "Estimate based on finding weights" : undefined
            : "No findings data"}
        />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-3">
        {([
          { title: "Review Findings", sub: `${m.bugs + m.vulnerabilities} open findings`, screen: "issues" as const, Icon: IssuesIcon },
          { title: "AI Assistant",    sub: "Ask about security issues",              screen: "ai-assistant" as const, Icon: ChatIcon },
          { title: "Learning",        sub: "Security & quality resources",           screen: "learning" as const, Icon: BookIcon },
        ] as const).map(a => (
          <button
            key={a.screen}
            onClick={() => navigate(a.screen)}
            className="rounded-lg p-4 text-left transition-colors"
            style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-accent-border)"
              ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-accent-subtle)"
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)"
              ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-bg-surface)"
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <a.Icon className="w-4 h-4" style={{ color: "var(--xm-accent)" } as React.CSSProperties} />
              <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{a.title}</div>
            </div>
            <div className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>{a.sub}</div>
          </button>
        ))}
      </div>
    </div>
  )
}

function FolderEmptyState({ navigate }: { navigate: (s: import("../App").Screen) => void }) {
  return (
    <div
      className="max-w-sm mx-auto px-8 py-12 rounded-xl text-center"
      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
    >
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4"
        style={{ backgroundColor: "var(--xm-accent-subtle)" }}
      >
        <AnalyzeIcon className="w-6 h-6" style={{ color: "var(--xm-accent)" } as React.CSSProperties} />
      </div>
      <h3 className="text-base font-semibold mb-2" style={{ color: "var(--xm-tx-primary)" }}>
        No project selected
      </h3>
      <p className="text-sm mb-5" style={{ color: "var(--xm-tx-muted)" }}>
        Select a project from the Projects page to view its dashboard.
      </p>
      <button onClick={() => navigate("projects")} className="xm-btn xm-btn-primary">
        Browse Projects
      </button>
    </div>
  )
}
