import { useEffect, useState } from "react"
import { useNav } from "../App"
import { CheckIcon, XIcon } from "../components/Icons"
import {
  apiGetFix,
  apiApproveFix,
  apiRejectFix,
  apiDownloadFix,
  type ApiFixResponse,
  ApiError,
} from "../lib/api"

function FixStatusBadge({ status }: { status: string }) {
  const map: Record<string, { color: string; bg: string }> = {
    proposed: { color: "var(--xm-info)",   bg: "var(--xm-info-sub)" },
    approved: { color: "var(--xm-ok)",     bg: "var(--xm-ok-sub)" },
    rejected: { color: "var(--xm-err)",    bg: "var(--xm-err-sub)" },
    applied:  { color: "var(--xm-accent)", bg: "var(--xm-accent-subtle)" },
    stale:    { color: "var(--xm-warn)",   bg: "var(--xm-warn-sub)" },
    failed:   { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)" },
  }
  const { color, bg } = map[status] ?? { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)" }
  return (
    <span className="text-xs px-2 py-0.5 rounded font-medium capitalize" style={{ color, backgroundColor: bg }}>
      {status}
    </span>
  )
}

function DiffView({ diff }: { diff: string }) {
  if (!diff) return <p className="text-xs italic p-4" style={{ color: "var(--xm-tx-muted)" }}>No diff available.</p>
  const lines = diff.split("\n")
  return (
    <div className="code-block leading-relaxed overflow-x-auto rounded">
      {lines.map((line, i) => {
        let cls = ""
        if (line.startsWith("+++") || line.startsWith("---")) cls = "code-line-header"
        else if (line.startsWith("+")) cls = "code-line-add"
        else if (line.startsWith("-")) cls = "code-line-remove"
        else if (line.startsWith("@@")) cls = "code-line-meta"
        return (
          <div key={i} className={`px-4 py-px ${cls}`}>{line || " "}</div>
        )
      })}
    </div>
  )
}

export default function SuggestedFix() {
  const { token, selectedProjectId, selectedIssueId, selectedFixId, navigate, logout } = useNav()
  const [fix, setFix] = useState<ApiFixResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) { logout(); return }
    if (!selectedProjectId || !selectedFixId) { setLoading(false); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    apiGetFix(token, selectedProjectId, selectedFixId)
      .then(f => { if (!cancelled) { setFix(f); setLoading(false) } })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load fix")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [token, selectedProjectId, selectedFixId])

  async function handleApprove() {
    if (!token || !selectedProjectId || !fix || actionLoading) return
    setActionLoading(true)
    setActionError(null)
    try {
      setFix(await apiApproveFix(token, selectedProjectId, fix.id))
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      setActionError(err instanceof ApiError ? err.message : "Failed to approve fix")
    } finally { setActionLoading(false) }
  }

  async function handleReject() {
    if (!token || !selectedProjectId || !fix || actionLoading) return
    setActionLoading(true)
    setActionError(null)
    try {
      setFix(await apiRejectFix(token, selectedProjectId, fix.id))
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      setActionError(err instanceof ApiError ? err.message : "Failed to reject fix")
    } finally { setActionLoading(false) }
  }

  async function handleDownload() {
    if (!token || !selectedProjectId || !fix || actionLoading) return
    setActionLoading(true)
    setActionError(null)
    try {
      const blob = await apiDownloadFix(token, selectedProjectId, fix.id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `fix-${fix.id}.zip`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setFix(await apiGetFix(token, selectedProjectId, fix.id))
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 409) {
        setActionError(err.message)
        try { setFix(await apiGetFix(token, selectedProjectId, fix.id)) } catch {}
      } else {
        setActionError(err instanceof Error ? err.message : "Failed to download fix")
      }
    } finally { setActionLoading(false) }
  }

  const breadcrumb = fix?.target_file
    ? `${fix.target_file}${fix.snippet_start_line ? ` · Line ${fix.snippet_start_line}` : ""}`
    : "Suggested Fix"

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs mb-4" style={{ color: "var(--xm-tx-muted)" }}>
        <button onClick={() => navigate("issues")} className="transition-colors" style={{ color: "var(--xm-tx-secondary)" }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)" }}>
          Findings
        </button>
        {selectedIssueId && (
          <>
            <span>›</span>
            <button onClick={() => navigate("issue-detail")} className="transition-colors" style={{ color: "var(--xm-tx-secondary)" }}
              onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
              onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)" }}>
              Issue Detail
            </button>
          </>
        )}
        <span>›</span>
        <span style={{ color: "var(--xm-tx-primary)" }}>{breadcrumb}</span>
      </div>

      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>Suggested Fix</h2>
            {fix && <FixStatusBadge status={fix.status} />}
          </div>
          {fix?.model_provider && (
            <p className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>
              Generated by {fix.model_provider} · {fix.model_name}
            </p>
          )}
        </div>
      </div>

      {loading && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="xm-skeleton h-32 rounded-lg" />)}
        </div>
      )}
      {error && (
        <div className="text-sm rounded-lg px-4 py-3 mb-4" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          {error}
        </div>
      )}
      {!loading && !error && !fix && (
        <div className="text-sm text-center py-12" style={{ color: "var(--xm-tx-muted)" }}>
          No fix selected. Go to an{" "}
          <button onClick={() => navigate("issue-detail")} className="underline" style={{ color: "var(--xm-accent)" }}>issue</button>
          {" "}and click Generate Fix.
        </div>
      )}

      {fix && (
        <div className="space-y-4">
          {!fix.source_available && (
            <div className="px-4 py-3 text-sm rounded-lg" style={{ backgroundColor: "var(--xm-warn-sub)", color: "var(--xm-warn)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}>
              Source code was not available when this fix was generated. The proposal is based on finding metadata only — verify carefully before applying.
            </div>
          )}
          {fix.status === "stale" && (
            <div className="px-4 py-3 text-sm rounded-lg" style={{ backgroundColor: "var(--xm-warn-sub)", color: "var(--xm-warn)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}>
              This fix is stale — the source file changed after the fix was generated. Go back and generate a new fix.
            </div>
          )}
          {actionError && (
            <div className="px-4 py-3 text-sm rounded-lg" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
              {actionError}
            </div>
          )}

          {/* Diff */}
          <div
            className="rounded-lg overflow-hidden"
            style={{ border: "1px solid var(--xm-border)" }}
          >
            <div
              className="px-4 py-2.5 flex items-center justify-between"
              style={{ backgroundColor: "var(--xm-bg-elevated)", borderBottom: "1px solid var(--xm-border)" }}
            >
              <h3 className="text-[11px] font-semibold uppercase tracking-wider xm-section-label">
                Proposed Change{fix.snippet_start_line && fix.snippet_end_line ? ` — Lines ${fix.snippet_start_line}–${fix.snippet_end_line}` : ""}
              </h3>
              {fix.target_file && <span className="text-xs font-mono" style={{ color: "var(--xm-tx-muted)" }}>{fix.target_file}</span>}
            </div>
            {fix.unified_diff ? (
              <DiffView diff={fix.unified_diff} />
            ) : fix.proposed_snippet ? (
              <pre className="text-xs font-mono p-4 overflow-x-auto leading-relaxed code-block">
                {fix.proposed_snippet}
              </pre>
            ) : (
              <div className="p-4 text-xs italic" style={{ color: "var(--xm-tx-muted)" }}>No diff or proposed code available.</div>
            )}
          </div>

          {/* Rationale + Caveats */}
          <div className="grid grid-cols-2 gap-4">
            {[
              { title: "Rationale", text: fix.rationale ?? "No rationale provided." },
              { title: "Caveats", text: fix.caveats ?? "No caveats noted." },
            ].map(({ title, text }) => (
              <div
                key={title}
                className="rounded-lg p-4"
                style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
              >
                <h3 className="text-[11px] font-semibold uppercase tracking-wider mb-2 xm-section-label">{title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: "var(--xm-tx-secondary)" }}>{text}</p>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div
            className="rounded-lg p-4"
            style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
          >
            <h3 className="text-[11px] font-semibold uppercase tracking-wider mb-2 xm-section-label">Actions</h3>
            <p className="text-xs mb-4" style={{ color: "var(--xm-tx-muted)" }}>
              AI-generated fixes must be reviewed and explicitly approved before download. The original source files are never modified — you receive a ZIP with the patch applied.
            </p>
            <div className="flex items-center gap-3 flex-wrap">
              {fix.status === "proposed" && (
                <>
                  <button onClick={handleApprove} disabled={actionLoading} className="xm-btn flex items-center gap-1.5 px-4 py-1.5 rounded text-sm font-medium" style={{ backgroundColor: "var(--xm-ok-sub)", color: "var(--xm-ok)", border: "1px solid color-mix(in srgb, var(--xm-ok) 40%, transparent)" }}>
                    <CheckIcon className="w-4 h-4" />
                    {actionLoading ? "Saving…" : "Approve Fix"}
                  </button>
                  <button onClick={handleReject} disabled={actionLoading} className="xm-btn xm-btn-secondary flex items-center gap-1.5 px-4 py-1.5 rounded text-sm font-medium" style={{ color: "var(--xm-err)", borderColor: "color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
                    <XIcon className="w-4 h-4" />
                    Reject
                  </button>
                </>
              )}
              {fix.status === "approved" && fix.source_available && (
                <>
                  <button onClick={handleDownload} disabled={actionLoading} className="xm-btn xm-btn-primary">
                    {actionLoading ? "Preparing…" : "Download Patched ZIP"}
                  </button>
                  <button onClick={handleReject} disabled={actionLoading} className="xm-btn xm-btn-secondary">Reject</button>
                </>
              )}
              {fix.status === "approved" && !fix.source_available && (
                <p className="text-sm" style={{ color: "var(--xm-warn)" }}>
                  Source not available — ZIP download is not possible. Apply the proposed changes manually using the diff above.
                </p>
              )}
              {fix.status === "applied" && (
                <p className="text-sm font-medium" style={{ color: "var(--xm-accent)" }}>Fix applied — ZIP has been downloaded.</p>
              )}
              {fix.status === "rejected" && (
                <p className="text-sm" style={{ color: "var(--xm-tx-muted)" }}>This fix has been rejected.</p>
              )}
              {fix.status === "stale" && (
                <p className="text-sm" style={{ color: "var(--xm-warn)" }}>
                  Fix is stale. Go back to{" "}
                  <button onClick={() => navigate("issue-detail")} className="underline" style={{ color: "var(--xm-accent)" }}>the issue</button>
                  {" "}and generate a new fix.
                </p>
              )}
            </div>
          </div>

          <p className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>
            AI-generated · Not verified by automated tests · Review all proposed changes before applying
          </p>
        </div>
      )}
    </div>
  )
}
