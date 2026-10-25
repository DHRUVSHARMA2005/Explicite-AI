"""
Tests for Supporting Metrics: duplication, technical debt, coverage, and CVSS.

Coverage:
- Duplication detection with known input data
- Duplication percentage denominator and edge cases
- Technical debt calculation and units
- Coverage unavailable state (Semgrep produces no coverage)
- CVSS valid vectors and score/version consistency
- CVSS missing vs. valid 0.0 distinction
- CVSS v4.0 vector stored without score
- API serialization of metrics and findings
- Persistence of metrics after analysis completion
- ZIP analysis regression (metrics populated for ZIP)
- Git analysis regression (metrics populated for git)
- Authentication and role restrictions unchanged
"""
import io
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

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
from app.services.analysis_engine import AnalysisResult, RawFinding
from app.services.cvss_scoring import score_cvss_vector, CvssResult
from app.services.duplication_service import detect_duplications, DuplicationResult, BLOCK_SIZE, MIN_TOTAL_LINES
from app.services.job_runner import _calculate_technical_debt

_TEST_DB_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL.replace(
    "/explicite_ai", "/test_explicite_ai"
)


# ── Technical debt unit tests ─────────────────────────────────────────────────

class TestCalculateTechnicalDebt:
    """_calculate_technical_debt returns minutes; units are documented."""

    def _make_findings(self, types: list[str]):
        class F:
            def __init__(self, issue_type):
                self.issue_type = issue_type
        return [F(t) for t in types]

    def test_empty_findings_returns_zero(self):
        assert _calculate_technical_debt([]) == 0

    def test_single_vulnerability_is_30_minutes(self):
        assert _calculate_technical_debt(self._make_findings(["Vulnerability"])) == 30

    def test_single_bug_is_15_minutes(self):
        assert _calculate_technical_debt(self._make_findings(["Bug"])) == 15

    def test_single_code_smell_is_5_minutes(self):
        assert _calculate_technical_debt(self._make_findings(["Code Smell"])) == 5

    def test_single_security_hotspot_is_20_minutes(self):
        assert _calculate_technical_debt(self._make_findings(["Security Hotspot"])) == 20

    def test_mixed_findings_sum_correctly(self):
        # 30 + 15 + 5 = 50
        result = _calculate_technical_debt(
            self._make_findings(["Vulnerability", "Bug", "Code Smell"])
        )
        assert result == 50

    def test_unknown_type_uses_default_5(self):
        result = _calculate_technical_debt(self._make_findings(["Unknown Type"]))
        assert result == 5

    def test_result_is_integer_minutes(self):
        result = _calculate_technical_debt(self._make_findings(["Bug", "Bug"]))
        assert isinstance(result, int)
        assert result == 30

    def test_no_double_counting(self):
        # Two vulnerabilities = 60, not more
        result = _calculate_technical_debt(
            self._make_findings(["Vulnerability", "Vulnerability"])
        )
        assert result == 60


# ── Duplication detection unit tests ─────────────────────────────────────────

class TestDetectDuplications:
    """detect_duplications uses real filesystem via tmp_path."""

    def _write_py(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_empty_directory_returns_pct_none(self, tmp_path):
        result = detect_duplications(tmp_path)
        assert result.pct is None
        assert result.total_lines == 0

    def test_no_supported_files_returns_pct_none(self, tmp_path):
        (tmp_path / "readme.txt").write_text("hello\n")
        result = detect_duplications(tmp_path)
        assert result.pct is None

    def test_too_few_lines_returns_pct_none(self, tmp_path):
        # Only 3 lines — below MIN_TOTAL_LINES
        self._write_py(tmp_path / "a.py", "x = 1\ny = 2\nz = 3\n")
        result = detect_duplications(tmp_path)
        assert result.pct is None
        assert result.total_lines == 3

    def test_no_duplicates_returns_zero_pct(self, tmp_path):
        # 60 unique lines
        content = "\n".join(f"line_{i} = {i}" for i in range(60))
        self._write_py(tmp_path / "a.py", content)
        result = detect_duplications(tmp_path)
        assert result.pct == 0.0
        assert result.duplicated_lines == 0

    def test_duplicate_block_detected(self, tmp_path):
        # Same BLOCK_SIZE lines appear in two files
        dup_block = "\n".join(f"x_{i} = {i}" for i in range(BLOCK_SIZE))
        # File a: 60 unique lines then the dup block
        unique = "\n".join(f"unique_a_{i} = {i}" for i in range(60))
        self._write_py(tmp_path / "a.py", unique + "\n" + dup_block)
        # File b: 60 unique lines then the same dup block
        unique_b = "\n".join(f"unique_b_{i} = {i}" for i in range(60))
        self._write_py(tmp_path / "b.py", unique_b + "\n" + dup_block)

        result = detect_duplications(tmp_path)
        assert result.pct is not None
        assert result.pct > 0.0
        assert result.duplicated_lines >= BLOCK_SIZE
        assert result.total_lines >= MIN_TOTAL_LINES

    def test_denominator_is_total_lines(self, tmp_path):
        """Percentage denominator = total_lines from detected_files."""
        # Make two files each with MIN_TOTAL_LINES unique lines
        a = "\n".join(f"a_{i} = {i}" for i in range(MIN_TOTAL_LINES))
        b = "\n".join(f"b_{i} = {i}" for i in range(MIN_TOTAL_LINES))
        self._write_py(tmp_path / "a.py", a)
        self._write_py(tmp_path / "b.py", b)

        result = detect_duplications(tmp_path)
        assert result.total_lines == MIN_TOTAL_LINES * 2
        assert result.pct == 0.0

    def test_binary_files_excluded(self, tmp_path):
        (tmp_path / "binary.py").write_bytes(b"\x00" * 200)
        # Add enough text lines to be above MIN_TOTAL_LINES
        self._write_py(tmp_path / "real.py", "\n".join(f"x = {i}" for i in range(MIN_TOTAL_LINES)))
        result = detect_duplications(tmp_path)
        # Binary excluded; result based on real.py only
        assert result.files_scanned == 1

    def test_excluded_dirs_ignored(self, tmp_path):
        node_mod = tmp_path / "node_modules"
        node_mod.mkdir()
        (node_mod / "pkg.js").write_text("x = 1\n" * 100)
        # Only real source
        self._write_py(tmp_path / "app.py", "\n".join(f"x = {i}" for i in range(MIN_TOTAL_LINES)))
        result = detect_duplications(tmp_path)
        assert result.files_scanned == 1

    def test_result_has_message(self, tmp_path):
        self._write_py(tmp_path / "a.py", "\n".join(f"x = {i}" for i in range(MIN_TOTAL_LINES)))
        result = detect_duplications(tmp_path)
        assert isinstance(result.message, str)
        assert len(result.message) > 0


# ── Coverage unavailable state ────────────────────────────────────────────────

class TestCoverageUnavailable:
    """Coverage requires a test report; Semgrep never provides one."""

    def test_job_coverage_pct_is_none_after_analysis(self):
        """
        After a completed analysis, coverage_pct must remain None.
        This is verified indirectly via the job model defaults.
        """
        job = AnalysisJob(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            status="queued",
        )
        assert job.coverage_pct is None

    def test_dashboard_api_returns_coverage_message(self, setup_test_db):
        # Tested via API integration below in TestMetricsPersistence
        pass


# ── CVSS scoring unit tests ───────────────────────────────────────────────────

class TestCvssScoring:
    def test_valid_v31_vector_returns_score(self):
        r = score_cvss_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        assert r.score is not None
        assert 9.0 <= r.score <= 10.0
        assert r.version == "3.1"
        assert r.severity == "Critical"
        assert r.error is None

    def test_none_vector_returns_none_score(self):
        r = score_cvss_vector(None)
        assert r.score is None
        assert r.version is None
        assert r.error is None

    def test_empty_string_returns_none_score(self):
        r = score_cvss_vector("")
        assert r.score is None

    def test_v40_vector_returns_none_score_but_version(self):
        r = score_cvss_vector("CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H")
        assert r.score is None
        assert r.version == "4.0"
        assert r.error is None  # not an error, just unsupported scoring

    def test_v20_vector_rejected(self):
        r = score_cvss_vector("(AV:N/AC:L/Au:N/C:C/I:C/A:C)")
        assert r.score is None
        assert r.version == "2.0"
        assert r.error is not None

    def test_zero_score_is_distinguished_from_none(self):
        # AV:P/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:N → ISC = 0 → score = 0.0
        r = score_cvss_vector("CVSS:3.1/AV:P/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:N")
        assert r.score == 0.0
        assert r.severity == "None"

    def test_malformed_vector_returns_error(self):
        r = score_cvss_vector("CVSS:3.1/GARBAGE")
        assert r.score is None
        assert r.error is not None

    def test_missing_metric_returns_error(self):
        # Missing 'A' impact metric
        r = score_cvss_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H")
        assert r.score is None
        assert r.error is not None
        assert "A" in r.error

    def test_medium_severity_band(self):
        r = score_cvss_vector("CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N")
        assert r.score is not None
        assert r.severity in ("Low", "Medium")

    def test_score_and_severity_consistent(self):
        r = score_cvss_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")
        assert r.score is not None
        if r.score >= 9.0:
            assert r.severity == "Critical"
        elif r.score >= 7.0:
            assert r.severity == "High"
        elif r.score >= 4.0:
            assert r.severity == "Medium"
        else:
            assert r.severity == "Low"


# ── API integration: metrics persistence ─────────────────────────────────────

@pytest_asyncio.fixture
async def metrics_client(setup_test_db):
    init_db(_TEST_DB_URL)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def metrics_owner(setup_test_db):
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        u = User(
            id=uuid.uuid4(),
            email=f"metrics_owner_{uuid.uuid4()}@test.invalid",
            password_hash=hash_password("TestPass1!"),
            full_name="Metrics Owner",
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
async def metrics_project(metrics_client, metrics_owner):
    _, token = metrics_owner
    r = await metrics_client.post(
        "/api/v1/projects",
        json={"name": "MetricsProject", "description": "metrics test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def _mock_analysis_result(findings=None):
    if findings is None:
        findings = [
            RawFinding(
                rule_key="python.test.vuln",
                title="Test Vulnerability",
                description="desc",
                engine_severity="High",
                issue_type="Vulnerability",
                file_path="app.py",
                line_number=1,
                cwe_id="CWE-89",
                owasp_category="A03:2021",
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cvss_version="3.1",
            ),
            RawFinding(
                rule_key="python.test.bug",
                title="Test Bug",
                description="desc",
                engine_severity="Medium",
                issue_type="Bug",
                file_path="app.py",
                line_number=5,
                cwe_id=None,
                owasp_category=None,
            ),
            RawFinding(
                rule_key="python.test.smell",
                title="Test Smell",
                description="desc",
                engine_severity="Low",
                issue_type="Code Smell",
                file_path="utils.py",
                line_number=10,
                cwe_id=None,
                owasp_category=None,
            ),
        ]
    return AnalysisResult(
        engine_name="semgrep",
        engine_version="1.0.0",
        findings=findings,
    )


class TestMetricsPersistence:
    """Verify technical debt and duplications are persisted after analysis."""

    async def test_technical_debt_persisted_after_zip_analysis(
        self, metrics_client, metrics_project, metrics_owner, tmp_path
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        mock_result = _mock_analysis_result()
        # 1 Vulnerability (30) + 1 Bug (15) + 1 Code Smell (5) = 50 minutes
        expected_debt = 50

        with (
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=5.0, duplicated_lines=3, total_lines=60, files_scanned=1, message="test"
            )),
        ):
            r = await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )
        assert r.status_code == 202
        job_id = r.json()["id"]

        # Check DB directly
        engine = create_async_engine(_TEST_DB_URL, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        from sqlalchemy import select as sa_select
        async with factory() as session:
            row = await session.execute(
                sa_select(AnalysisJob).where(AnalysisJob.id == uuid.UUID(job_id))
            )
            job = row.scalar_one_or_none()
        await engine.dispose()

        assert job is not None
        assert job.status == "completed"
        assert job.technical_debt_minutes == expected_debt
        assert job.duplications_pct == 5.0
        assert job.coverage_pct is None  # Coverage never set by Semgrep

    async def test_dashboard_returns_technical_debt_display(
        self, metrics_client, metrics_project, metrics_owner, tmp_path
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        mock_result = _mock_analysis_result()

        with (
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=3.2, duplicated_lines=2, total_lines=62, files_scanned=1, message="test"
            )),
        ):
            await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )

        dash_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/dashboard",
            headers=_auth(token),
        )
        assert dash_r.status_code == 200
        sm = dash_r.json()["supporting_metrics"]

        assert sm["technical_debt_display"] is not None
        assert sm["technical_debt_display"] != "—"
        assert sm["technical_debt_is_estimate"] is True
        assert sm["duplications_pct"] == pytest.approx(3.2, abs=0.1)
        assert sm["coverage_pct"] is None
        assert sm["coverage_message"] is not None
        assert "report" in sm["coverage_message"].lower()

    async def test_dashboard_no_analysis_shows_messages(
        self, metrics_client, metrics_owner
    ):
        _, token = metrics_owner
        r = await metrics_client.post(
            "/api/v1/projects",
            json={"name": f"EmptyProject_{uuid.uuid4()}", "description": ""},
            headers=_auth(token),
        )
        proj_id = r.json()["id"]

        dash_r = await metrics_client.get(
            f"/api/v1/projects/{proj_id}/dashboard",
            headers=_auth(token),
        )
        assert dash_r.status_code == 200
        sm = dash_r.json()["supporting_metrics"]
        assert sm["coverage_pct"] is None
        assert sm["coverage_message"] is not None
        assert sm["duplications_pct"] is None
        assert sm["technical_debt_display"] is None

    async def test_zero_technical_debt_when_no_findings(
        self, metrics_client, metrics_project, metrics_owner
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        empty_result = AnalysisResult(engine_name="semgrep", engine_version="1.0.0", findings=[])

        with (
            patch("app.services.job_runner.run_semgrep", return_value=empty_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=None, duplicated_lines=0, total_lines=1, files_scanned=1, message="too small"
            )),
        ):
            r = await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )
        assert r.status_code == 202

        dash_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/dashboard",
            headers=_auth(token),
        )
        sm = dash_r.json()["supporting_metrics"]
        assert sm["technical_debt_display"] == "0m"

    async def test_finding_cvss_score_persisted_and_returned(
        self, metrics_client, metrics_project, metrics_owner
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        # A finding WITH a valid CVSS vector
        mock_result = _mock_analysis_result(findings=[
            RawFinding(
                rule_key="python.test.sqli",
                title="SQL Injection",
                description="desc",
                engine_severity="High",
                issue_type="Vulnerability",
                file_path="db.py",
                line_number=42,
                cwe_id="CWE-89",
                owasp_category="A03:2021",
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cvss_version="3.1",
            )
        ])

        with (
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=None, duplicated_lines=0, total_lines=1, files_scanned=1, message="too small"
            )),
        ):
            await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )

        issues_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues",
            headers=_auth(token),
        )
        assert issues_r.status_code == 200
        items = issues_r.json()["items"]
        assert len(items) == 1

        detail_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues/{items[0]['id']}",
            headers=_auth(token),
        )
        assert detail_r.status_code == 200
        detail = detail_r.json()
        assert detail["cvss_score"] is not None
        assert detail["cvss_score"] >= 9.0
        assert detail["cvss_vector"] is not None
        assert detail["cvss_version"] == "3.1"
        assert detail["cvss_severity"] == "Critical"

    async def test_finding_without_cvss_returns_null_score(
        self, metrics_client, metrics_project, metrics_owner
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        mock_result = _mock_analysis_result(findings=[
            RawFinding(
                rule_key="python.test.smell",
                title="Code smell",
                description="desc",
                engine_severity="Low",
                issue_type="Code Smell",
                file_path="app.py",
                line_number=1,
                cwe_id=None,
                owasp_category=None,
                cvss_vector=None,
                cvss_version=None,
            )
        ])

        with (
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=None, duplicated_lines=0, total_lines=1, files_scanned=1, message="too small"
            )),
        ):
            await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )

        issues_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues",
            headers=_auth(token),
        )
        items = issues_r.json()["items"]
        detail_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues/{items[0]['id']}",
            headers=_auth(token),
        )
        detail = detail_r.json()
        # No CVSS data → null, NOT 0.0
        assert detail["cvss_score"] is None
        assert detail["cvss_vector"] is None

    async def test_cvss_zero_score_distinguished_from_null(
        self, metrics_client, metrics_project, metrics_owner
    ):
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        # CVSS vector that scores 0.0 (no CIA impact)
        zero_vector = "CVSS:3.1/AV:P/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:N"
        mock_result = _mock_analysis_result(findings=[
            RawFinding(
                rule_key="python.test.zero",
                title="Zero impact finding",
                description="desc",
                engine_severity="Low",
                issue_type="Vulnerability",
                file_path="app.py",
                line_number=1,
                cwe_id=None,
                owasp_category=None,
                cvss_vector=zero_vector,
                cvss_version="3.1",
            )
        ])

        with (
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=None, duplicated_lines=0, total_lines=1, files_scanned=1, message="too small"
            )),
        ):
            await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )

        issues_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues",
            headers=_auth(token),
        )
        items = issues_r.json()["items"]
        detail_r = await metrics_client.get(
            f"/api/v1/projects/{metrics_project}/issues/{items[0]['id']}",
            headers=_auth(token),
        )
        detail = detail_r.json()
        # 0.0 is a valid score — must NOT be null
        assert detail["cvss_score"] == pytest.approx(0.0)
        assert detail["cvss_severity"] == "None"
        assert detail["cvss_vector"] == zero_vector

    async def test_git_analysis_technical_debt_persisted(
        self, metrics_client, metrics_project, metrics_owner
    ):
        _, token = metrics_owner
        mock_result = _mock_analysis_result()

        def _patch_url_valid():
            return patch("app.api.analysis.validate_repo_url", side_effect=lambda url: url)

        with (
            _patch_url_valid(),
            patch("app.services.job_runner.clone_repository", return_value="a" * 40),
            patch("app.services.job_runner.run_semgrep", return_value=mock_result),
            patch("app.services.job_runner.detect_duplications", return_value=DuplicationResult(
                pct=7.5, duplicated_lines=5, total_lines=67, files_scanned=2, message="test"
            )),
        ):
            r = await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse/git",
                json={"repo_url": "https://github.com/owner/repo", "branch": "main"},
                headers=_auth(token),
            )
        assert r.status_code == 202

        engine = create_async_engine(_TEST_DB_URL, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        from sqlalchemy import select as sa_select
        job_id = r.json()["id"]
        async with factory() as session:
            row = await session.execute(
                sa_select(AnalysisJob).where(AnalysisJob.id == uuid.UUID(job_id))
            )
            job = row.scalar_one_or_none()
        await engine.dispose()

        assert job is not None
        assert job.status == "completed"
        assert job.technical_debt_minutes == 50  # same findings
        assert job.duplications_pct == pytest.approx(7.5, abs=0.1)
        assert job.coverage_pct is None

    async def test_existing_zip_upload_unaffected(
        self, metrics_client, metrics_project, metrics_owner
    ):
        """ZIP analysis endpoint still works and responds 202."""
        _, token = metrics_owner
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("app.py", "x = 1\n")
        buf.seek(0)

        with patch("app.api.analysis.run_analysis_job"):
            r = await metrics_client.post(
                f"/api/v1/projects/{metrics_project}/analyse",
                files={"source": ("repo.zip", buf, "application/zip")},
                headers=_auth(token),
            )
        assert r.status_code == 202

    async def test_auth_required_for_dashboard(
        self, metrics_client, metrics_project
    ):
        r = await metrics_client.get(f"/api/v1/projects/{metrics_project}/dashboard")
        assert r.status_code == 401

    async def test_auth_required_for_issues(
        self, metrics_client, metrics_project
    ):
        r = await metrics_client.get(f"/api/v1/projects/{metrics_project}/issues")
        assert r.status_code == 401
