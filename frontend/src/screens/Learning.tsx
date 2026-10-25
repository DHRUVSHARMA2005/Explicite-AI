import { useEffect, useState } from "react"
import { useNav } from "../App"
import SeverityBadge from "../components/SeverityBadge"
import { BookIcon, CheckIcon } from "../components/Icons"
import {
  apiGetLearningResources,
  apiGetLearningPaths,
  apiGetLearningProgress,
  apiCompleteResource,
  apiGetIssueResources,
  ApiError,
  type ApiLearningResource,
  type ApiLearningPath,
  type ApiLearningProgress,
  type ApiResourceRecommendation,
} from "../lib/api"

function formatStudyTime(minutes: number): string {
  if (minutes < 60) return `${minutes}min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}h ${m}min` : `${h}h`
}

function tagColor(tag: string | null | undefined): { color: string; bg: string } {
  if (tag === "Security") return { color: "var(--xm-err)", bg: "var(--xm-err-sub)" }
  if (tag === "Quality")  return { color: "var(--xm-info)", bg: "var(--xm-info-sub)" }
  return { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)" }
}

export default function Learning() {
  const { token, selectedProjectId, selectedIssueId, selectedIssueSummary, navigate, logout, openTutor } = useNav()
  const [resources, setResources] = useState<ApiLearningResource[]>([])
  const [paths, setPaths] = useState<ApiLearningPath[]>([])
  const [progress, setProgress] = useState<ApiLearningProgress | null>(null)
  const [issueRecs, setIssueRecs] = useState<ApiResourceRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set())
  const [completing, setCompleting] = useState<string | null>(null)
  const [completeError, setCompleteError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) { logout(); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    setIssueRecs([])
    const issueFilters = selectedIssueSummary
      ? { issueType: selectedIssueSummary.type, ruleKey: selectedIssueSummary.rule ?? undefined }
      : {}
    const recsFetch =
      selectedProjectId && selectedIssueId
        ? apiGetIssueResources(token, selectedProjectId, selectedIssueId)
        : Promise.resolve([] as ApiResourceRecommendation[])

    Promise.all([
      apiGetLearningResources(token, issueFilters),
      apiGetLearningPaths(token),
      apiGetLearningProgress(token),
      recsFetch,
    ])
      .then(([res, p, prog, recs]) => {
        if (cancelled) return
        setResources(res)
        setPaths(p)
        setProgress(prog)
        setCompletedIds(new Set(prog.completed_resource_ids ?? []))
        setIssueRecs(recs)
        setLoading(false)
      })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load learning resources")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [token, selectedIssueSummary?.id, selectedProjectId])

  async function markComplete(resourceId: string) {
    if (!token) { logout(); return }
    if (completing) return
    setCompleting(resourceId)
    setCompleteError(null)
    try {
      await apiCompleteResource(token, resourceId)
      setCompletedIds(prev => new Set([...prev, resourceId]))
      const updated = await apiGetLearningProgress(token)
      setProgress(updated)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      setCompleteError(err instanceof Error ? err.message : "Failed to mark complete")
    } finally { setCompleting(null) }
  }

  const contextResources: (ApiResourceRecommendation | ApiLearningResource)[] =
    issueRecs.length > 0
      ? issueRecs
      : selectedIssueSummary
        ? resources.filter(r => r.related_rule_key === (selectedIssueSummary.rule ?? null) || r.related_issue_type === selectedIssueSummary.type)
        : []

  const contextIds = new Set(contextResources.map(r => r.id))
  const generalResources = selectedIssueSummary ? resources.filter(r => !contextIds.has(r.id)) : resources

  function ResourceRow({ r, rank }: { r: ApiLearningResource | ApiResourceRecommendation; rank?: number }) {
    const done = completedIds.has(r.id)
    const matchReason = "match_reason" in r ? r.match_reason : null
    const tc = tagColor(r.tag)
    return (
      <div
        role="button"
        tabIndex={0}
        onClick={() => openTutor(r as ApiLearningResource)}
        onKeyDown={e => e.key === "Enter" && openTutor(r as ApiLearningResource)}
        className="flex items-start gap-3 p-4 cursor-pointer transition-colors"
        style={{ backgroundColor: "var(--xm-bg-surface)" }}
        onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.backgroundColor = "var(--xm-bg-hover)" }}
        onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.backgroundColor = "var(--xm-bg-surface)" }}
      >
        <div
          className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
          style={done
            ? { backgroundColor: "var(--xm-ok-sub)", color: "var(--xm-ok)" }
            : { backgroundColor: tc.bg, color: tc.color }
          }
        >
          {done ? "✓" : rank !== undefined ? rank : r.resource_type[0]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{r.title}</div>
          {r.description && <div className="text-xs mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>{r.description}</div>}
          {matchReason && <div className="text-xs mt-0.5 italic" style={{ color: "var(--xm-accent)" }}>{matchReason}</div>}
          <div className="text-xs mt-1" style={{ color: "var(--xm-tx-muted)" }}>
            {r.resource_type}{r.duration_minutes ? ` · ${r.duration_minutes} min` : ""}
            <span className="ml-1" style={{ color: "var(--xm-accent)" }}>· Start →</span>
          </div>
        </div>
        {!done ? (
          <button
            onClick={e => { e.stopPropagation(); markComplete(r.id) }}
            disabled={completing === r.id}
            className="shrink-0 text-xs px-2 py-1 rounded transition-colors"
            style={{ color: "var(--xm-tx-muted)", border: "1px solid var(--xm-border)" }}
            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-ok)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-ok)" }}
            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)" }}
          >
            {completing === r.id ? "…" : "Mark complete"}
          </button>
        ) : (
          <span className="shrink-0 text-xs font-medium" style={{ color: "var(--xm-ok)" }}>Completed</span>
        )}
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-5">
        <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>Learning & Recommendations</h2>
        <p className="text-sm mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
          Resources recommended based on detected issues in {selectedProjectId ? "this project" : "your projects"}
        </p>
      </div>

      {error && (
        <div className="mb-4 text-sm rounded-lg px-4 py-3" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          {error}
        </div>
      )}
      {completeError && (
        <div className="mb-4 text-sm rounded-lg px-4 py-3" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          Could not save completion: {completeError}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => <div key={i} className="xm-skeleton h-16 rounded-lg" />)}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-5">
          <div className="col-span-2 space-y-5">

            {/* Issue-specific recommendations */}
            {selectedIssueSummary && contextResources.length > 0 && (
              <div
                className="rounded-lg overflow-hidden"
                style={{ border: "1px solid var(--xm-border)" }}
              >
                <div
                  className="px-4 py-3 flex items-center justify-between"
                  style={{ backgroundColor: "var(--xm-bg-elevated)", borderBottom: "1px solid var(--xm-border)" }}
                >
                  <div>
                    <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Recommended for Current Issue</h3>
                    <p className="text-xs mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
                      {selectedIssueSummary.title} ·{" "}
                      <button onClick={() => navigate("issue-detail")} className="underline" style={{ color: "var(--xm-accent)" }}>View issue →</button>
                    </p>
                  </div>
                  <SeverityBadge severity={selectedIssueSummary.severity} />
                </div>
                <div className="divide-y" style={{ borderColor: "var(--xm-border-sub)" }}>
                  {contextResources.map((r, i) => <ResourceRow key={r.id} r={r} rank={i + 1} />)}
                </div>
              </div>
            )}

            {/* General resources */}
            {generalResources.length > 0 && (
              <div>
                <div className="xm-section-label mb-3">
                  {selectedIssueSummary && contextResources.length > 0 ? "General Recommended Learning" : "Learning Resources"}
                </div>
                <div
                  className="rounded-lg overflow-hidden"
                  style={{ border: "1px solid var(--xm-border)" }}
                >
                  <div className="divide-y" style={{ borderColor: "var(--xm-border-sub)" }}>
                    {generalResources.map(r => <ResourceRow key={r.id} r={r} />)}
                  </div>
                </div>
              </div>
            )}

            {/* Learning paths */}
            {paths.length > 0 && (
              <div>
                <div className="xm-section-label mb-3">Learning Paths</div>
                <div className="space-y-2">
                  {paths.map(p => (
                    <div
                      key={p.id}
                      className="rounded-lg p-4 transition-colors"
                      style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
                      onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-accent-border)" }}
                      onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-border)" }}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{p.name}</div>
                        <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                          {p.module_count} modules · {Math.round(p.progress_pct * 100)}% complete
                        </span>
                      </div>
                      {p.description && <p className="text-xs mb-2" style={{ color: "var(--xm-tx-secondary)" }}>{p.description}</p>}
                      <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: "var(--xm-bg-elevated)" }}>
                        <div className="h-full rounded-full" style={{ width: `${Math.round(p.progress_pct * 100)}%`, backgroundColor: "var(--xm-accent)" }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!loading && resources.length === 0 && paths.length === 0 && (
              <div className="text-center py-12 text-sm" style={{ color: "var(--xm-tx-muted)" }}>No learning resources available.</div>
            )}
          </div>

          {/* Right sidebar */}
          <div className="space-y-4">
            <div
              className="rounded-lg p-4"
              style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
            >
              <div className="xm-section-label mb-3">Learning Progress</div>
              {progress ? (
                <div className="space-y-2.5">
                  {([
                    ["Articles read", `${progress.resources_completed} / ${progress.resources_total}`],
                    ["Tutorials completed", `${progress.tutorials_completed} / ${progress.tutorials_total}`],
                    ["Paths started", String(progress.paths_started)],
                    ["Total study time", progress.total_study_minutes > 0 ? formatStudyTime(progress.total_study_minutes) : "—"],
                  ] as [string, string][]).map(([label, value]) => (
                    <div key={label} className="flex items-center justify-between">
                      <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>{label}</span>
                      <span className="text-xs font-semibold" style={{ color: "var(--xm-tx-primary)" }}>{value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs italic" style={{ color: "var(--xm-tx-muted)" }}>Loading…</div>
              )}
            </div>

            <div
              className="rounded-lg p-4"
              style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
            >
              <div className="xm-section-label mb-2">Quick Links</div>
              <button onClick={() => navigate("issues")} className="text-xs underline" style={{ color: "var(--xm-accent)" }}>
                View all findings →
              </button>
            </div>

            {resources.length > 0 && (
              <div
                className="rounded-lg p-4"
                style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
              >
                <div className="xm-section-label mb-3">Topic Tags</div>
                <div className="flex flex-wrap gap-1.5">
                  {Array.from(new Set(resources.flatMap(r => [r.tag, r.related_issue_type]).filter(Boolean))).map(tag => {
                    const tc = tagColor(tag)
                    return (
                      <span
                        key={tag}
                        className="text-xs px-2 py-0.5 rounded font-medium"
                        style={{ color: tc.color, backgroundColor: tc.bg }}
                      >
                        {tag}
                      </span>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
