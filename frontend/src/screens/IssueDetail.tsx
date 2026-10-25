import { useEffect, useState } from "react"
import { useNav } from "../App"
import SeverityBadge from "../components/SeverityBadge"
import { SparkleIcon, ChatIcon } from "../components/Icons"
import {
  apiGetIssueDetail,
  apiUpdateIssueStatus,
  apiExplainIssue,
  apiGenerateFix,
  apiGetSourceExcerpt,
  type ApiIssueDetail,
  type ApiExplainResponse,
  type ApiSourceExcerpt,
  ApiError,
} from "../lib/api"

const VALID_STATUSES = ["Open", "In Review", "Resolved"] as const

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
  } catch { return iso }
}

function SectionCard({ title, children, rightSlot }: { title: string; children: React.ReactNode; rightSlot?: React.ReactNode }) {
  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
    >
      <div
        className="px-4 py-2.5 flex items-center justify-between"
        style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}
      >
        <h3 className="text-[11px] font-semibold uppercase tracking-wider xm-section-label">{title}</h3>
        {rightSlot}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

export default function IssueDetail() {
  const { token, selectedProjectId, selectedIssueId, navigate, logout, openFix, preferences } = useNav()
  const [issue, setIssue] = useState<ApiIssueDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentStatus, setCurrentStatus] = useState<string>("Open")
  const [statusSaving, setStatusSaving] = useState(false)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [explanation, setExplanation] = useState<ApiExplainResponse | null>(null)
  const [explainLoading, setExplainLoading] = useState(false)
  const [explainError, setExplainError] = useState<string | null>(null)
  const [fixGenerating, setFixGenerating] = useState(false)
  const [fixError, setFixError] = useState<string | null>(null)
  const [sourceExcerpt, setSourceExcerpt] = useState<ApiSourceExcerpt | null>(null)
  const [sourceLoading, setSourceLoading] = useState(false)

  useEffect(() => {
    if (!token) { logout(); return }
    if (!selectedProjectId || !selectedIssueId) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setSourceLoading(true)
    setError(null)
    setSourceExcerpt(null)
    apiGetIssueDetail(token, selectedProjectId, selectedIssueId)
      .then(d => {
        if (!cancelled) {
          setIssue(d)
          setCurrentStatus(d.status)
          setLoading(false)
          apiGetSourceExcerpt(token, selectedProjectId!, selectedIssueId!)
            .then(s => { if (!cancelled) { setSourceExcerpt(s); setSourceLoading(false) } })
            .catch(() => { if (!cancelled) setSourceLoading(false) })
        }
      })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load issue")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [token, selectedProjectId, selectedIssueId])

  async function handleStatusChange(newStatus: string) {
    if (!token || !selectedProjectId || !selectedIssueId || statusSaving || newStatus === currentStatus) return
    setStatusSaving(true)
    setStatusError(null)
    try {
      const updated = await apiUpdateIssueStatus(token, selectedProjectId, selectedIssueId, newStatus)
      setCurrentStatus(updated.status)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      setStatusError(err instanceof Error ? err.message : "Failed to update status")
    } finally {
      setStatusSaving(false)
    }
  }

  async function handleExplain(force = false) {
    if (!token || !selectedProjectId || !selectedIssueId || explainLoading) return
    setExplainLoading(true)
    setExplainError(null)
    try {
      const level = preferences.ai_explain_level as "beginner" | "intermediate" | "advanced"
      const result = await apiExplainIssue(token, selectedProjectId, selectedIssueId, { force, level })
      setExplanation(result)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 503) {
        setExplainError("AI model is not configured. Ask your administrator to set up an AI provider.")
      } else if (err instanceof ApiError && err.status === 502) {
        setExplainError("The AI model returned an unreadable response. Try again later.")
      } else {
        setExplainError(err instanceof Error ? err.message : "Failed to generate explanation")
      }
    } finally {
      setExplainLoading(false)
    }
  }

  async function handleGenerateFix() {
    if (!token || !selectedProjectId || !selectedIssueId || fixGenerating) return
    setFixGenerating(true)
    setFixError(null)
    try {
      const fix = await apiGenerateFix(token, selectedProjectId, selectedIssueId)
      openFix(fix.id)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 503) {
        setFixError("AI model is not configured. Ask your administrator to set up an AI provider.")
      } else {
        setFixError(err instanceof Error ? err.message : "Failed to generate fix")
      }
    } finally {
      setFixGenerating(false)
    }
  }

  if (!selectedProjectId || !selectedIssueId) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <div className="text-sm text-center" style={{ color: "var(--xm-tx-muted)" }}>
          Select an issue from the{" "}
          <button onClick={() => navigate("issues")} className="underline" style={{ color: "var(--xm-accent)" }}>Issues</button> page.
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-4">
        {[...Array(3)].map((_, i) => <div key={i} className="xm-skeleton h-32 rounded-lg" />)}
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <div className="text-sm rounded-lg px-4 py-3" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>{error}</div>
      </div>
    )
  }

  if (!issue) return null

  const metaTag = [issue.rule, issue.cwe_id, issue.owasp_category].filter(Boolean).join(" · ")

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs mb-4" style={{ color: "var(--xm-tx-muted)" }}>
        <button
          onClick={() => navigate("issues")}
          className="transition-colors"
          style={{ color: "var(--xm-tx-secondary)" }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)" }}
        >
          Findings
        </button>
        <span>›</span>
        <span style={{ color: "var(--xm-tx-primary)" }}>{issue.title}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <SeverityBadge severity={issue.severity} size="md" />
            <span
              className="text-xs px-2 py-0.5 rounded font-medium"
              style={{
                color: issue.risk === "High" ? "var(--xm-err)" : issue.risk === "Medium" ? "var(--xm-medium)" : "var(--xm-tx-secondary)",
                backgroundColor: issue.risk === "High" ? "var(--xm-err-sub)" : issue.risk === "Medium" ? "var(--xm-medium-bg)" : "var(--xm-bg-elevated)",
              }}
            >
              {issue.risk} Risk
            </span>
            {metaTag && <span className="text-xs font-mono" style={{ color: "var(--xm-tx-muted)" }}>{metaTag}</span>}
          </div>
          <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>{issue.title}</h2>
          {(issue.file || issue.line) && (
            <p className="text-sm font-mono mt-0.5" style={{ color: "var(--xm-tx-muted)" }}>
              {issue.file ?? "Unknown file"}{issue.line ? ` · Line ${issue.line}` : ""}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button onClick={() => navigate("ai-assistant")} className="xm-btn xm-btn-secondary">
            <ChatIcon className="w-4 h-4" />
            AI Assistant
          </button>
          <button onClick={handleGenerateFix} disabled={fixGenerating} className="xm-btn xm-btn-primary">
            <SparkleIcon className="w-4 h-4" />
            {fixGenerating ? "Generating…" : "Generate Fix"}
          </button>
        </div>
      </div>

      {fixError && (
        <div className="mb-4 text-xs rounded-lg px-3 py-2.5" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          {fixError}
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        {/* Main column */}
        <div className="col-span-2 space-y-4">

          {/* Code Context */}
          <div
            className="rounded-lg overflow-hidden"
            style={{ border: "1px solid var(--xm-border)" }}
          >
            <div
              className="px-4 py-2.5 flex items-center justify-between"
              style={{ backgroundColor: "var(--xm-bg-elevated)", borderBottom: "1px solid var(--xm-border)" }}
            >
              <h3 className="text-[11px] font-semibold uppercase tracking-wider xm-section-label">Code Context</h3>
              {(sourceExcerpt?.file || issue.file) && (
                <span className="font-mono text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                  {sourceExcerpt?.file || issue.file}{issue.line ? `:${issue.line}` : ""}
                </span>
              )}
            </div>
            {sourceLoading ? (
              <div className="code-block py-8 text-center text-xs" style={{ color: "var(--xm-tx-muted)" }}>Loading source…</div>
            ) : sourceExcerpt?.available && sourceExcerpt.lines.length > 0 ? (
              <div className="code-block leading-relaxed overflow-x-auto">
                {sourceExcerpt.lines.map(ln => (
                  <div key={ln.number} className={ln.is_target ? "code-line-remove" : ""}>
                    <span className="select-none pr-3 text-right inline-block w-10" style={{ color: ln.is_target ? "var(--xm-err)" : "#484f58" }}>
                      {ln.number}
                    </span>
                    <span style={ln.is_target ? { backgroundColor: "#3d1a1a", display: "inline-block", width: "calc(100% - 3rem)", color: "#ff7b72" } : {}}>
                      {ln.content || " "}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="code-block py-8 text-center text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                {sourceExcerpt?.message || `Source preview not available — open in your IDE at ${issue.file ?? "the location above"}${issue.line ? `:${issue.line}` : ""}`}
              </div>
            )}
          </div>

          {/* Risk Analysis */}
          <SectionCard title="Risk Analysis" rightSlot={
            <span
              className="text-xs px-1.5 py-0.5 rounded font-medium"
              style={{
                color: issue.risk === "High" ? "var(--xm-err)" : issue.risk === "Medium" ? "var(--xm-medium)" : "var(--xm-tx-secondary)",
                backgroundColor: issue.risk === "High" ? "var(--xm-err-sub)" : issue.risk === "Medium" ? "var(--xm-medium-bg)" : "var(--xm-bg-elevated)",
              }}
            >
              {issue.risk} Risk
            </span>
          }>
            <div className="grid grid-cols-4 gap-4 mb-3">
              {[
                { label: "Severity", value: issue.severity, color: issue.severity === "Critical" || issue.severity === "High" ? "var(--xm-err)" : issue.severity === "Medium" ? "var(--xm-medium)" : "var(--xm-tx-secondary)" },
                { label: "Risk Level", value: issue.risk, color: issue.risk === "High" ? "var(--xm-err)" : issue.risk === "Medium" ? "var(--xm-medium)" : "var(--xm-tx-secondary)" },
                { label: "CVSS Score", value: issue.cvss_score !== null ? `${issue.cvss_score.toFixed(1)} / 10` : "Not available", color: issue.cvss_score !== null && issue.cvss_score >= 7 ? "var(--xm-err)" : issue.cvss_score !== null && issue.cvss_score >= 4 ? "var(--xm-medium)" : "var(--xm-tx-secondary)" },
                { label: "Status", value: currentStatus, color: currentStatus === "Resolved" ? "var(--xm-ok)" : "var(--xm-tx-primary)" },
              ].map(r => (
                <div key={r.label} className="text-center">
                  <div className="text-[11px] mb-1" style={{ color: "var(--xm-tx-muted)" }}>{r.label}</div>
                  <div className="text-base font-bold" style={{ color: r.color }}>{r.value}</div>
                </div>
              ))}
            </div>
            {(issue.cvss_score !== null || issue.cvss_vector || issue.cwe_id || issue.owasp_category) && (
              <div className="flex items-center gap-4 pt-3 flex-wrap" style={{ borderTop: "1px solid var(--xm-border-sub)" }}>
                {issue.cvss_score !== null ? (
                  <div className="text-xs" style={{ color: "var(--xm-tx-secondary)" }}>
                    {issue.cvss_version && <span className="mr-1 font-mono" style={{ color: "var(--xm-tx-muted)" }}>CVSS v{issue.cvss_version}</span>}
                    <span className="font-semibold" style={{ color: issue.cvss_score >= 7 ? "var(--xm-err)" : issue.cvss_score >= 4 ? "var(--xm-medium)" : "var(--xm-tx-secondary)" }}>
                      {issue.cvss_score.toFixed(1)} / 10
                    </span>
                    {issue.cvss_severity && <span className="ml-1" style={{ color: "var(--xm-tx-muted)" }}>({issue.cvss_severity})</span>}
                  </div>
                ) : issue.cvss_vector ? (
                  <div className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                    {issue.cvss_version && <span className="mr-1 font-mono">CVSS v{issue.cvss_version}</span>}
                    <span className="italic">Score not computed for this version</span>
                  </div>
                ) : null}
                {issue.cvss_vector && <div className="text-xs font-mono break-all" style={{ color: "var(--xm-tx-muted)" }}>{issue.cvss_vector}</div>}
                {issue.cwe_id && <div className="text-xs" style={{ color: "var(--xm-tx-secondary)" }}>CWE: <span className="font-mono" style={{ color: "var(--xm-tx-primary)" }}>{issue.cwe_id}</span></div>}
                {issue.owasp_category && <div className="text-xs" style={{ color: "var(--xm-tx-secondary)" }}>OWASP: <span className="font-mono" style={{ color: "var(--xm-tx-primary)" }}>{issue.owasp_category}</span></div>}
              </div>
            )}
          </SectionCard>

          {/* Why Does It Matter */}
          <SectionCard title="Why Does it Matter?">
            {issue.description ? (
              <p className="text-sm leading-relaxed" style={{ color: "var(--xm-tx-secondary)" }}>{issue.description}</p>
            ) : (
              <p className="text-sm italic" style={{ color: "var(--xm-tx-muted)" }}>No description available.</p>
            )}
          </SectionCard>

          {/* AI Explanation */}
          <SectionCard title="AI Explanation" rightSlot={
            <div className="flex items-center gap-2">
              {explanation && (
                <span
                  className="text-xs px-1.5 py-0.5 rounded font-medium"
                  style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}
                >
                  {explanation.cached ? "Cached" : explanation.model_provider}
                </span>
              )}
              {explanation && (
                <button onClick={() => handleExplain(true)} disabled={explainLoading} className="text-xs transition-colors" style={{ color: "var(--xm-tx-muted)" }}
                  onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                  onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)" }}
                >
                  Regenerate
                </button>
              )}
              <button onClick={() => handleExplain(false)} disabled={explainLoading} className="xm-btn xm-btn-primary text-xs px-2.5 py-1">
                {explainLoading ? "Generating…" : explanation ? "Refresh" : issue.ai_explanation ? "Load" : "Explain with AI"}
              </button>
            </div>
          }>
            {explainError && (
              <div className="text-xs rounded px-3 py-2.5 mb-3" style={{ backgroundColor: "var(--xm-warn-sub)", color: "var(--xm-warn)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}>
                {explainError}
              </div>
            )}
            {explanation ? (
              <div className="space-y-3 text-sm" style={{ color: "var(--xm-tx-secondary)" }}>
                {[
                  ["What it means", explanation.what],
                  ["Why it matters", explanation.why],
                  ["How it arises", explanation.how_it_arises],
                  ["Remediation", explanation.remediation],
                ].map(([label, text]) => (
                  <div key={String(label)}>
                    <span className="text-[11px] font-semibold uppercase tracking-wider block mb-0.5 xm-section-label">{label}</span>
                    <p className="leading-relaxed">{text}</p>
                  </div>
                ))}
                {explanation.caveats && (
                  <div className="rounded px-3 py-2" style={{ backgroundColor: "var(--xm-bg-elevated)", border: "1px solid var(--xm-border)" }}>
                    <span className="text-[11px] font-semibold uppercase tracking-wider block mb-0.5 xm-section-label">Caveats</span>
                    <p className="text-xs leading-relaxed" style={{ color: "var(--xm-tx-secondary)" }}>{explanation.caveats}</p>
                  </div>
                )}
              </div>
            ) : !explainLoading && !explainError ? (
              <p className="text-sm italic" style={{ color: "var(--xm-tx-muted)" }}>
                {issue.ai_explanation
                  ? 'An explanation was previously generated. Click "Load" to view it.'
                  : 'No AI explanation yet. Click "Explain with AI" to generate one.'}
              </p>
            ) : null}
            <p className="text-xs mt-3" style={{ color: "var(--xm-tx-muted)" }}>AI-generated · Not a substitute for manual review · Verify all AI explanations</p>
          </SectionCard>
        </div>

        {/* Right sidebar */}
        <div className="space-y-4">
          <SectionCard title="Details">
            <div className="space-y-2">
              {([
                ["Type", issue.type],
                ["Rule", issue.rule ?? "—"],
                ["Detected", formatDate(issue.created_at)],
                ...(issue.cwe_id ? [["CWE", issue.cwe_id]] : []),
                ...(issue.owasp_category ? [["OWASP", issue.owasp_category]] : []),
              ] as [string, string][]).map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-2">
                  <span className="text-xs shrink-0" style={{ color: "var(--xm-tx-muted)" }}>{label}</span>
                  <span className="text-xs font-mono text-right" style={{ color: "var(--xm-tx-primary)" }}>{value}</span>
                </div>
              ))}
              <div className="flex items-center justify-between gap-2 pt-1">
                <span className="text-xs shrink-0" style={{ color: "var(--xm-tx-muted)" }}>Status</span>
                <div className="flex items-center gap-1.5">
                  {statusSaving && <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>Saving…</span>}
                  <select
                    value={currentStatus}
                    disabled={statusSaving}
                    onChange={e => handleStatusChange(e.target.value)}
                    className="xm-select text-xs px-1.5 py-0.5"
                  >
                    {VALID_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              {statusError && (
                <div className="text-xs rounded px-2 py-1 mt-1" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)" }}>
                  {statusError}
                </div>
              )}
            </div>
          </SectionCard>

          <div
            className="rounded-lg p-3"
            style={{ backgroundColor: "var(--xm-accent-subtle)", border: "1px solid var(--xm-accent-border)" }}
          >
            <h3 className="text-xs font-semibold mb-2" style={{ color: "var(--xm-accent)" }}>Next Steps</h3>
            <div className="space-y-1.5">
              {["Review the code context", "Assess the risk analysis", "Read the AI explanation", "Generate and review fix", "Re-analyse to verify"].map((step, i) => (
                <div key={step} className="flex items-center gap-2 text-xs" style={{ color: "var(--xm-tx-secondary)" }}>
                  <span
                    className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
                    style={{ backgroundColor: "var(--xm-accent-subtle)", color: "var(--xm-accent)", border: "1px solid var(--xm-accent-border)" }}
                  >
                    {i + 1}
                  </span>
                  {step}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
