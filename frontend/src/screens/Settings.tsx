import { useEffect, useState } from "react"
import { useNav } from "../App"
import {
  apiUpdateProfile,
  ApiError,
  type ProfileUpdateRequest,
  type UserPreferences,
  DEFAULT_PREFERENCES,
} from "../lib/api"
import {
  applyAppearance,
  loadAppearance,
  saveAppearance,
  type AppearanceSettings,
} from "../lib/appearance"

const SECTIONS = ["Profile", "Appearance", "Preferences", "Project Defaults", "Analysis Settings", "Developer Settings"]

const SECTION_DESC: Record<string, string> = {
  Profile: "Manage your account information.",
  Appearance: "Customise the visual appearance. Saved to this device only.",
  Preferences: "Notification and workflow preferences. Saved to your account.",
  "Project Defaults": "Default values applied to new projects. Saved to your account.",
  "Analysis Settings": "Quality gate thresholds for new analyses. Saved to your account.",
  "Developer Settings": "Advanced settings and API integrations.",
}

// ── Shared field components ────────────────────────────────────────────────────

function Field({ label, value, type = "text", readOnly, onChange, hint }: {
  label: string; value: string; type?: string; readOnly?: boolean; onChange?: (v: string) => void; hint?: string
}) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>{label}</label>
      <input
        type={type}
        value={value}
        readOnly={readOnly}
        onChange={e => onChange?.(e.target.value)}
        className={`xm-input ${readOnly ? "cursor-not-allowed opacity-60" : ""}`}
        style={readOnly ? { backgroundColor: "var(--xm-bg-elevated)" } : {}}
      />
      {hint && <p className="mt-1 text-xs" style={{ color: "var(--xm-tx-muted)" }}>{hint}</p>}
    </div>
  )
}

function NumberField({ label, value, min = 0, max, onChange, hint }: {
  label: string; value: number; min?: number; max?: number; onChange: (v: number) => void; hint?: string
}) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>{label}</label>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={e => onChange(Number(e.target.value))}
        className="xm-input"
        style={{ maxWidth: "10rem" }}
      />
      {hint && <p className="mt-1 text-xs" style={{ color: "var(--xm-tx-muted)" }}>{hint}</p>}
    </div>
  )
}

function SelectField({ label, options, value, onChange }: {
  label: string; options: string[]; value: string; onChange: (v: string) => void
}) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--xm-tx-secondary)" }}>{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)} className="xm-select w-full">
        {options.map(o => <option key={o}>{o}</option>)}
      </select>
    </div>
  )
}

function SaveRow({ saving, success, error, onSave, dirty }: {
  saving: boolean; success: string | null; error: string | null; onSave: () => void; dirty: boolean
}) {
  return (
    <div className="flex items-center gap-3 pt-1">
      <button onClick={onSave} disabled={saving || !dirty} className="xm-btn xm-btn-primary">
        {saving ? "Saving…" : "Save Changes"}
      </button>
      {success && <span className="text-xs" style={{ color: "var(--xm-ok)" }}>{success}</span>}
      {error && <span className="text-xs" style={{ color: "var(--xm-err)" }}>{error}</span>}
      {dirty && !saving && !success && <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>Unsaved changes</span>}
    </div>
  )
}

// ── Profile ────────────────────────────────────────────────────────────────────

function ProfileSection() {
  const { token, currentUser, logout, updateCurrentUser } = useNav()
  const [fullName, setFullName] = useState(currentUser?.full_name ?? "")
  const [department, setDepartment] = useState(currentUser?.department ?? "")
  const [experienceLevel, setExperienceLevel] = useState(currentUser?.experience_level ?? "beginner")
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const dirty =
    fullName !== (currentUser?.full_name ?? "") ||
    department !== (currentUser?.department ?? "") ||
    experienceLevel !== (currentUser?.experience_level ?? "beginner")

  async function handleSave() {
    if (!token || saving) { if (!token) logout(); return }
    setSaving(true); setSuccess(null); setError(null)
    const payload: ProfileUpdateRequest = {}
    if (fullName !== currentUser?.full_name) payload.full_name = fullName
    if (department !== (currentUser?.department ?? "")) payload.department = department
    if (experienceLevel !== currentUser?.experience_level) payload.experience_level = experienceLevel
    try {
      const updated = await apiUpdateProfile(token, payload)
      updateCurrentUser(updated)
      setSuccess("Profile saved.")
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      setError(err instanceof Error ? err.message : "Failed to save profile")
    } finally { setSaving(false) }
  }

  return (
    <>
      <Field label="Full name" value={fullName} onChange={v => { setFullName(v); setSuccess(null) }} />
      <Field label="Email address" value={currentUser?.email ?? ""} type="email" readOnly />
      <Field label="Role" value={currentUser?.system_role === "system_admin" ? "Administrator" : "Developer"} readOnly />
      <Field label="Department" value={department} onChange={v => { setDepartment(v); setSuccess(null) }} />
      <SelectField label="Experience level" options={["beginner", "intermediate", "advanced"]} value={experienceLevel} onChange={v => { setExperienceLevel(v); setSuccess(null) }} />
      <SaveRow saving={saving} success={success} error={error} onSave={handleSave} dirty={dirty} />
    </>
  )
}

// ── Appearance ─────────────────────────────────────────────────────────────────

function AppearanceSection() {
  const [settings, setSettings] = useState<AppearanceSettings>(loadAppearance)
  const [saved, setSaved] = useState<AppearanceSettings>(loadAppearance)
  const dirty = JSON.stringify(settings) !== JSON.stringify(saved)

  function update(patch: Partial<AppearanceSettings>) { setSettings(prev => ({ ...prev, ...patch })) }

  function handleSave() {
    saveAppearance(settings)
    applyAppearance(settings)
    setSaved({ ...settings })
  }

  return (
    <>
      <SelectField label="Theme" options={["Dark", "Light (default)", "System"]} value={settings.theme} onChange={v => update({ theme: v })} />
      <SelectField label="Code font size" options={["12px", "13px", "14px", "16px"]} value={settings.codeFontSize} onChange={v => update({ codeFontSize: v })} />
      <SelectField label="Code colour scheme" options={["Dark (default)", "Light", "High Contrast"]} value={settings.codeColorScheme} onChange={v => update({ codeColorScheme: v })} />
      <div className="flex items-center gap-3 pt-1">
        <button onClick={handleSave} disabled={!dirty} className="xm-btn xm-btn-primary">Save Changes</button>
        {!dirty && <span className="text-xs" style={{ color: "var(--xm-ok)" }}>Saved.</span>}
        {dirty && <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>Unsaved — click Save to apply.</span>}
      </div>
    </>
  )
}

// ── Shared backend-preferences hook ──────────────────────────────────────────

function usePreferencesSave(prefs: Partial<UserPreferences>, setPrefs: (p: UserPreferences) => void) {
  const { token, logout, updateCurrentUser } = useNav()
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [fieldError, setFieldError] = useState<Record<string, string>>({})

  async function handleSave() {
    if (!token || saving) { if (!token) logout(); return }
    setSaving(true); setSuccess(null); setError(null); setFieldError({})
    try {
      const updated = await apiUpdateProfile(token, { preferences: prefs })
      updateCurrentUser(updated)
      setPrefs(updated.preferences)
      setSuccess("Saved.")
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      if (err instanceof ApiError && err.status === 422) {
        if (Array.isArray(err.detail)) {
          const fe: Record<string, string> = {}
          for (const d of err.detail) {
            const loc: string = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : "unknown"
            fe[loc] = d.msg ?? "Invalid"
          }
          setFieldError(fe)
        } else {
          setError("Validation error — check values.")
        }
      } else {
        setError(err instanceof Error ? err.message : "Failed to save.")
      }
    } finally { setSaving(false) }
  }

  return { saving, success, error, fieldError, handleSave }
}

function PreferencesSection() {
  const { currentUser } = useNav()
  const base = currentUser?.preferences ?? DEFAULT_PREFERENCES
  const [emailNotifs, setEmailNotifs] = useState(base.email_notifications)
  const [issueSort, setIssueSort] = useState(base.default_issue_sort)
  const [aiLevel, setAiLevel] = useState(base.ai_explain_level)
  const patch = { email_notifications: emailNotifs, default_issue_sort: issueSort, ai_explain_level: aiLevel }
  const dirty = emailNotifs !== base.email_notifications || issueSort !== base.default_issue_sort || aiLevel !== base.ai_explain_level
  const { saving, success, error, handleSave } = usePreferencesSave(patch, () => {})
  return (
    <>
      <SelectField label="Email notifications" options={["All issues", "Critical and High only", "None"]} value={emailNotifs} onChange={setEmailNotifs} />
      <SelectField label="Default issue sort" options={["Severity (highest first)", "Date detected", "File name"]} value={issueSort} onChange={setIssueSort} />
      <SelectField label="AI explanation verbosity" options={["beginner", "intermediate", "advanced"]} value={aiLevel} onChange={setAiLevel} />
      <SaveRow saving={saving} success={success} error={error} onSave={handleSave} dirty={dirty} />
    </>
  )
}

function ProjectDefaultsSection() {
  const { currentUser } = useNav()
  const base = currentUser?.preferences ?? DEFAULT_PREFERENCES
  const [branch, setBranch] = useState(base.default_branch)
  const [autoRun, setAutoRun] = useState(base.auto_run_analysis)
  const [exclusions, setExclusions] = useState(base.analysis_exclusions)
  const patch = { default_branch: branch, auto_run_analysis: autoRun, analysis_exclusions: exclusions }
  const dirty = branch !== base.default_branch || autoRun !== base.auto_run_analysis || exclusions !== base.analysis_exclusions
  const { saving, success, error, handleSave } = usePreferencesSave(patch, () => {})
  return (
    <>
      <Field label="Default branch" value={branch} onChange={setBranch} hint="Pre-filled when creating new projects." />
      <SelectField label="Auto-run analysis on push" options={["Enabled", "Disabled"]} value={autoRun} onChange={setAutoRun} />
      <Field label="Analysis exclusions (glob patterns)" value={exclusions} onChange={setExclusions} hint="Comma-separated, e.g. **/test/**, **/generated/**" />
      <SaveRow saving={saving} success={success} error={error} onSave={handleSave} dirty={dirty} />
    </>
  )
}

function AnalysisSettingsSection() {
  const { currentUser } = useNav()
  const base = currentUser?.preferences ?? DEFAULT_PREFERENCES
  const [maxBugs, setMaxBugs] = useState(base.quality_gate_max_bugs)
  const [maxVulns, setMaxVulns] = useState(base.quality_gate_max_vulnerabilities)
  const [maxSmells, setMaxSmells] = useState(base.quality_gate_max_code_smells)
  const [coverage, setCoverage] = useState(base.quality_gate_coverage_threshold)
  const [debt, setDebt] = useState(base.quality_gate_debt_hours)
  const patch = { quality_gate_max_bugs: maxBugs, quality_gate_max_vulnerabilities: maxVulns, quality_gate_max_code_smells: maxSmells, quality_gate_coverage_threshold: coverage, quality_gate_debt_hours: debt }
  const dirty = maxBugs !== base.quality_gate_max_bugs || maxVulns !== base.quality_gate_max_vulnerabilities || maxSmells !== base.quality_gate_max_code_smells || coverage !== base.quality_gate_coverage_threshold || debt !== base.quality_gate_debt_hours
  const { saving, success, error, handleSave } = usePreferencesSave(patch, () => {})
  return (
    <>
      <div
        className="text-xs rounded px-3 py-2.5"
        style={{ backgroundColor: "var(--xm-warn-sub)", color: "var(--xm-warn)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}
      >
        These thresholds are applied to the quality gate when you submit a new analysis. Setting a threshold to 0 means zero are allowed.
      </div>
      <NumberField label="Coverage threshold (%)" value={coverage} min={0} max={100} onChange={setCoverage} hint="Set to 0 to disable coverage enforcement." />
      <NumberField label="Maximum bugs (Quality Gate)" value={maxBugs} min={0} max={100} onChange={setMaxBugs} />
      <NumberField label="Maximum vulnerabilities" value={maxVulns} min={0} max={100} onChange={setMaxVulns} />
      <NumberField label="Maximum code smells" value={maxSmells} min={0} max={1000} onChange={setMaxSmells} />
      <NumberField label="Technical debt threshold (hours)" value={debt} min={0} max={9999} onChange={setDebt} />
      <SaveRow saving={saving} success={success} error={error} onSave={handleSave} dirty={dirty} />
    </>
  )
}

function DeveloperSettingsSection() {
  return (
    <div className="space-y-4">
      <div
        className="rounded-lg px-4 py-3"
        style={{ backgroundColor: "var(--xm-warn-sub)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}
      >
        <p className="text-sm font-medium mb-1" style={{ color: "var(--xm-warn)" }}>SonarQube integration not available</p>
        <p className="text-sm" style={{ color: "var(--xm-tx-secondary)" }}>
          This application uses Semgrep as its static analysis engine. SonarQube project keys, server URLs, and analysis tokens have no effect. These controls are shown for reference only.
        </p>
      </div>
      <div className="opacity-50 pointer-events-none space-y-4">
        <Field label="SonarQube server URL" value="http://localhost:9000" readOnly />
        <Field label="Project key" value="com.university:student-management" readOnly />
        <Field label="Analysis token" value="••••••••••••••••" type="password" readOnly />
        <SelectField label="Java version" options={["Java 17", "Java 11", "Java 8"]} value="Java 17" onChange={() => {}} />
      </div>
    </div>
  )
}

// ── Settings screen ────────────────────────────────────────────────────────────

export default function Settings() {
  const [active, setActive] = useState("Profile")

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sidebar nav */}
      <div
        className="w-44 shrink-0 py-3 overflow-y-auto"
        style={{ borderRight: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-sidebar)" }}
      >
        {SECTIONS.map(s => (
          <button
            key={s}
            onClick={() => setActive(s)}
            className="w-full text-left px-4 py-2 text-sm transition-colors relative"
            style={{
              color: active === s ? "var(--xm-accent)" : "var(--xm-tx-secondary)",
              backgroundColor: active === s ? "var(--xm-accent-subtle)" : "transparent",
              fontWeight: active === s ? "500" : "400",
              borderRight: active === s ? "2px solid var(--xm-accent)" : "2px solid transparent",
            }}
            onMouseEnter={e => {
              if (active !== s) {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-bg-hover)"
                ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-primary)"
              }
            }}
            onMouseLeave={e => {
              if (active !== s) {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
                ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)"
              }
            }}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <h2 className="text-lg font-semibold mb-0.5" style={{ color: "var(--xm-tx-primary)" }}>{active}</h2>
        <p className="text-sm mb-6" style={{ color: "var(--xm-tx-muted)" }}>{SECTION_DESC[active]}</p>
        <div className="max-w-md space-y-4">
          {active === "Profile"            && <ProfileSection />}
          {active === "Appearance"         && <AppearanceSection />}
          {active === "Preferences"        && <PreferencesSection />}
          {active === "Project Defaults"   && <ProjectDefaultsSection />}
          {active === "Analysis Settings"  && <AnalysisSettingsSection />}
          {active === "Developer Settings" && <DeveloperSettingsSection />}
        </div>
      </div>
    </div>
  )
}
