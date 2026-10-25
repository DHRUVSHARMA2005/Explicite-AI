"""
Git repository retrieval service.

Supports cloning public HTTPS repositories for static analysis.

Security measures:
- Only HTTPS URLs accepted; http://, ssh://, git://, file:// all rejected
- SSRF protection: DNS resolution at validation time; RFC 1918, loopback,
  link-local and other non-routable IPs blocked
  ** Known limitation: DNS rebinding — the IP validated here may differ from
     the IP git uses at connection time.  For stronger isolation, run the
     server behind an egress firewall that blocks RFC 1918 ranges.
- URL credentials (userinfo) rejected
- Branch names validated against a strict allowlist pattern
- git clone run as subprocess with a fixed argument list (never shell=True)
- GIT_TERMINAL_PROMPT=0 prevents git from prompting for credentials
- .git/ removed after clone (reduces disk usage and attack surface)
- Workspace cleaned up on any error
- Source files from the cloned repo are never executed
"""
import ipaddress
import logging
import os
import re
import shutil
import socket
import subprocess
import urllib.parse
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

_ALLOWED_SCHEMES = frozenset({"https"})

# Hostnames that should never reach the network
_LOCALHOST_NAMES = frozenset({
    "localhost", "ip6-localhost", "ip6-loopback", "broadcasthost",
})

# Non-routable / private networks to block (SSRF protection)
_BLOCKED_NETWORKS: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network("0.0.0.0/8"),       # "this" network
    ipaddress.ip_network("10.0.0.0/8"),      # RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),   # shared address space
    ipaddress.ip_network("127.0.0.0/8"),     # loopback
    ipaddress.ip_network("169.254.0.0/16"),  # link-local
    ipaddress.ip_network("172.16.0.0/12"),   # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),    # IETF protocol
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),   # benchmark testing
    ipaddress.ip_network("198.51.100.0/24"), # documentation TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # documentation TEST-NET-3
    ipaddress.ip_network("240.0.0.0/4"),     # reserved
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),        # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
    ipaddress.ip_network("::ffff:0:0/96"),   # IPv4-mapped (re-checked below)
]

# Branch name: must start with alphanumeric, then allow . - _ / alphanumeric
_BRANCH_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._\-/]*$")
# SHA-40 pattern
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

_MAX_URL_LEN = 500
_MAX_BRANCH_LEN = 255


# ── Exceptions ─────────────────────────────────────────────────────────────────

class GitServiceError(Exception):
    """Base class for all git service errors."""


class GitUrlError(GitServiceError):
    """URL or branch failed validation."""


class GitCloneError(GitServiceError):
    """git clone subprocess returned a non-zero exit code."""


class GitTimeoutError(GitServiceError):
    """git clone timed out."""


class GitRepoTooLargeError(GitServiceError):
    """Cloned repository exceeds size or file-count limits."""


# ── Internal helpers ───────────────────────────────────────────────────────────

def _is_private_ip(addr_str: str) -> bool:
    """Return True when the address is private, loopback, or otherwise blocked."""
    try:
        addr = ipaddress.ip_address(addr_str)
    except ValueError:
        return True  # unparseable → block
    # Unwrap IPv4-mapped IPv6 (e.g. ::ffff:10.0.0.1)
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    return any(addr in net for net in _BLOCKED_NETWORKS)


def _sanitize_git_error(stderr: str) -> str:
    """Return a user-facing error message from git stderr, stripping internal paths."""
    s = stderr.lower()
    if "not found" in s or "unknown revision" in s or "invalid refspec" in s:
        return "Branch not found or repository has no matching branch"
    if "could not read" in s or "repository" in s and "not" in s:
        return "Repository not found or not publicly accessible"
    if "authentication" in s or " 403" in s or " 401" in s or "access denied" in s:
        return "Repository requires authentication; only public repositories are supported"
    if "timeout" in s or "timed out" in s:
        return "Repository connection timed out"
    if "ssl" in s or "certificate" in s:
        return "TLS/SSL error connecting to repository"
    # Generic fallback: truncate and redact filesystem paths
    safe = re.sub(r"/[^\s]*", "<path>", stderr)
    return f"Clone failed: {safe[:200]}"


# ── Public API ─────────────────────────────────────────────────────────────────

def validate_repo_url(url: str) -> str:
    """
    Validate and normalise a public HTTPS Git repository URL.

    Returns the canonicalised URL string on success.
    Raises GitUrlError on any violation.
    """
    if not url or not isinstance(url, str):
        raise GitUrlError("Repository URL is required")

    url = url.strip()

    if len(url) > _MAX_URL_LEN:
        raise GitUrlError(f"Repository URL exceeds {_MAX_URL_LEN} character limit")

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        raise GitUrlError("Malformed repository URL")

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise GitUrlError(
            f"Unsupported URL scheme '{parsed.scheme}'; only HTTPS is permitted"
        )

    if not parsed.netloc:
        raise GitUrlError("Repository URL has no hostname")

    # Credentials embedded in URL are not permitted
    if parsed.username or parsed.password:
        raise GitUrlError("Credentials in the repository URL are not permitted")

    hostname = parsed.hostname
    if not hostname:
        raise GitUrlError("Repository URL has no resolvable hostname")

    # Reject well-known localhost aliases without DNS lookup
    if hostname.lower() in _LOCALHOST_NAMES:
        raise GitUrlError("Repository host is not accessible from this server")

    # If the hostname is an IP literal, validate directly without DNS
    try:
        ip_literal = ipaddress.ip_address(hostname)
        if _is_private_ip(str(ip_literal)):
            raise GitUrlError("Repository host is a private or reserved IP address")
        # Allow public IP literals to proceed
    except ValueError:
        # Not an IP literal — resolve via DNS
        try:
            addr_infos = socket.getaddrinfo(
                hostname, 443, proto=socket.IPPROTO_TCP
            )
        except socket.gaierror:
            raise GitUrlError(f"Cannot resolve repository host '{hostname}'")

        if not addr_infos:
            raise GitUrlError(f"Repository host '{hostname}' returned no addresses")

        for info in addr_infos:
            ip_str = info[4][0]
            if _is_private_ip(ip_str):
                raise GitUrlError(
                    "Repository host resolves to a private or reserved address"
                )

    # Reconstruct a clean URL (strip query string, fragment, trailing slash)
    path = parsed.path.rstrip("/") or "/"
    clean = urllib.parse.urlunparse(("https", parsed.netloc, path, "", "", ""))
    return clean


def validate_branch(branch: str) -> str:
    """
    Validate and return a branch name.
    Raises GitUrlError on any violation.
    """
    if not branch or not isinstance(branch, str):
        raise GitUrlError("Branch name is required")

    branch = branch.strip()

    if not branch:
        raise GitUrlError("Branch name must not be empty")

    if len(branch) > _MAX_BRANCH_LEN:
        raise GitUrlError(f"Branch name exceeds {_MAX_BRANCH_LEN} character limit")

    if branch.startswith("-"):
        raise GitUrlError("Branch name may not start with a hyphen")

    if branch.startswith("."):
        raise GitUrlError("Branch name may not start with a period")

    if ".." in branch:
        raise GitUrlError("Branch name may not contain '..'")

    if branch.endswith("."):
        raise GitUrlError("Branch name may not end with a period")

    if branch.endswith(".lock"):
        raise GitUrlError("Branch name may not end with '.lock'")

    if "@{" in branch or "\\" in branch or " " in branch:
        raise GitUrlError("Branch name contains invalid characters")

    if not _BRANCH_RE.match(branch):
        raise GitUrlError(
            "Branch name contains invalid characters "
            "(allowed: letters, digits, '.', '-', '_', '/')"
        )

    return branch


def find_git() -> str:
    """Return path to the git executable or raise GitServiceError."""
    exe = shutil.which("git")
    if exe is None:
        raise GitServiceError(
            "git is not installed or not on PATH. "
            "Install git to enable repository analysis."
        )
    return exe


def get_git_version() -> str:
    """Return the installed git version string."""
    exe = find_git()
    result = subprocess.run(
        [exe, "--version"],
        capture_output=True, text=True, timeout=10, shell=False,
    )
    return result.stdout.strip() or "unknown"


def _resolve_commit_sha(clone_dir: Path, git: str) -> str:
    """Return the HEAD commit SHA from the cloned repo (requires .git present)."""
    try:
        result = subprocess.run(
            [git, "-C", str(clone_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, shell=False,
        )
        sha = result.stdout.strip()
        if result.returncode == 0 and _SHA_RE.match(sha):
            return sha
    except Exception:
        pass
    return "unknown"


def _measure_workspace(directory: Path) -> tuple[int, int]:
    """Return (file_count, total_bytes) for all files under directory."""
    count = 0
    total = 0
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            try:
                total += (Path(dirpath) / fname).stat().st_size
            except OSError:
                pass
            count += 1
    return count, total


def clone_repository(
    repo_url: str,
    branch: str,
    dest_dir: Path,
    timeout_seconds: int = 120,
    max_mb: int = 100,
    max_files: int = 5000,
) -> str:
    """
    Clone a repository at the specified branch into dest_dir (which must not exist).

    Returns the resolved HEAD commit SHA (40-char hex, or "unknown").
    Raises GitServiceError subclasses on failure; dest_dir is removed on error.

    Security:
    - Never uses shell=True; URL and branch are separate argv elements
    - GIT_TERMINAL_PROMPT=0 prevents interactive credential prompts
    - .git/ removed after clone; source code is never executed
    - Size and file-count limits enforced after clone
    """
    git = find_git()

    if dest_dir.exists():
        raise GitServiceError(f"Destination already exists: {dest_dir}")

    # The '--' end-of-options marker separates git flags from URL/dest arguments.
    cmd = [
        git, "clone",
        "--depth", "1",
        "--branch", branch,
        "--single-branch",
        "--no-tags",
        "--",
        repo_url,
        str(dest_dir),
    ]

    logger.info("git clone %s@%s → %s", repo_url, branch, dest_dir)

    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise GitTimeoutError(
            f"git clone timed out after {timeout_seconds}s; "
            "the repository may be too large or the host unreachable"
        )
    except FileNotFoundError:
        raise GitServiceError("git executable not found; is git installed?")

    if result.returncode != 0:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise GitCloneError(_sanitize_git_error(result.stderr.strip()))

    # Resolve commit SHA before removing .git
    commit_sha = _resolve_commit_sha(dest_dir, git)

    # Remove .git — not needed for analysis, reduces attack surface and disk use
    git_dir = dest_dir / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    # Enforce post-clone limits
    file_count, total_bytes = _measure_workspace(dest_dir)
    total_mb = total_bytes / (1024 * 1024)

    if file_count > max_files:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise GitRepoTooLargeError(
            f"Repository contains {file_count} files; limit is {max_files}"
        )

    if total_mb > max_mb:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise GitRepoTooLargeError(
            f"Repository source is {total_mb:.0f} MB; limit is {max_mb} MB"
        )

    logger.info(
        "Cloned %s@%s → SHA %s (%d files, %.1f MB)",
        repo_url, branch, commit_sha, file_count, total_mb,
    )
    return commit_sha
