import { useEffect, useRef, useState } from "react"
import { useNav } from "../App"
import { FolderIcon, AnalyzeIcon, UploadIcon } from "../components/Icons"
import {
  apiGetProjects,
  apiCreateProject,
  apiSubmitAnalysis,
  apiGetAnalysisJob,
  type ApiProject,
  type ApiAnalysisJob,
  ApiError,
} from "../lib/api"

// ─── Create modal ─────────────────────────────────────────────────────────────

interface CreateModalProps {
  token: string
  onCreated: (project: ApiProject) => void
  onClose: () => void
  defaultBranch?: string
}

function CreateProjectModal({ token, onCreated, onClose, defaultBranch = "main" }: CreateModalProps) {
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [branch, setBranch] = useState(defaultBranch)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const nameRef = useRef<HTMLInputElement>(null)
  useEffect(() => { nameRef.current?.focus() }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmedName = name.trim()
    if (!trimmedName) { setError("Project name is required."); return }
    if (trimmedName.length > 255) { setError("Project name must be 255 characters or fewer."); return }
    setSaving(true)
    setError(null)
    try {
      const created = await apiCreateProject(token, {
        name: trimmedName,
        description: description.trim() || undefined,
        default_branch: branch.trim() || "main",
      })
      onCreated(created)
    } catch (err) {
      setSaving(false)
      setError(err instanceof ApiError ? (err.message || "Failed to create project.") : (err instanceof Error ? err.message : "Failed to create project."))
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        className="w-full max-w-md mx-4 rounded-xl shadow-2xl"
        style={{ backgroundColor: "var(--xm-bg-elevated)", border: "1px solid var(--xm-border)" }}
      >
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--xm-border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Create New Project</h3>
          <button onClick={onClose} className="text-lg leading-none" style={{ color: "var(--xm-tx-muted)" }}>×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-5 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>
              Project name <span style={{ color: "var(--xm-err)" }}>*</span>
            </label>
            <input ref={nameRef} type="text" value={name} onChange={e => setName(e.target.value)} maxLength={255} placeholder="e.g. Student Management System" className="xm-input" />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>Description <span style={{ color: "var(--xm-tx-muted)" }}>(optional)</span></label>
            <textarea value={description} onChange={e => setDescription(e.target.value)} rows={2} maxLength={2000} placeholder="Short description" className="xm-input resize-none" />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>Default branch</label>
            <input type="text" value={branch} onChange={e => setBranch(e.target.value)} placeholder="main" className="xm-input" />
          </div>
          {error && (
            <div className="text-xs rounded px-3 py-2.5" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
              {error}
            </div>
          )}
          <div className="flex justify-end gap-2 pt-1">
            <button type="button" onClick={onClose} disabled={saving} className="xm-btn xm-btn-secondary">Cancel</button>
            <button type="submit" disabled={saving} className="xm-btn xm-btn-primary">{saving ? "Creating…" : "Create Project"}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ─── Analyse modal ─────────────────────────────────────────────────────────────

function AnalyseModal({ projectName, onClose, onSubmit }: { projectName: string; onClose: () => void; onSubmit: (file: File) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-md mx-4 rounded-xl shadow-2xl"
        style={{ backgroundColor: "var(--xm-bg-elevated)", border: "1px solid var(--xm-border)" }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--xm-border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>Analyse: {projectName}</h3>
          <button onClick={onClose} className="text-lg leading-none" style={{ color: "var(--xm-tx-muted)" }}>×</button>
        </div>
        <div className="px-5 py-4 space-y-4">
          <p className="text-sm" style={{ color: "var(--xm-tx-secondary)" }}>
            Upload a ZIP archive (max 10 MB). Supported: <span className="font-mono text-xs">.py .java .js .ts .jsx .tsx</span>
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
              </>
            )}
          </div>
          <input ref={inputRef} type="file" accept=".zip,application/zip" className="hidden" onChange={e => setFile(e.target.files?.[0] ?? null)} />
          <div className="flex gap-2 justify-end">
            <button onClick={onClose} className="xm-btn xm-btn-secondary">Cancel</button>
            <button disabled={!file} onClick={() => file && onSubmit(file)} className="xm-btn xm-btn-primary">Start Analysis</button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Status dot ───────────────────────────────────────────────────────────────

function QualityGateBadge({ status }: { status: string }) {
  const passed = status === "Passed"
  const color = passed ? "var(--xm-ok)" : status === "Failed" ? "var(--xm-err)" : "var(--xm-tx-muted)"
  const bg    = passed ? "var(--xm-ok-sub)" : status === "Failed" ? "var(--xm-err-sub)" : "var(--xm-bg-elevated)"
  return (
    <span
      className="inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded"
      style={{ color, backgroundColor: bg }}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  )
}

// ─── Projects screen ──────────────────────────────────────────────────────────

export default function Projects() {
  const { token, openProject, logout, preferences } = useNav()
  const [projects, setProjects] = useState<ApiProject[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [analysingProject, setAnalysingProject] = useState<{ id: string; name: string } | null>(null)
  const [activeJobs, setActiveJobs] = useState<Record<string, ApiAnalysisJob>>({})
  const [analyseError, setAnalyseError] = useState<string | null>(null)

  function loadProjects() {
    if (!token) { logout(); return }
    setLoading(true)
    setError(null)
    apiGetProjects(token)
      .then(data => { setProjects(data); setLoading(false) })
      .catch(err => {
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to load projects")
        setLoading(false)
      })
  }

  useEffect(() => { loadProjects() }, [token])

  function handleCreated(project: ApiProject) {
    setShowModal(false)
    setProjects(prev => [project, ...prev])
    loadProjects()
  }

  async function handleAnalyseSubmit(file: File) {
    if (!token || !analysingProject) return
    const { id: projectId } = analysingProject
    setAnalysingProject(null)
    setAnalyseError(null)
    try {
      const job = await apiSubmitAnalysis(token, projectId, file)
      setActiveJobs(prev => ({ ...prev, [projectId]: job }))
    } catch (err) {
      setAnalyseError(err instanceof ApiError ? err.message : "Failed to start analysis")
    }
  }

  useEffect(() => {
    const running = Object.entries(activeJobs).filter(([, job]) => job.status !== "completed" && job.status !== "failed")
    if (!running.length || !token) return
    let cancelled = false
    const interval = setInterval(() => {
      running.forEach(([projectId, job]) => {
        apiGetAnalysisJob(token, projectId, job.id)
          .then(updated => {
            if (!cancelled) {
              setActiveJobs(prev => ({ ...prev, [projectId]: updated }))
              if (updated.status === "completed") loadProjects()
            }
          })
          .catch(() => {})
      })
    }, 2000)
    return () => { cancelled = true; clearInterval(interval) }
  }, [activeJobs, token])

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {showModal && token && (
        <CreateProjectModal token={token} onCreated={handleCreated} onClose={() => setShowModal(false)} defaultBranch={preferences.default_branch} />
      )}
      {analysingProject && (
        <AnalyseModal projectName={analysingProject.name} onClose={() => setAnalysingProject(null)} onSubmit={handleAnalyseSubmit} />
      )}

      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>Projects</h2>
          <p className="text-sm mt-0.5" style={{ color: "var(--xm-tx-secondary)" }}>
            {loading ? "Loading…" : `${projects.length} project${projects.length === 1 ? "" : "s"}`}
          </p>
        </div>
        <button onClick={() => setShowModal(true)} className="xm-btn xm-btn-primary">
          <FolderIcon className="w-4 h-4" />
          New Project
        </button>
      </div>

      {error && (
        <div className="mb-4 text-sm rounded-lg px-4 py-3" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          {error}
        </div>
      )}
      {analyseError && (
        <div className="mb-4 text-sm rounded-lg px-4 py-3 flex items-center justify-between" style={{ backgroundColor: "var(--xm-err-sub)", color: "var(--xm-err)", border: "1px solid color-mix(in srgb, var(--xm-err) 40%, transparent)" }}>
          <span>{analyseError}</span>
          <button onClick={() => setAnalyseError(null)} className="text-xs underline ml-3">Dismiss</button>
        </div>
      )}

      {loading ? (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => <div key={i} className="xm-skeleton h-14 rounded-lg" />)}
        </div>
      ) : (
        <div
          className="rounded-lg overflow-hidden"
          style={{ border: "1px solid var(--xm-border)" }}
        >
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}>
                {["Project", "Quality Gate", "Bugs", "Vulnerabilities", "Smells", "Coverage", "Last Analysis", ""].map(h => (
                  <th
                    key={h}
                    className="text-left px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider"
                    style={{ color: "var(--xm-tx-muted)" }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="px-4 py-12 text-center text-sm" style={{ color: "var(--xm-tx-muted)", backgroundColor: "var(--xm-bg-surface)" }}>
                      No projects yet.{" "}
                      <button onClick={() => setShowModal(true)} className="underline" style={{ color: "var(--xm-accent)" }}>
                        Create your first project
                      </button>
                    </div>
                  </td>
                </tr>
              ) : projects.map((p, idx) => (
                <tr
                  key={p.id}
                  style={{
                    backgroundColor: "var(--xm-bg-surface)",
                    borderBottom: idx < projects.length - 1 ? "1px solid var(--xm-border-sub)" : "none",
                  }}
                  onMouseEnter={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "var(--xm-bg-hover)" }}
                  onMouseLeave={e => { (e.currentTarget as HTMLTableRowElement).style.backgroundColor = "var(--xm-bg-surface)" }}
                >
                  <td className="px-4 py-3">
                    <div className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{p.name}</div>
                    <div className="text-xs font-mono" style={{ color: "var(--xm-tx-muted)" }}>{p.branch}</div>
                  </td>
                  <td className="px-4 py-3"><QualityGateBadge status={p.status} /></td>
                  <td className="px-4 py-3 text-sm font-semibold" style={{ color: p.bugs > 0 ? "var(--xm-err)" : "var(--xm-tx-secondary)" }}>{p.bugs}</td>
                  <td className="px-4 py-3 text-sm font-semibold" style={{ color: p.vulnerabilities > 0 ? "var(--xm-high)" : "var(--xm-tx-secondary)" }}>{p.vulnerabilities}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: p.code_smells > 0 ? "var(--xm-medium)" : "var(--xm-tx-secondary)" }}>{p.code_smells}</td>
                  <td className="px-4 py-3 text-sm" style={{ color: "var(--xm-tx-secondary)" }}>{p.coverage ?? "—"}</td>
                  <td className="px-4 py-3 text-xs" style={{ color: "var(--xm-tx-muted)" }}>{p.last_analysis ?? "Never"}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => openProject(p.id, p.name)}
                        className="text-xs font-medium transition-colors"
                        style={{ color: "var(--xm-accent)" }}
                        onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent-hover)" }}
                        onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                      >
                        Open
                      </button>
                      {activeJobs[p.id] && activeJobs[p.id].status !== "completed" && activeJobs[p.id].status !== "failed" ? (
                        <span className="text-xs xm-pulse" style={{ color: "var(--xm-info)" }}>Analysing…</span>
                      ) : activeJobs[p.id]?.status === "completed" ? (
                        <span className="text-xs font-medium" style={{ color: "var(--xm-ok)" }}>
                          ✓ {activeJobs[p.id].findings_count ?? 0} findings
                        </span>
                      ) : activeJobs[p.id]?.status === "failed" ? (
                        <button
                          onClick={() => setAnalysingProject({ id: p.id, name: p.name })}
                          className="text-xs"
                          style={{ color: "var(--xm-err)" }}
                          title={activeJobs[p.id].failure_reason ?? "Analysis failed"}
                        >
                          Retry
                        </button>
                      ) : (
                        <button
                          onClick={() => setAnalysingProject({ id: p.id, name: p.name })}
                          className="text-xs transition-colors"
                          style={{ color: "var(--xm-tx-muted)" }}
                          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)" }}
                        >
                          <AnalyzeIcon className="w-3.5 h-3.5 inline mr-0.5" />
                          Analyse
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
