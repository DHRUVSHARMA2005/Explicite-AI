import { useRef, useState } from "react"
import { useNav } from "../App"
import { SparkleIcon } from "../components/Icons"
import { apiAskAssistant, type ApiIssueSummary, ApiError } from "../lib/api"

interface Message {
  role: "user" | "assistant"
  content: string
  error?: boolean
}

const SUGGESTED = [
  "What does this issue mean?",
  "Why is this risky?",
  "How should I investigate this?",
  "What should I check in the code?",
  "Show me a safer approach.",
]

function buildInitialMessages(issue: ApiIssueSummary | null): Message[] {
  if (!issue) {
    return [{
      role: "assistant",
      content: "No issue is currently selected. Navigate to an issue and click 'AI Assistant' to start a context-aware conversation.",
    }]
  }
  return [{
    role: "assistant",
    content: `I am ready to help you understand the "${issue.title}" issue${issue.file ? ` in ${issue.file}${issue.line ? `:${issue.line}` : ""}` : ""}.\n\nThis is a ${issue.severity} severity issue (${issue.risk} risk). Ask me anything about what it means, why it matters, or how to remediate it.`,
  }]
}

function severityColor(s: string): string {
  if (s === "Critical" || s === "High") return "var(--xm-err)"
  if (s === "Medium") return "var(--xm-medium)"
  return "var(--xm-tx-muted)"
}

export default function AIAssistant() {
  const { token, selectedProjectId, selectedIssueSummary, selectedIssueId, logout } = useNav()
  const [messages, setMessages] = useState<Message[]>(() => buildInitialMessages(selectedIssueSummary))
  const [input, setInput] = useState("")
  const [pending, setPending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const issueTitle = selectedIssueSummary?.title ?? null

  const send = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || pending) return
    if (!token || !selectedProjectId) {
      setMessages(prev => [
        ...prev,
        { role: "user", content: trimmed },
        { role: "assistant", content: "No project is selected. Please select a project first.", error: true },
      ])
      return
    }
    const withUser: Message[] = [...messages, { role: "user", content: trimmed }]
    setMessages(withUser)
    setInput("")
    setPending(true)
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50)

    try {
      const result = await apiAskAssistant(token, selectedProjectId, trimmed, selectedIssueId ?? undefined)
      setMessages([...withUser, { role: "assistant", content: result.reply }])
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      let msg: string
      if (err instanceof ApiError && err.status === 503) {
        msg = "AI model is not configured. Ask your administrator to set up an AI provider in .env."
      } else if (err instanceof ApiError && err.status === 422) {
        msg = "Your message could not be processed (too long or empty). Please shorten it and try again."
      } else {
        msg = err instanceof Error ? err.message : "Failed to get a response. Please try again."
      }
      setMessages([...withUser, { role: "assistant", content: msg, error: true }])
    } finally {
      setPending(false)
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50)
    }
  }

  return (
    <div className="flex h-full overflow-hidden">
      {/* Chat panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Context header */}
        <div
          className="px-4 py-3 shrink-0"
          style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <SparkleIcon className="w-4 h-4" style={{ color: "var(--xm-accent)" } as React.CSSProperties} />
              <h2 className="text-sm font-semibold" style={{ color: "var(--xm-tx-primary)" }}>AI Code Assistant</h2>
              <span
                className="text-xs px-1.5 py-0.5 rounded font-medium"
                style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}
              >
                AI-powered
              </span>
            </div>
            <span className="text-xs" style={{ color: "var(--xm-tx-muted)" }}>All responses should be verified</span>
          </div>
          <div
            className="flex items-center gap-4 px-3 py-2 rounded flex-wrap text-xs"
            style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}
          >
            {selectedIssueSummary ? (
              <>
                <span style={{ color: "var(--xm-tx-muted)" }}>Issue: <span className="font-semibold" style={{ color: "var(--xm-tx-primary)" }}>{selectedIssueSummary.title}</span></span>
                <span style={{ color: "var(--xm-border)" }}>·</span>
                <span style={{ color: "var(--xm-tx-muted)" }}>Severity: <span className="font-semibold" style={{ color: severityColor(selectedIssueSummary.severity) }}>{selectedIssueSummary.severity}</span></span>
                <span style={{ color: "var(--xm-border)" }}>·</span>
                <span style={{ color: "var(--xm-tx-muted)" }}>Risk: <span className="font-semibold" style={{ color: selectedIssueSummary.risk === "High" ? "var(--xm-err)" : selectedIssueSummary.risk === "Medium" ? "var(--xm-medium)" : "var(--xm-tx-secondary)" }}>{selectedIssueSummary.risk}</span></span>
                {selectedIssueSummary.file && (
                  <>
                    <span style={{ color: "var(--xm-border)" }}>·</span>
                    <span className="font-mono" style={{ color: "var(--xm-tx-secondary)" }}>
                      {selectedIssueSummary.file}{selectedIssueSummary.line ? `:${selectedIssueSummary.line}` : ""}
                    </span>
                  </>
                )}
              </>
            ) : (
              <span className="italic" style={{ color: "var(--xm-tx-muted)" }}>No issue selected — navigate to an issue and click AI Assistant</span>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ backgroundColor: "var(--xm-bg-app)" }}>
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-lg text-sm leading-relaxed ${msg.role === "user" ? "rounded-br-sm px-3.5 py-2.5 text-white" : "rounded-bl-sm overflow-hidden"}`}
                style={msg.role === "user"
                  ? { backgroundColor: "var(--xm-accent)" }
                  : msg.error
                  ? { backgroundColor: "var(--xm-warn-sub)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }
                  : { backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }
                }
              >
                {msg.role === "assistant" && (
                  <div
                    className="px-3.5 pt-2.5 pb-1.5 flex items-center gap-1.5"
                    style={{ borderBottom: "1px solid var(--xm-border-sub)" }}
                  >
                    <span className="text-xs font-medium" style={{ color: "var(--xm-tx-muted)" }}>
                      AI Response{issueTitle ? ` · ${issueTitle}` : ""}
                    </span>
                    {!msg.error && (
                      <span className="text-xs px-1 py-0.5 rounded" style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}>
                        AI-generated
                      </span>
                    )}
                  </div>
                )}
                <div
                  className={`whitespace-pre-wrap ${msg.role === "assistant" ? "px-3.5 py-2.5" : ""}`}
                  style={msg.role === "assistant" ? { color: "var(--xm-tx-secondary)" } : {}}
                >
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {pending && (
            <div className="flex justify-start">
              <div
                className="rounded-lg rounded-bl-sm px-3.5 py-3 text-sm flex items-center gap-2"
                style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)", color: "var(--xm-tx-muted)" }}
              >
                <svg className="xm-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" aria-hidden>
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div
          className="p-4 shrink-0"
          style={{ borderTop: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !e.shiftKey && send(input)}
              placeholder="Ask about the issue, the fix, or security concepts…"
              disabled={pending}
              className="xm-input flex-1"
            />
            <button onClick={() => send(input)} disabled={pending || !input.trim()} className="xm-btn xm-btn-primary">
              {pending ? "…" : "Send"}
            </button>
          </div>
          <p className="text-xs mt-1.5" style={{ color: "var(--xm-tx-muted)" }}>
            AI-generated · Grounded in project findings · Not a substitute for manual review
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div
        className="w-52 shrink-0 p-4 space-y-5 overflow-y-auto"
        style={{ borderLeft: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-sidebar)" }}
      >
        <div>
          <div className="xm-section-label mb-2">Suggested Questions</div>
          <div className="space-y-1.5">
            {SUGGESTED.map(q => (
              <button
                key={q}
                onClick={() => send(q)}
                disabled={pending}
                className="w-full text-left text-xs p-2 rounded transition-colors"
                style={{ color: "var(--xm-tx-secondary)", border: "1px solid var(--xm-border)" }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-accent-border)"
                  ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)"
                  ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-accent-subtle)"
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)"
                  ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)"
                  ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        <div>
          <div className="xm-section-label mb-2">Issue Context</div>
          {selectedIssueSummary ? (
            <div className="space-y-1.5 text-xs">
              {([
                ["Issue", selectedIssueSummary.title],
                ["File", selectedIssueSummary.file ?? "—"],
                ["Line", selectedIssueSummary.line !== null ? String(selectedIssueSummary.line) : "—"],
                ["Rule", selectedIssueSummary.rule ?? "—"],
                ["Severity", selectedIssueSummary.severity],
                ["Risk", selectedIssueSummary.risk],
              ] as [string, string][]).map(([k, v]) => (
                <div key={k} className="flex items-start justify-between gap-2">
                  <span style={{ color: "var(--xm-tx-muted)" }} className="shrink-0">{k}</span>
                  <span
                    className="font-mono text-right"
                    style={{
                      color: k === "Severity" || k === "Risk"
                        ? severityColor(v)
                        : "var(--xm-tx-secondary)",
                    }}
                  >
                    {v}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs italic" style={{ color: "var(--xm-tx-muted)" }}>No issue selected</p>
          )}
        </div>
      </div>
    </div>
  )
}
