import { useNav, type Screen } from "../App"
import {
  DashboardIcon,
  IssuesIcon,
  ChatIcon,
  CodeIcon,
  FolderIcon,
  BookIcon,
  SettingsIcon,
  AnalyzeIcon,
  UserIcon,
  LogOutIcon,
  SparkleIcon,
} from "./Icons"

interface NavGroup {
  label: string
  items: { label: string; screen: Screen; Icon: React.FC<{ className?: string }>; desc?: string }[]
}

const groups: NavGroup[] = [
  {
    label: "Workspace",
    items: [
      { label: "Dashboard",      screen: "dashboard",     Icon: DashboardIcon,  desc: "Project overview" },
      { label: "Projects",       screen: "projects",      Icon: FolderIcon,     desc: "All projects" },
      { label: "Code Analysis",  screen: "code-analysis", Icon: AnalyzeIcon,    desc: "Run analysis" },
    ],
  },
  {
    label: "Development",
    items: [
      { label: "Findings",       screen: "issues",        Icon: IssuesIcon,     desc: "All findings" },
      { label: "AI Assistant",   screen: "ai-assistant",  Icon: ChatIcon,       desc: "Ask about issues" },
      { label: "Learning",       screen: "learning",      Icon: BookIcon,       desc: "Security learning" },
    ],
  },
  {
    label: "Account",
    items: [
      { label: "Settings",       screen: "settings",      Icon: SettingsIcon,   desc: "Preferences" },
    ],
  },
]

const issueScreens: Screen[] = ["issue-detail", "suggested-fix"]
const tutorScreen: Screen[]  = ["tutor"]

function isActive(screen: Screen, target: Screen): boolean {
  if (target === "issues" && issueScreens.includes(screen)) return true
  if (target === "learning" && tutorScreen.includes(screen)) return true
  return screen === target
}

function initials(name: string): string {
  return name.split(" ").map(w => w[0] ?? "").join("").slice(0, 2).toUpperCase()
}

export default function Sidebar() {
  const { screen, navigate, currentUser, logout } = useNav()

  return (
    <aside
      className="w-56 shrink-0 flex flex-col overflow-hidden"
      style={{
        backgroundColor: "var(--xm-bg-sidebar)",
        borderRight: "1px solid var(--xm-border)",
      }}
    >
      {/* Brand */}
      <div
        className="px-4 py-4 shrink-0"
        style={{ borderBottom: "1px solid var(--xm-border)" }}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="w-7 h-7 rounded flex items-center justify-center shrink-0"
            style={{ backgroundColor: "var(--xm-accent)" }}
          >
            <CodeIcon className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold tracking-tight" style={{ color: "var(--xm-tx-primary)" }}>
              Explicite AI
            </div>
            <div className="text-[10px] font-medium" style={{ color: "var(--xm-tx-muted)" }}>
              Code Intelligence
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3" aria-label="Main navigation">
        {groups.map(group => (
          <div key={group.label} className="mb-1">
            <div
              className="px-4 py-1.5 text-[10px] font-semibold tracking-widest uppercase xm-section-label"
            >
              {group.label}
            </div>
            {group.items.map(({ label, screen: s, Icon }) => {
              const active = isActive(screen, s)
              return (
                <button
                  key={s}
                  onClick={() => navigate(s)}
                  title={label}
                  aria-current={active ? "page" : undefined}
                  className="w-full text-left flex items-center gap-2.5 px-4 py-2 text-sm transition-colors relative focus-visible:outline-none"
                  style={{
                    color: active ? "var(--xm-accent)" : "var(--xm-tx-secondary)",
                    backgroundColor: active ? "var(--xm-accent-subtle)" : "transparent",
                    fontWeight: active ? "500" : "400",
                  }}
                  onMouseEnter={e => {
                    if (!active) {
                      (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-bg-hover)"
                      ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-primary)"
                    }
                  }}
                  onMouseLeave={e => {
                    if (!active) {
                      (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
                      ;(e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-secondary)"
                    }
                  }}
                >
                  {active && (
                    <span
                      className="absolute left-0 top-1 bottom-1 w-0.5 rounded-r"
                      style={{ backgroundColor: "var(--xm-accent)" }}
                    />
                  )}
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="truncate">{label}</span>
                </button>
              )
            })}
          </div>
        ))}
      </nav>

      {/* User section */}
      {currentUser && (
        <div
          className="shrink-0 px-3 py-3"
          style={{ borderTop: "1px solid var(--xm-border)" }}
        >
          <div className="flex items-center gap-2.5 mb-2">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold text-white select-none"
              style={{ backgroundColor: "var(--xm-accent)" }}
            >
              {initials(currentUser.full_name)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium truncate" style={{ color: "var(--xm-tx-primary)" }}>
                {currentUser.full_name}
              </div>
              <div className="text-[10px] truncate" style={{ color: "var(--xm-tx-muted)" }}>
                {currentUser.system_role === "system_admin" ? "Admin" : "Developer"}
              </div>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors"
            style={{ color: "var(--xm-tx-muted)" }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-err)"
              ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--xm-err-sub)"
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)"
              ;(e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent"
            }}
          >
            <LogOutIcon className="w-3.5 h-3.5 shrink-0" />
            Sign out
          </button>
        </div>
      )}
    </aside>
  )
}
