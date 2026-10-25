import { createContext, useContext, useEffect, useState } from "react"
import Sidebar from "./components/Sidebar"
import Login from "./screens/Login"
import Dashboard from "./screens/Dashboard"
import Issues from "./screens/Issues"
import IssueDetail from "./screens/IssueDetail"
import AIAssistant from "./screens/AIAssistant"
import SuggestedFix from "./screens/SuggestedFix"
import CodeAnalysis from "./screens/CodeAnalysis"
import Learning from "./screens/Learning"
import TutorSession from "./screens/TutorSession"
import Projects from "./screens/Projects"
import Settings from "./screens/Settings"
import { type UserPublic, type ApiIssueSummary, type UserPreferences, type ApiLearningResource, DEFAULT_PREFERENCES, getStoredToken, storeToken, clearToken } from "./lib/api"
import { applyAppearance, loadAppearance } from "./lib/appearance"
import { CodeIcon, FolderIcon, ChevronRightIcon } from "./components/Icons"

export type Screen =
  | "login"
  | "dashboard"
  | "issues"
  | "issue-detail"
  | "ai-assistant"
  | "suggested-fix"
  | "code-analysis"
  | "learning"
  | "tutor"
  | "projects"
  | "settings"

interface NavState {
  screen: Screen
  navigate: (s: Screen) => void
  token: string | null
  currentUser: UserPublic | null
  login: (token: string, user: UserPublic) => void
  logout: () => void
  selectedProjectId: string | null
  selectedProjectName: string | null
  openProject: (id: string, name: string) => void
  selectedIssueId: string | null
  selectedIssueSummary: ApiIssueSummary | null
  openIssue: (id: string, summary?: ApiIssueSummary) => void
  selectedFixId: string | null
  openFix: (fixId: string) => void
  updateCurrentUser: (user: UserPublic) => void
  preferences: UserPreferences
  selectedLearningResource: ApiLearningResource | null
  openTutor: (resource: ApiLearningResource) => void
}

export const NavCtx = createContext<NavState>({
  screen: "login",
  navigate: () => {},
  token: null,
  currentUser: null,
  login: () => {},
  logout: () => {},
  selectedProjectId: null,
  selectedProjectName: null,
  openProject: () => {},
  selectedIssueId: null,
  selectedIssueSummary: null,
  openIssue: () => {},
  selectedFixId: null,
  openFix: () => {},
  updateCurrentUser: () => {},
  preferences: DEFAULT_PREFERENCES,
  selectedLearningResource: null,
  openTutor: () => {},
})
export const useNav = () => useContext(NavCtx)

const SCREEN_TITLES: Partial<Record<Screen, string>> = {
  dashboard:     "Dashboard",
  issues:        "Findings",
  "issue-detail":"Issue Detail",
  "ai-assistant":"AI Assistant",
  "suggested-fix":"Suggested Fix",
  "code-analysis":"Code Analysis",
  learning:      "Learning",
  tutor:         "AI Tutor",
  projects:      "Projects",
  settings:      "Settings",
}

function TopBar({ screen, projectName, navigate }: {
  screen: Screen
  projectName: string | null
  navigate: (s: Screen) => void
}) {
  const title = SCREEN_TITLES[screen] ?? screen
  const showProjectCrumb = projectName && ["dashboard","issues","issue-detail","ai-assistant","suggested-fix","code-analysis"].includes(screen)

  return (
    <header
      className="h-11 shrink-0 flex items-center px-5 gap-2"
      style={{
        backgroundColor: "var(--xm-bg-sidebar)",
        borderBottom: "1px solid var(--xm-border)",
      }}
    >
      {showProjectCrumb ? (
        <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs">
          <button
            onClick={() => navigate("projects")}
            className="transition-colors"
            style={{ color: "var(--xm-tx-muted)" }}
            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-accent)" }}
            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = "var(--xm-tx-muted)" }}
          >
            {projectName}
          </button>
          <ChevronRightIcon className="w-3 h-3" style={{ color: "var(--xm-tx-muted)" } as React.CSSProperties} />
          <span className="font-medium" style={{ color: "var(--xm-tx-primary)" }}>{title}</span>
        </nav>
      ) : (
        <span className="text-sm font-medium" style={{ color: "var(--xm-tx-primary)" }}>{title}</span>
      )}
    </header>
  )
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("login")
  const [token, setToken] = useState<string | null>(getStoredToken)
  const [currentUser, setCurrentUser] = useState<UserPublic | null>(null)

  useEffect(() => { applyAppearance(loadAppearance()) }, [])

  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [selectedProjectName, setSelectedProjectName] = useState<string | null>(null)
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null)
  const [selectedIssueSummary, setSelectedIssueSummary] = useState<ApiIssueSummary | null>(null)
  const [selectedFixId, setSelectedFixId] = useState<string | null>(null)
  const [selectedLearningResource, setSelectedLearningResource] = useState<ApiLearningResource | null>(null)

  function login(newToken: string, user: UserPublic) {
    storeToken(newToken)
    setToken(newToken)
    setCurrentUser(user)
    setScreen("projects")
  }

  function logout() {
    clearToken()
    setToken(null)
    setCurrentUser(null)
    setSelectedProjectId(null)
    setSelectedProjectName(null)
    setSelectedIssueId(null)
    setSelectedIssueSummary(null)
    setSelectedFixId(null)
    setScreen("login")
  }

  function openProject(id: string, name: string) {
    setSelectedProjectId(id)
    setSelectedProjectName(name)
    setScreen("dashboard")
  }

  function openIssue(id: string, summary?: ApiIssueSummary) {
    setSelectedIssueId(id)
    setSelectedIssueSummary(summary ?? null)
    setScreen("issue-detail")
  }

  function openFix(fixId: string) {
    setSelectedFixId(fixId)
    setScreen("suggested-fix")
  }

  function openTutor(resource: ApiLearningResource) {
    setSelectedLearningResource(resource)
    setScreen("tutor")
  }

  function updateCurrentUser(user: UserPublic) {
    setCurrentUser(user)
  }

  const ctx: NavState = {
    screen,
    navigate: setScreen,
    token,
    currentUser,
    login,
    logout,
    selectedProjectId,
    selectedProjectName,
    openProject,
    selectedIssueId,
    selectedIssueSummary,
    openIssue,
    selectedFixId,
    openFix,
    updateCurrentUser,
    preferences: currentUser?.preferences ?? DEFAULT_PREFERENCES,
    selectedLearningResource,
    openTutor,
  }

  if (screen === "login") {
    return (
      <NavCtx.Provider value={ctx}>
        <Login />
      </NavCtx.Provider>
    )
  }

  return (
    <NavCtx.Provider value={ctx}>
      <div className="flex h-full overflow-hidden" style={{ backgroundColor: "var(--xm-bg-app)" }}>
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar screen={screen} projectName={selectedProjectName} navigate={setScreen} />
          <main className="flex-1 overflow-y-auto" style={{ backgroundColor: "var(--xm-bg-app)" }}>
            {screen === "dashboard"     && <Dashboard />}
            {screen === "issues"        && <Issues />}
            {screen === "issue-detail"  && <IssueDetail />}
            {screen === "ai-assistant"  && <AIAssistant />}
            {screen === "suggested-fix" && <SuggestedFix />}
            {screen === "code-analysis" && <CodeAnalysis />}
            {screen === "learning"      && <Learning />}
            {screen === "tutor"         && <TutorSession />}
            {screen === "projects"      && <Projects />}
            {screen === "settings"      && <Settings />}
          </main>
        </div>
      </div>
    </NavCtx.Provider>
  )
}
