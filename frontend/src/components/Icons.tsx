interface IconProps { className?: string }

export function DashboardIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <rect x="1.5" y="1.5" width="5" height="5" rx="1"/>
      <rect x="9.5" y="1.5" width="5" height="5" rx="1"/>
      <rect x="1.5" y="9.5" width="5" height="5" rx="1"/>
      <rect x="9.5" y="9.5" width="5" height="5" rx="1"/>
    </svg>
  )
}

export function IssuesIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="8" cy="8" r="6"/>
      <line x1="8" y1="5" x2="8" y2="8.5"/>
      <circle cx="8" cy="11" r="0.7" fill="currentColor" stroke="none"/>
    </svg>
  )
}

export function ChatIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M14 1.5H2a.5.5 0 00-.5.5v8a.5.5 0 00.5.5h3v3l3-3h6a.5.5 0 00.5-.5V2a.5.5 0 00-.5-.5z" strokeLinejoin="round"/>
    </svg>
  )
}

export function CodeIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <polyline points="5,4 1,8 5,12"/>
      <polyline points="11,4 15,8 11,12"/>
      <line x1="9.5" y1="2.5" x2="6.5" y2="13.5"/>
    </svg>
  )
}

export function FolderIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M1.5 4.5h4l1.5-2h7.5a.5.5 0 01.5.5v9a.5.5 0 01-.5.5h-13a.5.5 0 01-.5-.5V5a.5.5 0 01.5-.5z" strokeLinejoin="round"/>
    </svg>
  )
}

export function BookIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M3 2h7l2 2v10H3z" strokeLinejoin="round"/>
      <line x1="5" y1="6" x2="10" y2="6"/>
      <line x1="5" y1="8.5" x2="10" y2="8.5"/>
      <line x1="5" y1="11" x2="8" y2="11"/>
    </svg>
  )
}

export function SettingsIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="8" cy="8" r="2"/>
      <path d="M8 1.5v1.2M8 13.3V14.5M1.5 8h1.2M13.3 8h1.2M3.3 3.3l.85.85M11.85 11.85l.85.85M3.3 12.7l.85-.85M11.85 4.15l.85-.85"/>
    </svg>
  )
}

export function ChevronRightIcon({ className = "w-3 h-3" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={2} className={className} aria-hidden>
      <polyline points="5,2 11,8 5,14"/>
    </svg>
  )
}

export function ShieldIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M8 1.5L2 4v4c0 3.5 2.5 5.5 6 6.5C12 13.5 14 11.5 14 8V4L8 1.5z" strokeLinejoin="round"/>
    </svg>
  )
}

export function BugIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="8" cy="9" r="4"/>
      <path d="M5.5 5L4 3.5M10.5 5L12 3.5M4 9H1.5M14.5 9H12M8 5V2.5"/>
    </svg>
  )
}

export function GitBranchIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="4" cy="3.5" r="1.5"/>
      <circle cx="4" cy="12.5" r="1.5"/>
      <circle cx="12" cy="3.5" r="1.5"/>
      <line x1="4" y1="5" x2="4" y2="11"/>
      <path d="M12 5c0 4-8 4-8 7.5"/>
    </svg>
  )
}

export function ClockIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="8" cy="8" r="6"/>
      <path d="M8 4.5V8l2.5 2.5"/>
    </svg>
  )
}

export function CheckIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={2} className={className} aria-hidden>
      <polyline points="2.5,8 6,11.5 13.5,4"/>
    </svg>
  )
}

export function XIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={2} className={className} aria-hidden>
      <line x1="3" y1="3" x2="13" y2="13"/>
      <line x1="13" y1="3" x2="3" y2="13"/>
    </svg>
  )
}

export function UploadIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M8 1.5L5 4.5M8 1.5L11 4.5M8 1.5V10"/>
      <path d="M2.5 10.5v3a.5.5 0 00.5.5h10a.5.5 0 00.5-.5v-3"/>
    </svg>
  )
}

export function SparkleIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" className={className} aria-hidden>
      <path d="M8 1c.4 2.8 1.7 4 4 4.3-2.3.3-3.6 1.6-4 4-.4-2.4-1.8-3.7-4-4 2.2-.3 3.6-1.5 4-4.3z"/>
      <path d="M3 1c.2 1.4.8 2 2 2.1-1.2.1-1.8.8-2 2-.2-1.2-.9-1.9-2-2 1.1-.1 1.8-.7 2-2.1z" opacity=".5"/>
    </svg>
  )
}

export function AnalyzeIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="6.5" cy="6.5" r="4"/>
      <line x1="9.6" y1="9.6" x2="14" y2="14"/>
      <line x1="4.5" y1="6.5" x2="8.5" y2="6.5"/>
      <line x1="6.5" y1="4.5" x2="6.5" y2="8.5"/>
    </svg>
  )
}

export function UserIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <circle cx="8" cy="5.5" r="2.5"/>
      <path d="M2 14c0-3 2.7-5 6-5s6 2 6 5"/>
    </svg>
  )
}

export function LogOutIcon({ className = "w-4 h-4" }: IconProps) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.5} className={className} aria-hidden>
      <path d="M6 2.5H2.5a.5.5 0 00-.5.5v10a.5.5 0 00.5.5H6"/>
      <path d="M11 5l3 3-3 3M14 8H6"/>
    </svg>
  )
}
