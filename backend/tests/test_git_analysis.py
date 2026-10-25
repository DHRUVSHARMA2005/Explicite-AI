"""
Tests for Git repository analysis (Phase M.1).

Coverage:
- URL validation: valid HTTPS, bad schemes, private IPs, credentials, malformed
- Branch validation: valid names, leading dash, '..', empty, invalid chars
- API endpoint: auth, role, 202 on valid request, 422 on bad input
- Background job: successful clone → analysis, clone failure, timeout, size limit
- Metadata persistence: repo_url, source_branch, source_revision saved
- SSRF: localhost, 127.x, 10.x, 172.16.x, 192.168.x rejected
- Existing ZIP upload endpoint unaffected

External network calls are mocked throughout.
"""
import asyncio
import io
import uuid
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import create_access_token, hash_password
from app.database import init_db
from app.main import app
from app.models.analysis import AnalysisJob
from app.models.project import Project, ProjectMembership
from app.models.user import User
from app.services.git_service import (
    GitCloneError,
    GitRepoTooLargeError,
    GitTimeoutError,
    GitUrlError,
    validate_branch,
    validate_repo_url,
)

_TEST_DB_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL.replace(
    "/explicite_ai", "/test_explicite_ai"
)


# ── URL validation unit tests ─────────────────────────────────────────────────

class TestValidateRepoUrl:
    """Pure validation — no network or DB access."""

    def _patched(self, url: str):
        """Call validate_repo_url with DNS resolution mocked to return a public IP."""
        with patch("app.services.git_service.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("1.2.3.4", 443))]
            return validate_repo_url(url)

    def test_valid_https_github(self):
        result = self._patched("https://github.com/owner/repo")
        assert result.startswith("https://github.com")

    def test_normalises_trailing_slash(self):
        result = self._patched("https://github.com/owner/repo/")
        assert not result.endswith("/")

    def test_strips_fragment_and_query(self):
        result = self._patched("https://github.com/owner/repo?foo=bar#readme")
        assert "foo" not in result
        assert "#" not in result

    def test_valid_gitlab(self):
        result = self._patched("https://gitlab.com/group/project")
        assert "gitlab.com" in result

    def test_rejects_http(self):
        with pytest.raises(GitUrlError, match="HTTPS"):
            validate_repo_url("http://github.com/owner/repo")

    def test_rejects_ssh(self):
        with pytest.raises(GitUrlError, match="scheme"):
            validate_repo_url("ssh://github.com/owner/repo")

    def test_rejects_git_scheme(self):
        with pytest.raises(GitUrlError, match="scheme"):
            validate_repo_url("git://github.com/owner/repo")

    def test_rejects_file_scheme(self):
        with pytest.raises(GitUrlError, match="scheme"):
            validate_repo_url("file:///etc/passwd")

    def test_rejects_credentials_in_url(self):
        with pytest.raises(GitUrlError, match="Credentials"):
            validate_repo_url("https://user:pass@github.com/owner/repo")

    def test_rejects_empty_string(self):
        with pytest.raises(GitUrlError):
            validate_repo_url("")

    def test_rejects_too_long_url(self):
        with pytest.raises(GitUrlError, match="limit"):
            validate_repo_url("https://github.com/" + "a" * 500)

    # ── SSRF tests ────────────────────────────────────────────────────────────

    def test_rejects_localhost_name(self):
        with pytest.raises(GitUrlError):
            validate_repo_url("https://localhost/owner/repo")

    def test_rejects_loopback_ip_literal(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://127.0.0.1/owner/repo")

    def test_rejects_loopback_ip_another_form(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://127.0.0.2/owner/repo")

    def test_rejects_private_10_block(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://10.0.0.1/owner/repo")

    def test_rejects_private_172_block(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://172.16.0.1/owner/repo")

    def test_rejects_private_192_168_block(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://192.168.1.1/owner/repo")

    def test_rejects_link_local_ip(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://169.254.169.254/owner/repo")

    def test_rejects_dns_resolving_to_private(self):
        with patch("app.services.git_service.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("192.168.1.5", 443))]
            with pytest.raises(GitUrlError, match="private"):
                validate_repo_url("https://internal.corp.example/repo")

    def test_rejects_dns_resolution_failure(self):
        import socket
        with patch("app.services.git_service.socket.getaddrinfo", side_effect=socket.gaierror):
            with pytest.raises(GitUrlError, match="resolve"):
                validate_repo_url("https://no-such-host.invalid/repo")

    def test_rejects_ipv6_loopback(self):
        with pytest.raises(GitUrlError, match="private"):
            validate_repo_url("https://[::1]/repo")

    def test_accepts_public_ip_literal(self):
        result = validate_repo_url("https://1.2.3.4/repo")
        assert "1.2.3.4" in result


# ── Branch validation unit tests ─────────────────────────────────────────────

class TestValidateBranch:
    def test_valid_main(self):
        assert validate_branch("main") == "main"

    def test_valid_develop(self):
        assert validate_branch("develop") == "develop"

    def test_valid_feature_branch(self):
        assert validate_branch("feature/my-feature") == "feature/my-feature"

    def test_valid_version_tag(self):
        assert validate_branch("v1.2.3") == "v1.2.3"

    def test_valid_with_underscores(self):
        assert validate_branch("release_1_0") == "release_1_0"

    def test_strips_whitespace(self):
        assert validate_branch("  main  ") == "main"

    def test_rejects_leading_dash(self):
        with pytest.raises(GitUrlError, match="hyphen"):
            validate_branch("-bad")

    def test_rejects_leading_dot(self):
        with pytest.raises(GitUrlError, match="period"):
            validate_branch(".hidden")

    def test_rejects_double_dot(self):
        with pytest.raises(GitUrlError, match="'\\.\\.'"):
            validate_branch("refs/../head")

    def test_rejects_trailing_dot(self):
        with pytest.raises(GitUrlError, match="period"):
            validate_branch("branch.")

    def test_rejects_dot_lock_suffix(self):
        with pytest.raises(GitUrlError, match=".lock"):
            validate_branch("foo.lock")

    def test_rejects_at_brace(self):
        with pytest.raises(GitUrlError):
            validate_branch("branch@{0}")

    def test_rejects_empty(self):
        with pytest.raises(GitUrlError):
            validate_branch("")

    def test_rejects_space(self):
        with pytest.raises(GitUrlError):
            validate_branch("bad branch")

    def test_rejects_too_long(self):
        with pytest.raises(GitUrlError, match="limit"):
            validate_branch("a" * 256)


# ── API endpoint tests ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def committing_client(setup_test_db):
    init_db(_TEST_DB_URL)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def git_owner(setup_test_db):
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        u = User(
            id=uuid.uuid4(),
            email="git_owner@test.invalid",
            password_hash=hash_password("TestPass1!"),
            full_name="Git Owner",
            system_role="member",
            is_email_verified=True,
            is_active=True,
        )
        session.add(u)
        await session.commit()
        token = create_access_token(subject=str(u.id))
    await engine.dispose()
    return u, token


@pytest_asyncio.fixture
async def git_project(committing_client, git_owner):
    _, token = git_owner
    r = await committing_client.post(
        "/api/v1/projects",
        json={"name": "GitProject", "description": "test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest_asyncio.fixture
async def git_viewer_token(setup_test_db, git_project):
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        u = User(
            id=uuid.uuid4(),
            email="git_viewer@test.invalid",
            password_hash=hash_password("TestPass1!"),
            full_name="Viewer",
            system_role="member",
            is_email_verified=True,
            is_active=True,
        )
        session.add(u)
        await session.flush()
        membership = ProjectMembership(
            project_id=uuid.UUID(git_project), user_id=u.id, role="viewer"
        )
        session.add(membership)
        await session.commit()
        token = create_access_token(subject=str(u.id))
    await engine.dispose()
    return token


def _git_auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _valid_git_payload():
    return {"repo_url": "https://github.com/example/repo", "branch": "main"}


def _patch_url_valid():
    """Patch validate_repo_url to skip DNS and return the input unchanged."""
    return patch(
        "app.api.analysis.validate_repo_url",
        side_effect=lambda url: url,
    )


class TestSubmitGitAnalysis:
    async def test_requires_auth(self, committing_client, git_project):
        r = await committing_client.post(
            f"/api/v1/projects/{git_project}/analyse/git",
            json=_valid_git_payload(),
        )
        assert r.status_code == 401

    async def test_viewer_cannot_submit(self, committing_client, git_project, git_viewer_token):
        with _patch_url_valid():
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json=_valid_git_payload(),
                headers=_git_auth(git_viewer_token),
            )
        assert r.status_code == 403

    async def test_nonmember_cannot_submit(self, committing_client, git_project, setup_test_db):
        engine = create_async_engine(_TEST_DB_URL, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            u = User(
                id=uuid.uuid4(), email="outsider@test.invalid",
                password_hash=hash_password("x"), full_name="Out",
                system_role="member", is_email_verified=True, is_active=True,
            )
            session.add(u)
            await session.commit()
            tok = create_access_token(subject=str(u.id))
        await engine.dispose()
        with _patch_url_valid():
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json=_valid_git_payload(),
                headers=_git_auth(tok),
            )
        assert r.status_code == 403

    async def test_invalid_url_scheme_returns_422(self, committing_client, git_project, git_owner):
        _, token = git_owner
        r = await committing_client.post(
            f"/api/v1/projects/{git_project}/analyse/git",
            json={"repo_url": "ssh://github.com/owner/repo", "branch": "main"},
            headers=_git_auth(token),
        )
        assert r.status_code == 422

    async def test_private_ip_returns_422(self, committing_client, git_project, git_owner):
        _, token = git_owner
        r = await committing_client.post(
            f"/api/v1/projects/{git_project}/analyse/git",
            json={"repo_url": "https://127.0.0.1/repo", "branch": "main"},
            headers=_git_auth(token),
        )
        assert r.status_code == 422

    async def test_invalid_branch_returns_422(self, committing_client, git_project, git_owner):
        _, token = git_owner
        with _patch_url_valid():
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json={"repo_url": "https://github.com/owner/repo", "branch": "-bad"},
                headers=_git_auth(token),
            )
        assert r.status_code == 422

    async def test_valid_request_returns_202_queued(
        self, committing_client, git_project, git_owner
    ):
        _, token = git_owner
        with _patch_url_valid(), patch("app.api.analysis.run_git_analysis_job"):
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json=_valid_git_payload(),
                headers=_git_auth(token),
            )
        assert r.status_code == 202
        data = r.json()
        assert data["status"] == "queued"
        assert data["repo_url"] == "https://github.com/example/repo"
        assert data["source_branch"] == "main"

    async def test_job_metadata_persisted(
        self, committing_client, git_project, git_owner
    ):
        _, token = git_owner
        with _patch_url_valid(), patch("app.api.analysis.run_git_analysis_job"):
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json={"repo_url": "https://github.com/owner/repo", "branch": "develop"},
                headers=_git_auth(token),
            )
        assert r.status_code == 202
        data = r.json()
        job_id = data["id"]

        # Re-fetch via list endpoint to verify DB persistence
        list_r = await committing_client.get(
            f"/api/v1/projects/{git_project}/analyse",
            headers=_git_auth(token),
        )
        jobs = list_r.json()
        found = next((j for j in jobs if j["id"] == job_id), None)
        assert found is not None
        assert found["repo_url"] == "https://github.com/owner/repo"
        assert found["source_branch"] == "develop"


# ── Background job tests ──────────────────────────────────────────────────────

class TestRunGitAnalysisJob:
    """Tests for run_git_analysis_job; git and semgrep are fully mocked."""

    @pytest_asyncio.fixture(autouse=True)
    async def _setup(self, setup_test_db):
        pass

    async def _make_job(self, project_id: uuid.UUID, repo_url: str, branch: str) -> uuid.UUID:
        engine = create_async_engine(_TEST_DB_URL, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        from app.database import init_db as _init_db
        _init_db(_TEST_DB_URL)
        async with factory() as session:
            u = User(
                id=uuid.uuid4(), email=f"bg_{uuid.uuid4()}@test.invalid",
                password_hash=hash_password("x"), full_name="BG",
                system_role="member", is_email_verified=True, is_active=True,
            )
            session.add(u)
            p = Project(
                id=project_id, name="BGProject", default_branch="main", owner_id=u.id
            )
            session.add(p)
            job = AnalysisJob(
                id=uuid.uuid4(),
                project_id=project_id,
                status="queued",
                source_branch=branch,
                repo_url=repo_url,
            )
            session.add(job)
            await session.commit()
        await engine.dispose()
        return job.id

    async def _get_job(self, job_id: uuid.UUID) -> AnalysisJob | None:
        engine = create_async_engine(_TEST_DB_URL, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        from sqlalchemy import select as sa_select
        async with factory() as session:
            row = await session.execute(
                sa_select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = row.scalar_one_or_none()
        await engine.dispose()
        return job

    async def test_successful_clone_and_analysis(self, tmp_path):
        from app.services.job_runner import run_git_analysis_job
        from app.services.analysis_engine import AnalysisResult, RawFinding

        project_id = uuid.uuid4()
        repo_url = "https://github.com/owner/repo"
        branch = "main"
        dest = tmp_path / "src"
        dest.mkdir()
        (dest / "app.py").write_text("x = 1\n")

        job_id = await self._make_job(project_id, repo_url, branch)

        mock_result = AnalysisResult(
            engine_name="semgrep",
            engine_version="1.0.0",
            findings=[
                RawFinding(
                    rule_key="python.test.rule",
                    title="Test finding",
                    description="desc",
                    engine_severity="High",
                    issue_type="Vulnerability",
                    file_path="app.py",
                    line_number=1,
                    cwe_id="CWE-89",
                    owasp_category="A03:2021",
                )
            ],
        )

        with (
            patch("app.services.job_runner.clone_repository", return_value="abc" * 13 + "abcd") as mock_clone,
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
        ):
            await run_git_analysis_job(
                job_id, repo_url, branch, str(dest), timeout=30
            )

        job = await self._get_job(job_id)
        assert job is not None
        assert job.status == "completed"
        assert job.vulnerabilities_count == 1
        assert job.source_revision is not None

    async def test_clone_failure_marks_job_failed(self, tmp_path):
        from app.services.job_runner import run_git_analysis_job

        project_id = uuid.uuid4()
        dest = tmp_path / "fail_src"
        job_id = await self._make_job(
            project_id, "https://github.com/owner/repo", "main"
        )

        with patch(
            "app.services.job_runner.clone_repository",
            side_effect=GitCloneError("Repository not found"),
        ):
            await run_git_analysis_job(
                job_id, "https://github.com/owner/repo", "main", str(dest)
            )

        job = await self._get_job(job_id)
        assert job is not None
        assert job.status == "failed"
        assert "Repository not found" in (job.failure_reason or "")

    async def test_clone_timeout_marks_job_failed(self, tmp_path):
        from app.services.job_runner import run_git_analysis_job

        project_id = uuid.uuid4()
        dest = tmp_path / "timeout_src"
        job_id = await self._make_job(
            project_id, "https://github.com/owner/repo", "main"
        )

        with patch(
            "app.services.job_runner.clone_repository",
            side_effect=GitTimeoutError("git clone timed out after 120s"),
        ):
            await run_git_analysis_job(
                job_id, "https://github.com/owner/repo", "main", str(dest)
            )

        job = await self._get_job(job_id)
        assert job.status == "failed"
        assert "timed out" in (job.failure_reason or "")

    async def test_repo_too_large_marks_job_failed(self, tmp_path):
        from app.services.job_runner import run_git_analysis_job

        project_id = uuid.uuid4()
        dest = tmp_path / "large_src"
        job_id = await self._make_job(
            project_id, "https://github.com/owner/repo", "main"
        )

        with patch(
            "app.services.job_runner.clone_repository",
            side_effect=GitRepoTooLargeError("Repository contains 9999 files; limit is 5000"),
        ):
            await run_git_analysis_job(
                job_id, "https://github.com/owner/repo", "main", str(dest)
            )

        job = await self._get_job(job_id)
        assert job.status == "failed"

    async def test_git_not_installed_marks_job_failed(self, tmp_path):
        from app.services.job_runner import run_git_analysis_job
        from app.services.git_service import GitServiceError

        project_id = uuid.uuid4()
        dest = tmp_path / "no_git_src"
        job_id = await self._make_job(
            project_id, "https://github.com/owner/repo", "main"
        )

        with patch(
            "app.services.job_runner.clone_repository",
            side_effect=GitServiceError("git is not installed or not on PATH"),
        ):
            await run_git_analysis_job(
                job_id, "https://github.com/owner/repo", "main", str(dest)
            )

        job = await self._get_job(job_id)
        assert job.status == "failed"
        assert "git is not installed" in (job.failure_reason or "")


# ── Regression: ZIP upload unaffected ─────────────────────────────────────────

class TestZipUploadUnchanged:
    """Confirm the original ZIP endpoint still works after the git changes."""

    async def test_zip_endpoint_still_accepts_uploads(self, committing_client, git_project, git_owner):
        _, token = git_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)
        with patch("app.api.analysis.run_analysis_job"):
            r = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_git_auth(token),
            )
        assert r.status_code == 202
        data = r.json()
        assert data["status"] == "queued"
        assert data.get("repo_url") is None

    async def test_zip_and_git_jobs_coexist(self, committing_client, git_project, git_owner):
        _, token = git_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)
        with patch("app.api.analysis.run_analysis_job"):
            r1 = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_git_auth(token),
            )
        assert r1.status_code == 202

        with _patch_url_valid(), patch("app.api.analysis.run_git_analysis_job"):
            r2 = await committing_client.post(
                f"/api/v1/projects/{git_project}/analyse/git",
                json=_valid_git_payload(),
                headers=_git_auth(token),
            )
        assert r2.status_code == 202

        list_r = await committing_client.get(
            f"/api/v1/projects/{git_project}/analyse",
            headers=_git_auth(token),
        )
        assert len(list_r.json()) == 2
