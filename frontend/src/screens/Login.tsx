import { useState } from "react"
import { useNav } from "../App"
import { CodeIcon, ShieldIcon } from "../components/Icons"
import { apiLogin, ApiError } from "../lib/api"

export default function Login() {
  const { login } = useNav()
  const [email, setEmail] = useState("jane.doe@university.ac.uk")
  const [password, setPassword] = useState("password")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || !password) return
    setLoading(true)
    setError(null)
    try {
      const res = await apiLogin(email.trim(), password)
      login(res.access_token, res.user)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 401 ? "Invalid email or password." : `Error ${err.status}: ${err.message}`)
      } else {
        setError("Could not reach the server. Is the backend running?")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-full flex items-center justify-center px-4"
      style={{ backgroundColor: "var(--xm-bg-app)" }}
    >
      <div className="w-full max-w-sm">

        {/* Brand mark */}
        <div className="text-center mb-8">
          <div
            className="inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4"
            style={{ backgroundColor: "var(--xm-accent)", boxShadow: "0 0 32px var(--xm-accent-subtle)" }}
          >
            <CodeIcon className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>
            Explicite AI
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--xm-tx-muted)" }}>
            Code intelligence platform
          </p>
        </div>

        {/* Form card */}
        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--xm-bg-surface)",
            border: "1px solid var(--xm-border)",
          }}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                className="block text-xs font-medium mb-1.5"
                style={{ color: "var(--xm-tx-secondary)" }}
              >
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                disabled={loading}
                autoComplete="email"
                className="xm-input"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium" style={{ color: "var(--xm-tx-secondary)" }}>
                  Password
                </label>
              </div>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                disabled={loading}
                autoComplete="current-password"
                className="xm-input"
              />
            </div>

            {error && (
              <div
                className="text-xs rounded px-3 py-2.5"
                style={{
                  backgroundColor: "var(--xm-err-sub)",
                  border: "1px solid var(--xm-err)",
                  color: "var(--xm-err)",
                  borderColor: "color-mix(in srgb, var(--xm-err) 40%, transparent)",
                }}
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="xm-btn xm-btn-primary w-full py-2.5 mt-1 text-sm font-medium"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="xm-spin w-4 h-4" fill="none" viewBox="0 0 24 24" aria-hidden>
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                  Signing in…
                </span>
              ) : "Sign in"}
            </button>
          </form>
        </div>

        {/* Security note */}
        <div className="flex items-center justify-center gap-1.5 mt-5">
          <ShieldIcon className="w-3.5 h-3.5" style={{ color: "var(--xm-tx-muted)" } as React.CSSProperties} />
          <p className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>
            Secured · Sessions expire on tab close
          </p>
        </div>
      </div>
    </div>
  )
}
