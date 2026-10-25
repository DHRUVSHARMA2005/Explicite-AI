import React, { useEffect, useRef, useState } from "react"
import { useNav } from "../App"
import { BookIcon, SparkleIcon, CheckIcon } from "../components/Icons"
import {
  apiStartTutorSession,
  apiTutorChat,
  apiCompleteResource,
  ApiError,
  type ApiTutorMessage,
} from "../lib/api"

const SUGGESTED_PROMPTS = [
  "Explain with an example",
  "Show me a code snippet",
  "What are common mistakes?",
  "Give me a practical exercise",
  "Quiz me on this topic",
  "Explain in simpler terms",
  "Show the secure fix",
]

function renderContent(text: string): React.ReactElement {
  const parts: React.ReactElement[] = []
  const re = /```(\w*)\n?([\s\S]*?)```/g
  let last = 0
  let match
  let key = 0

  while ((match = re.exec(text)) !== null) {
    if (match.index > last) {
      parts.push(<span key={key++} className="whitespace-pre-wrap">{text.slice(last, match.index)}</span>)
    }
    const lang = match[1] || "code"
    parts.push(
      <pre key={key++} className="code-block rounded p-3 my-2 overflow-x-auto text-xs leading-relaxed" data-lang={lang}>
        <div className="text-xs mb-1 font-mono" style={{ color: "var(--xm-tx-muted)" }}>{lang}</div>
        <code>{match[2]}</code>
      </pre>
    )
    last = match.index + match[0].length
  }
  if (last < text.length) parts.push(<span key={key++} className="whitespace-pre-wrap">{text.slice(last)}</span>)
  return <>{parts}</>
}

function tagStyle(tag: string | null | undefined): { color: string; bg: string } {
  if (tag === "Security") return { color: "var(--xm-err)", bg: "var(--xm-err-sub)" }
  if (tag === "Quality")  return { color: "var(--xm-info)", bg: "var(--xm-info-sub)" }
  return { color: "var(--xm-tx-muted)", bg: "var(--xm-bg-elevated)" }
}

export default function TutorSession() {
  const { token, selectedLearningResource, navigate, logout } = useNav()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ApiTutorMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [pending, setPending] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [completing, setCompleting] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const resource = selectedLearningResource

  useEffect(() => {
    if (!token || !resource) { navigate("learning"); return }
    let cancelled = false
    setLoading(true)
    setError(null)
    apiStartTutorSession(token, resource.id)
      .then(session => {
        if (cancelled) return
        setSessionId(session.session_id)
        setMessages(session.messages)
        setLoading(false)
        setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "auto" }), 50)
      })
      .catch(err => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) { logout(); return }
        setError(err instanceof Error ? err.message : "Failed to start tutor session")
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [resource?.id])

  const scrollBottom = () => setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50)

  async function send(text: string) {
    const trimmed = text.trim()
    if (!trimmed || pending || !sessionId || !token) return
    const optimisticUser: ApiTutorMessage = {
      id: "optimistic-" + Date.now(),
      session_id: sessionId,
      role: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, optimisticUser])
    setInput("")
    setPending(true)
    scrollBottom()
    try {
      const resp = await apiTutorChat(token, sessionId, trimmed)
      setMessages(prev => [
        ...prev.filter(m => m.id !== optimisticUser.id),
        { ...optimisticUser, id: "user-" + Date.now() },
        resp.message,
      ])
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) { logout(); return }
      let msg: string
      if (err instanceof ApiError && err.status === 503) {
        msg = "The AI tutor is not available. Check that your AI provider is configured (LLM_PROVIDER in .env)."
      } else if (err instanceof ApiError && err.status === 422) {
        msg = "Your message is too long (max 2000 characters). Please shorten it."
      } else {
        msg = err instanceof Error ? err.message : "Failed to get a response. Please try again."
      }
      setMessages(prev => [...prev, { id: "error-" + Date.now(), session_id: sessionId, role: "assistant", content: msg, created_at: new Date().toISOString() }])
    } finally { setPending(false); scrollBottom() }
  }

  async function handleComplete() {
    if (!token || !resource || completing || completed) return
    setCompleting(true)
    try {
      await apiCompleteResource(token, resource.id)
      setCompleted(true)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) logout()
    } finally { setCompleting(false) }
  }

  if (!resource) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <div className="text-sm text-center" style={{ color: "var(--xm-tx-muted)" }}>
          No learning resource selected.{" "}
          <button onClick={() => navigate("learning")} className="underline" style={{ color: "var(--xm-accent)" }}>
            Back to learning →
          </button>
        </div>
      </div>
    )
  }

  const ts = tagStyle(resource.tag)

  return (
    <div className="flex h-full overflow-hidden">
      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <div
          className="px-4 py-3 shrink-0"
          style={{ borderBottom: "1px solid var(--xm-border)", backgroundColor: "var(--xm-bg-elevated)" }}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 min-w-0">
              <button
                onClick={() => navigate("learning")}
                className="text-xs shrink-0 mt-0.5 transition-colors"
                style={{ color: "var(--xm-tx-muted)" }}
                onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
                onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)" }}
              >
                ← Back
              </button>
              <div className="min-w-0">
                <h2 className="text-sm font-semibold truncate" style={{ color: "var(--xm-tx-primary)" }}>{resource.title}</h2>
                <div className="flex items-center gap-2 mt-0.5 flex-wrap text-xs" style={{ color: "var(--xm-tx-muted)" }}>
                  <span>{resource.resource_type}</span>
                  {resource.duration_minutes && <><span>·</span><span>{resource.duration_minutes} min</span></>}
                  {resource.tag && (
                    <>
                      <span>·</span>
                      <span className="px-1.5 py-0.5 rounded font-medium" style={{ color: ts.color, backgroundColor: ts.bg }}>{resource.tag}</span>
                    </>
                  )}
                  {resource.related_issue_type && <><span>·</span><span>{resource.related_issue_type}</span></>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs px-1.5 py-0.5 rounded font-medium" style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}>
                AI Tutor
              </span>
              {completed ? (
                <span className="text-xs font-medium px-2 py-1 rounded" style={{ color: "var(--xm-ok)", backgroundColor: "var(--xm-ok-sub)", border: "1px solid color-mix(in srgb, var(--xm-ok) 40%, transparent)" }}>
                  ✓ Completed
                </span>
              ) : (
                <button
                  onClick={e => { e.stopPropagation(); handleComplete() }}
                  disabled={completing}
                  className="text-xs px-2 py-1 rounded transition-colors"
                  style={{ color: "var(--xm-tx-muted)", border: "1px solid var(--xm-border)" }}
                  onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-ok)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-ok)" }}
                  onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)" }}
                >
                  {completing ? "Saving…" : "Mark complete"}
                </button>
              )}
            </div>
          </div>
          {resource.description && (
            <p className="text-xs mt-2 pl-10" style={{ color: "var(--xm-tx-secondary)" }}>{resource.description}</p>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ backgroundColor: "var(--xm-bg-app)" }}>
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg rounded-bl-sm px-3.5 py-3 text-sm flex items-center gap-2" style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)", color: "var(--xm-tx-muted)" }}>
                <svg className="xm-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" aria-hidden>
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                Loading tutor session…
              </div>
            </div>
          )}
          {error && (
            <div className="rounded px-3 py-2 text-sm" style={{ backgroundColor: "var(--xm-warn-sub)", color: "var(--xm-warn)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }}>
              {error}
            </div>
          )}
          {!loading && messages.length === 0 && !error && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg rounded-bl-sm overflow-hidden" style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }}>
                <div className="px-3.5 pt-2.5 pb-1.5 flex items-center gap-1.5" style={{ borderBottom: "1px solid var(--xm-border-sub)" }}>
                  <span className="text-xs font-medium" style={{ color: "var(--xm-tx-muted)" }}>AI Tutor · {resource.title}</span>
                  <span className="text-xs px-1 py-0.5 rounded" style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}>AI-generated</span>
                </div>
                <div className="px-3.5 py-2.5 text-sm" style={{ color: "var(--xm-tx-secondary)" }}>
                  <p>Welcome! I am your AI tutor for <strong style={{ color: "var(--xm-tx-primary)" }}>{resource.title}</strong>.</p>
                  <p className="mt-2">
                    {resource.description
                      ? `${resource.description} Ask me anything — I can explain concepts, show code examples, and quiz you.`
                      : "Ask me anything about this topic — I can explain concepts, show code examples, and quiz you."}
                  </p>
                  <p className="mt-2 text-xs italic" style={{ color: "var(--xm-tx-muted)" }}>
                    Responses are AI-generated and should be verified against authoritative sources.
                  </p>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, i) => {
            const isUser = msg.role === "user"
            const isError = msg.id.startsWith("error-")
            return (
              <div key={msg.id ?? i} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-lg text-sm leading-relaxed ${isUser ? "rounded-br-sm px-3.5 py-2.5 text-white" : "rounded-bl-sm overflow-hidden"}`}
                  style={isUser
                    ? { backgroundColor: "var(--xm-accent)" }
                    : isError
                    ? { backgroundColor: "var(--xm-warn-sub)", border: "1px solid color-mix(in srgb, var(--xm-warn) 40%, transparent)" }
                    : { backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)" }
                  }
                >
                  {!isUser && (
                    <div className="px-3.5 pt-2.5 pb-1.5 flex items-center gap-1.5" style={{ borderBottom: "1px solid var(--xm-border-sub)" }}>
                      <span className="text-xs font-medium" style={{ color: "var(--xm-tx-muted)" }}>AI Tutor · {resource.title}</span>
                      {!isError && (
                        <span className="text-xs px-1 py-0.5 rounded" style={{ color: "var(--xm-info)", backgroundColor: "var(--xm-info-sub)" }}>AI-generated</span>
                      )}
                    </div>
                  )}
                  <div className={`${!isUser ? "px-3.5 py-2.5" : ""}`} style={!isUser ? { color: "var(--xm-tx-secondary)" } : {}}>
                    {isUser ? msg.content : renderContent(msg.content)}
                  </div>
                </div>
              </div>
            )
          })}

          {pending && (
            <div className="flex justify-start">
              <div className="rounded-lg rounded-bl-sm px-3.5 py-3 text-sm flex items-center gap-2" style={{ backgroundColor: "var(--xm-bg-surface)", border: "1px solid var(--xm-border)", color: "var(--xm-tx-muted)" }}>
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
          <div className="flex gap-2 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input) } }}
              placeholder="Ask a question… (Enter to send, Shift+Enter for new line)"
              disabled={pending || loading}
              rows={2}
              className="xm-input flex-1 resize-none"
            />
            <button
              onClick={() => send(input)}
              disabled={pending || loading || !input.trim()}
              className="xm-btn xm-btn-primary self-end"
            >
              {pending ? "…" : "Send"}
            </button>
          </div>
          <p className="text-xs mt-1.5" style={{ color: "var(--xm-tx-muted)" }}>
            AI-generated · Responses may not be authoritative · Verify before applying
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
            {SUGGESTED_PROMPTS.map(q => (
              <button
                key={q}
                onClick={() => send(q)}
                disabled={pending || loading}
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
          <div className="xm-section-label mb-2">Resource Info</div>
          <div className="space-y-1.5 text-xs">
            {[
              ["Type", resource.resource_type],
              ["Duration", resource.duration_minutes ? `${resource.duration_minutes} min` : "—"],
              ["Category", resource.tag ?? "—"],
              ["Issue type", resource.related_issue_type ?? "—"],
              ["Rule", resource.related_rule_key ?? "—"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-start justify-between gap-2">
                <span className="shrink-0" style={{ color: "var(--xm-tx-muted)" }}>{k}</span>
                <span className="font-mono text-right truncate max-w-[7rem]" style={{ color: "var(--xm-tx-secondary)" }}>{v}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="xm-section-label mb-2">Actions</div>
          <div className="space-y-1.5">
            <button
              onClick={() => navigate("learning")}
              className="w-full text-left text-xs p-2 rounded transition-colors"
              style={{ color: "var(--xm-tx-secondary)", border: "1px solid var(--xm-border)" }}
              onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-accent-border)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
              onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)" }}
            >
              ← Back to Learning
            </button>
            {!completed && (
              <button
                onClick={handleComplete}
                disabled={completing}
                className="w-full text-left text-xs p-2 rounded transition-colors"
                style={{ color: "var(--xm-tx-secondary)", border: "1px solid var(--xm-border)" }}
                onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-ok)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-ok)" }}
                onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--xm-border)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)" }}
              >
                {completing ? "Saving…" : "✓ Mark as Complete"}
              </button>
            )}
            {completed && (
              <div className="text-xs font-medium p-2 rounded" style={{ color: "var(--xm-ok)", backgroundColor: "var(--xm-ok-sub)", border: "1px solid color-mix(in srgb, var(--xm-ok) 40%, transparent)" }}>
                ✓ Completed
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
