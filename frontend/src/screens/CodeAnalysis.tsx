import React, { useEffect, useRef, useState } from "react"
import { useNav } from "../App"
import { UploadIcon, GitBranchIcon, ClockIcon, CheckIcon, XIcon } from "../components/Icons"
import {
  apiListAnalysisJobs,
  apiSubmitAnalysis,
  apiSubmitGitAnalysis,
  ApiError,
  type ApiAnalysisJob,
} from "../lib/api"

type Mode = "zip" | "git"

const POLL_INTERVAL_MS = 3000

function statusMeta(job: ApiAnalysisJob): { color: string; bg: string; label: string } {
  if (job.status === "completed") return { color: "var(--xm-ok)", bg: "var(--xm-ok-sub)", label: "Completed" }
  if (job.status === "failed")    return { color: "var(--xm-err)", bg: "var(--xm-err-sub)", label: "Failed" }
  if (job.status === "running")   return { color: "var(--xm-info)", bg: "var(--xm-info-sub)", label: "Running…" }
  if (job.status === "cancelled") return { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)", label: "Cancelled" }
  const label = job.repo_url ? "Queued (cloning…)" : "Queued"
  return { color: "var(--xm-medium)", bg: "var(--xm-medium-bg)", label }
}

function shortSha(sha: string | null): string {
  if (!sha || sha === "unknown") return ""
  return sha.slice(0, 7)
}

function hostOf(url: string | null): string {
  if (!url) return ""
  try { return new URL(url).hostname } catch { return url }
}

export default function CodeAnalysis() {
  const { token, selectedProjectId, selectedProjectName, navigate, logout } = useNav()

  const [mode, setMode] = useState<Mode>("zip")
  const [jobs, setJobs] = useState<ApiAnalysisJob[]>([])
  const [loadingJobs, setLoadingJobs] = useState(false)
  const [jobsError, setJobsError] = useState<string | null>(null)

  const [zipFile, setZipFile] = useState<File | null>(null)
  const [zipSubmitting, setZipSubmitting] = useState(false)
  const [zipError, setZipError] = useState<string | null>(null)
  const zipInputRef = useRef<HTMLInputElement>(null)

  const [gitUrl, setGitUrl] = useState("")
  const [gitBranch, setGitBranch] = useState("main")
  const [gitSubmitting, setGitSubmitting] = useState(false)
  const [gitError, setGitError] = useState<string | null>(null)

  const isPolling = jobs.some(j => j.status === "queued" || j.status === "running")

  useEffect(() => {
    if (!token || !selectedProjectId) return
    let cancelled = false
    setLoadingJobs(true)
    setJobsError(null)
    apiListAnalysisJobs(token, selectedProjectId)
      .then(data => { if (!cancelled) { setJobs(data); setLoadingJobs(false) } })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setJobsError(err instanceof Error ? err.message : "Failed to load jobs")
        setLoadingJobs(false)
      })
    return () => { cancelled = true }
  }, [token, selectedProjectId])

  useEffect(() => {
    if (!token || !selectedProjectId || !isPolling) return
    const id = setInterval(() => {
      apiListAnalysisJobs(token, selectedProjectId)
        .then(data => setJobs(data))
        .catch(() => {})
    }, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [token, selectedProjectId, isPolling])

  async function handleZipSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!zipFile || !token || !selectedProjectId || zipSubmitting) return
    setZipSubmitting(true)
    setZipError(null)
    try {
      const job = await apiSubmitAnalysis(token, selectedProjectId, zipFile)
      setJobs(prev => [job, ...prev])
      setZipFile(null)
      if (zipInputRef.current) zipInputRef.current.value = ""
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 413) {
        setZipError("File is too large (max 10 MB).")
      } else if (err instanceof ApiError && err.status === 403) {
        setZipError("Developer role or higher required to run analysis.")
      } else {
        setZipError(err instanceof Error ? err.message : "Upload failed.")
      }
    } finally {
      setZipSubmitting(false)
    }
  }

  async function handleGitSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!token || !selectedProjectId || gitSubmitting) return
    const trimUrl = gitUrl.trim()
    const trimBranch = gitBranch.trim() || "main"
    if (!trimUrl) { setGitError("Repository URL is required."); return }
    if (!trimUrl.startsWith("https://")) {
      setGitError("Only HTTPS repository URLs are supported.")
      return
    }
    setGitSubmitting(true)
    setGitError(null)
    try {
      const job = await apiSubmitGitAnalysis(token, selectedProjectId, trimUrl, trimBranch)
      setJobs(prev => [job, ...prev])
      setGitUrl("")
      setGitBranch("main")
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 403) {
        setGitError("Developer role or higher required to run analysis.")
      } else if (err instanceof ApiError && err.status === 422) {
        setGitError(err.message || "Invalid repository URL or branch name.")
      } else if (err instanceof ApiError && err.status === 503) {
        setGitError("git is not available on this server.")
      } else {
        setGitError(err instanceof Error ? err.message : "Submission failed.")
      }
    } finally {
      setGitSubmitting(false)
    }
  }

  if (!selectedProjectId) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <div
          className="max-w-sm text-center px-8 py-12 rounded-xl"
          style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
        >
          <div className="text-sm mb-4" style={{ color: "var(--xm-tx-muted)" }}>No project selected.</div>
          <button onClick={() => navigate("projects")} className="xm-btn xm-btn-primary">
            Choose a project →
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-5">
      <div>
        <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>
          Code Analysis
        </h2>
        <p className="text-sm mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
          {selectedProjectName ?? "Project"} — submit source code for static analysis with Semgrep
        </p>
      </div>

      {/* Submit panel */}
      <div
        className="rounded-lg overflow-hidden"
        style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
      >
        {/* Mode tabs */}
        <div className="flex" style={{ borderBottom: "1px solid var(--xm-border)" }}>
          {(["zip", "git"] as Mode[]).map(m => (
            <button
              key={m}
              onClick={() => { setMode(m); setZipError(null); setGitError(null) }}
              className="px-5 py-2.5 text-sm font-medium flex items-center gap-1.5 transition-colors"
              style={{
                color: mode === m ? "var(--xm-accent)" : "var(--xm-tx-muted)",
                backgroundColor: mode === m ? "var(--xm-accent-subtle)" : "transparent",
                borderBottom: mode === m ? "2px solid var(--xm-accent)" : "2px solid transparent",
              }}
            >
              {m === "zip" ? <><UploadIcon className="w-4 h-4" /> Upload ZIP</> : <><GitBranchIcon className="w-4 h-4" /> Git Repository</>}
            </button>
          ))}
        </div>

        <div className="p-5">
          {mode === "zip" && (
            <form onSubmit={handleZipSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>
                  ZIP archive of source files (max 10 MB)
                </label>
                <div
                  className="border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-colors"
                  style={{ borderColor: zipFile ? "var(--xm-accent)" : "var(--xm-border)", backgroundColor: zipFile ? "var(--xm-accent-subtle)" : "transparent" }}
                  onClick={() => zipInputRef.current?.click()}
                  onMouseEnter={e => { if (!zipFile) (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-accent)" }}
                  onMouseLeave={e => { if (!zipFile) (e.currentTarget as HTMLDivElement).style.borderColor = "var(--xm-border)" }}
                >
                  {zipFile ? (
                    <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>
                      {zipFile.name}
                      <span className="ml-2" style={{ color: "var(--xm-tx-muted)" }}>({(zipFile.size / 1024).toFixed(0)} KB)</span>
                    </div>
                  ) : (
                    <>
                      <UploadIcon className="w-8 h-8 mx-auto mb-2" style={{ color: "var(--xm-tx-muted)" } as React.CSSProperties} />
                      <div className="text-sm" style={{ color: "var(--xm-tx-secondary)" }}>Click to select a ZIP file</div>
                      <div className="text-xs mt-1" style={{ color: "var(--xm-tx-muted)" }}>Python, Java, JavaScript, TypeScript supported</div>
                    </>
                  )}
                </div>
                <input
                  ref={zipInputRef}
                  type="file"
                  accept=".zip,application/zip"
                  onChange={e => setZipFile(e.target.files?.[0] ?? null)}
                  className="hidden"
                />
              </div>
              {zipError && (
                <div className="text-xs rounded px-3 py-2.5" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
                  {zipError}
                </div>
              )}
              <button type="submit" disabled={!zipFile || zipSubmitting} className="xm-btn xm-btn-primary">
                {zipSubmitting ? "Uploading…" : "Run Analysis"}
              </button>
            </form>
          )}

          {mode === "git" && (
            <form onSubmit={handleGitSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>
                  Repository URL <span style={{ color: "var(--xm-err)" }}>*</span>
                </label>
                <input
                  type="url"
                  value={gitUrl}
                  onChange={e => setGitUrl(e.target.value)}
                  placeholder="https://github.com/owner/repository"
                  className="xm-input"
                />
                <p className="text-xs mt-1" style={{ color: "var(--xm-tx-muted)" }}>
                  Public HTTPS repositories only.
                </p>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>Branch</label>
                <input
                  type="text"
                  value={gitBranch}
                  onChange={e => setGitBranch(e.target.value)}
                  placeholder="main"
                  className="xm-input"
                  style={{ maxWidth: "12rem" }}
                />
              </div>
              {gitError && (
                <div className="text-xs rounded px-3 py-2.5" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
                  {gitError}
                </div>
              )}
              <div className="flex items-center gap-4">
                <button type="submit" disabled={!gitUrl.trim() || gitSubmitting} className="xm-btn xm-btn-primary">
                  {gitSubmitting ? "Queuing…" : "Run Analysis"}
                </button>
                <p className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>Cloning may take up to 2 minutes.</p>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Job history */}
      <div
        className="rounded-lg overflow-hidden"
        style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
      >
        <div
          className="px-5 py-3.5 flex items-center justify-between"
          style={{ borderBottom: "1px solid var(--xm-border)" }}
        >
          <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Recent Analysis Jobs</h3>
          {isPolling && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: "var(--xm-info)" }}>
              <span className="w-1.5 h-1.5 rounded-full bg-current xm-pulse" />
              Live · updating
            </div>
          )}
        </div>

        {loadingJobs && (
          <div className="p-8 text-center text-sm" style={{ color: "var(--xm-tx-muted)" }}>
            <div className="xm-skeleton h-4 w-48 mx-auto rounded mb-2" />
            <div className="xm-skeleton h-4 w-64 mx-auto rounded" />
          </div>
        )}
        {jobsError && (
          <div className="p-4 text-sm" style={{ color: "var(--xm-err)" }}>{jobsError}</div>
        )}
        {!loadingJobs && !jobsError && jobs.length === 0 && (
          <div className="p-8 text-sm text-center" style={{ color: "var(--xm-tx-muted)" }}>
            No analysis jobs yet. Submit a ZIP or a Git repository URL above.
          </div>
        )}
        {jobs.length > 0 && (
          <div className="divide-y" style={{ borderColor: "var(--xm-border-sub)" }}>
            {jobs.map(job => {
              const { color, bg, label } = statusMeta(job)
              return (
                <div key={job.id} className="px-5 py-3 flex items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className="text-xs px-2 py-0.5 rounded font-medium"
                        style={{ color, backgroundColor: bg }}
                      >
                        {label}
                      </span>
                      {job.repo_url ? (
                        <span className="text-xs font-mono truncate max-w-xs" style={{ color: "var(--xm-tx-secondary)" }}>
                          {hostOf(job.repo_url)}{job.source_branch ? `@${job.source_branch}` : ""}
                        </span>
                      ) : (
                        <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>ZIP upload</span>
                      )}
                      {job.source_revision && shortSha(job.source_revision) && (
                        <span
                          className="text-xs font-mono px-1 rounded"
                          style={{ color: "var(--xm-tx-muted)", backgroundColor: "var(--xm-bg-elevated)" }}
                        >
                          {shortSha(job.source_revision)}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 mt-1 text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                      <ClockIcon className="w-3 h-3" />
                      {new Date(job.created_at).toLocaleString()}
                      {job.engine_version && ` · semgrep ${job.engine_version}`}
                    </div>
                    {job.failure_reason && (
                      <div className="text-xs mt-0.5 truncate max-w-lg" style={{ color: "var(--xm-err)" }}>
                        {job.failure_reason}
                      </div>
                    )}
                  </div>
                  {job.status === "completed" && (
                    <div className="shrink-0 flex items-center gap-5">
                      <div className="space-y-0.5 text-xs text-right">
                        {[
                          ["Vulns", job.vulnerabilities_count],
                          ["Bugs", job.bugs_count],
                          ["Smells", job.code_smells_count],
                        ].map(([lbl, count]) => (
                          <div key={String(lbl)} className="flex gap-2 justify-end">
                            <span style={{ color: "var(--xm-tx-muted)" }}>{lbl}</span>
                            <span
                              className="font-medium"
                              style={{ color: Number(count) > 0 ? "var(--xm-err)" : "var(--xm-tx-secondary)" }}
                            >
                              {count}
                            </span>
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={() => navigate("issues")}
                        className="xm-btn xm-btn-secondary text-xs px-2 py-1"
                      >
                        View →
                      </button>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Security note */}
      <div
        className="rounded-lg px-4 py-3 text-xs"
        style={{ backgroundColor: "var(--xm-bg-elevated)", border: "1px solid var(--xm-border)", color: "var(--xm-tx-muted)" }}
      >
        <strong style={{ color: "var(--xm-tx-secondary)" }}>Repository analysis:</strong> Only public HTTPS repositories are supported.
        Source code is cloned on the server, analysed with Semgrep, and the workspace is removed after analysis.
        Source code from cloned repositories is never executed.
        {" "}<strong style={{ color: "var(--xm-tx-secondary)" }}>Limitation:</strong> SSRF protection uses DNS pre-validation;
        DNS rebinding is not fully mitigated. Ensure the server's egress firewall blocks RFC 1918 ranges.
      </div>
    </div>
  )
}
