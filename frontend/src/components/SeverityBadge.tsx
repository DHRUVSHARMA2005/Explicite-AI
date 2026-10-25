interface Props {
  severity: string
  size?: "sm" | "md"
}

const styles: Record<string, { bg: string; text: string; dot: string }> = {
  Critical: {
    bg:   "bg-[var(--xm-critical-bg)]",
    text: "text-[var(--xm-critical)]",
    dot:  "bg-[var(--xm-critical)]",
  },
  High: {
    bg:   "bg-[var(--xm-high-bg)]",
    text: "text-[var(--xm-high)]",
    dot:  "bg-[var(--xm-high)]",
  },
  Medium: {
    bg:   "bg-[var(--xm-medium-bg)]",
    text: "text-[var(--xm-medium)]",
    dot:  "bg-[var(--xm-medium)]",
  },
  Low: {
    bg:   "bg-[var(--xm-low-bg)]",
    text: "text-[var(--xm-low)]",
    dot:  "bg-[var(--xm-low)]",
  },
}

const fallback = {
  bg:   "bg-[var(--xm-bg-elevated)]",
  text: "text-[var(--xm-tx-muted)]",
  dot:  "bg-[var(--xm-tx-muted)]",
}

export default function SeverityBadge({ severity, size = "sm" }: Props) {
  const s = styles[severity] ?? fallback
  const px = size === "md" ? "px-2.5 py-1" : "px-2 py-0.5"
  const fs = size === "md" ? "text-xs" : "text-[11px]"
  return (
    <span className={`inline-flex items-center gap-1.5 ${px} rounded ${fs} font-semibold tracking-wide ${s.bg} ${s.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${s.dot}`} />
      {severity}
    </span>
  )
}
