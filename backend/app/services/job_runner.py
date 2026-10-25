"""
Background analysis job runner.

Architecture note:
Jobs run as asyncio tasks within the FastAPI process.
Semgrep (subprocess) runs in a thread via asyncio.to_thread().
Jobs do NOT survive server restart; stale 'running' jobs are reset
to 'failed' at startup by main.py's lifespan.

Risk scoring: each finding receives a deterministic risk_score and
risk_level computed by app.services.risk_scoring (SRS FR-RISK-01–07).
"""
import asyncio
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.database import get_session_factory
from app.models.analysis import AnalysisJob
from app.models.finding import Finding
from app.services.analysis_engine import AnalysisEngineError, run_semgrep
from app.services.cvss_scoring import score_cvss_vector
from app.services.duplication_service import detect_duplications
from app.services.git_service import GitServiceError, clone_repository
from app.services.risk_scoring import SCORING_VERSION, score_finding

logger = logging.getLogger(__name__)

# Technical debt estimates — minutes per finding by issue type.
# Labeled "estimate" in API responses; no industry-standard claim is made.
_DEBT_MINUTES_PER_TYPE: dict[str, int] = {
    "Vulnerability": 30,
    "Security Hotspot": 20,
    "Bug": 15,
    "Code Smell": 5,
}


def _calculate_technical_debt(findings: list) -> int:
    """Return total estimated remediation time in minutes across all findings."""
    return sum(_DEBT_MINUTES_PER_TYPE.get(f.issue_type, 5) for f in findings)


def _sanitize_failure_reason(msg: str, source_path: str | None) -> str:
    """Replace the internal upload path with a placeholder before storing."""
    if source_path:
        msg = msg.replace(source_path, "<source_dir>")
    return msg[:500]


async def run_analysis_job(
    job_id: uuid.UUID,
    source_path: str,
    timeout: int = 300,
    max_bugs: int = 0,
    max_vulnerabilities: int = 0,
    enforce_coverage: bool = False,
    coverage_target_pct: float = 80.0,
) -> None:
    """
    Execute an analysis job end-to-end.
    Creates its own DB session (request session has already closed).
    """
    factory = get_session_factory()

    # ── Mark running ──────────────────────────────────────────────────────────
    async with factory() as db:
        try:
            row = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
            job = row.scalar_one_or_none()
            if job is None:
                logger.error("run_analysis_job: job %s not found", job_id)
                return
            if job.status != "queued":
                logger.warning("run_analysis_job: job %s is in state %s, expected queued", job_id, job.status)
                return
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()
        except Exception:
            logger.exception("Failed to mark job %s as running", job_id)
            return

    # ── Run semgrep in a thread ───────────────────────────────────────────────
    analysis_result = None
    error_msg: str | None = None
    try:
        analysis_result = await asyncio.to_thread(
            run_semgrep, Path(source_path), timeout
        )
    except AnalysisEngineError as exc:
        error_msg = str(exc)
        logger.warning("Analysis engine error for job %s: %s", job_id, exc)
    except Exception as exc:
        error_msg = "Unexpected error during analysis"
        logger.exception("Unexpected error for job %s", job_id)

    # ── Persist results ───────────────────────────────────────────────────────
    async with factory() as db:
        try:
            row = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
            job = row.scalar_one_or_none()
            if job is None:
                logger.error("run_analysis_job: job %s gone before finalise", job_id)
                return

            now = datetime.now(timezone.utc)

            if error_msg or analysis_result is None:
                job.status = "failed"
                job.failed_at = now
                job.failure_reason = _sanitize_failure_reason(error_msg or "Unknown error", source_path)
                db.add(job)
            else:
                # Insert findings with deterministic risk scores (FR-RISK-01, FR-RISK-03)
                for raw in analysis_result.findings:
                    r_score, r_level = score_finding(
                        raw.engine_severity,
                        raw.issue_type,
                        raw.cwe_id,
                        raw.owasp_category,
                    )
                    cvss_result = score_cvss_vector(raw.cvss_vector)
                    f = Finding(
                        id=uuid.uuid4(),
                        analysis_job_id=job.id,
                        project_id=job.project_id,
                        engine_severity=raw.engine_severity,
                        risk_level=r_level,
                        risk_score=r_score,
                        risk_score_version=SCORING_VERSION,
                        issue_type=raw.issue_type,
                        title=raw.title,
                        rule_key=raw.rule_key,
                        file_path=raw.file_path,
                        line_number=raw.line_number,
                        description=raw.description,
                        status="Open",
                        cwe_id=raw.cwe_id,
                        owasp_category=raw.owasp_category,
                        cvss_vector=raw.cvss_vector,
                        cvss_version=raw.cvss_version,
                        cvss_score=cvss_result.score,
                    )
                    db.add(f)

                await db.flush()

                bugs = sum(
                    1 for r in analysis_result.findings if r.issue_type == "Bug"
                )
                vulns = sum(
                    1 for r in analysis_result.findings if r.issue_type == "Vulnerability"
                )
                smells = sum(
                    1 for r in analysis_result.findings if r.issue_type == "Code Smell"
                )
                hotspots = sum(
                    1 for r in analysis_result.findings if r.issue_type == "Security Hotspot"
                )

                # Technical debt estimate (transparent; labeled "estimate" in API)
                debt_minutes = _calculate_technical_debt(analysis_result.findings)

                # Duplication detection — run synchronously here (already in a bg thread)
                try:
                    dup = detect_duplications(Path(source_path))
                    dup_pct = dup.pct
                except Exception:
                    logger.warning("Duplication detection failed for job %s", job_id, exc_info=True)
                    dup_pct = None

                job.status = "completed"
                job.completed_at = now
                job.engine_name = analysis_result.engine_name
                job.engine_version = analysis_result.engine_version
                job.bugs_count = bugs
                job.vulnerabilities_count = vulns
                job.code_smells_count = smells
                job.security_hotspots_count = hotspots
                job.technical_debt_minutes = debt_minutes
                job.duplications_pct = dup_pct
                job.scoring_model_version = SCORING_VERSION
                # Quality gate: configurable thresholds (defaults: 0,0 = strict)
                gate_pass = vulns <= max_vulnerabilities and bugs <= max_bugs
                if enforce_coverage and job.coverage_pct is not None:
                    if job.coverage_pct < coverage_target_pct:
                        gate_pass = False
                job.quality_gate_passed = gate_pass
                db.add(job)

            await db.commit()
            logger.info(
                "Job %s finished with status=%s findings=%s",
                job_id,
                job.status,
                len(analysis_result.findings) if analysis_result else 0,
            )
        except Exception:
            logger.exception("Failed to finalise job %s", job_id)
            await db.rollback()


async def run_git_analysis_job(
    job_id: uuid.UUID,
    repo_url: str,
    branch: str,
    dest_dir: str,
    timeout: int = 300,
    max_bugs: int = 0,
    max_vulnerabilities: int = 0,
    enforce_coverage: bool = False,
    coverage_target_pct: float = 80.0,
) -> None:
    """
    Clone a public Git repository and run analysis end-to-end.
    Creates its own DB sessions (request session has already closed).

    Security: repository source code is never executed; only passed to semgrep.
    Cleanup: dest_dir is removed on clone failure.
    """
    from app.config import settings

    factory = get_session_factory()

    # ── Mark running ──────────────────────────────────────────────────────────
    async with factory() as db:
        try:
            row = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
            job = row.scalar_one_or_none()
            if job is None:
                logger.error("run_git_analysis_job: job %s not found", job_id)
                return
            if job.status != "queued":
                logger.warning(
                    "run_git_analysis_job: job %s is in state %s, expected queued",
                    job_id, job.status,
                )
                return
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()
        except Exception:
            logger.exception("Failed to mark git job %s as running", job_id)
            return

    # ── Clone repository in a thread ─────────────────────────────────────────
    commit_sha: str | None = None
    clone_error: str | None = None
    source_path = dest_dir  # will be set to cloned dir on success

    try:
        commit_sha = await asyncio.to_thread(
            clone_repository,
            repo_url,
            branch,
            Path(dest_dir),
            settings.GIT_CLONE_TIMEOUT_SECONDS,
            settings.GIT_MAX_REPO_MB,
            settings.GIT_MAX_FILE_COUNT,
        )
    except GitServiceError as exc:
        clone_error = str(exc)
        logger.warning("Git clone failed for job %s: %s", job_id, exc)
    except Exception:
        clone_error = "Unexpected error during repository clone"
        logger.exception("Unexpected clone error for job %s", job_id)

    # ── Update job with clone metadata (even on failure) ─────────────────────
    async with factory() as db:
        try:
            row = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
            job = row.scalar_one_or_none()
            if job is None:
                logger.error("run_git_analysis_job: job %s gone after clone", job_id)
                return
            if clone_error:
                job.status = "failed"
                job.failed_at = datetime.now(timezone.utc)
                job.failure_reason = clone_error[:500]
                db.add(job)
                await db.commit()
                return
            # Record metadata from successful clone
            job.source_path = source_path
            job.source_revision = commit_sha
            db.add(job)
            await db.commit()
        except Exception:
            logger.exception("Failed to update git job %s after clone", job_id)
            return

    # ── Run semgrep in a thread ───────────────────────────────────────────────
    analysis_result = None
    error_msg: str | None = None
    try:
        analysis_result = await asyncio.to_thread(
            run_semgrep, Path(source_path), timeout
        )
    except AnalysisEngineError as exc:
        error_msg = str(exc)
        logger.warning("Analysis engine error for git job %s: %s", job_id, exc)
    except Exception:
        error_msg = "Unexpected error during analysis"
        logger.exception("Unexpected analysis error for git job %s", job_id)

    # ── Persist results ───────────────────────────────────────────────────────
    async with factory() as db:
        try:
            row = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
            job = row.scalar_one_or_none()
            if job is None:
                logger.error("run_git_analysis_job: job %s gone before finalise", job_id)
                return

            now = datetime.now(timezone.utc)

            if error_msg or analysis_result is None:
                job.status = "failed"
                job.failed_at = now
                job.failure_reason = _sanitize_failure_reason(
                    error_msg or "Unknown error", source_path
                )
                db.add(job)
            else:
                for raw in analysis_result.findings:
                    r_score, r_level = score_finding(
                        raw.engine_severity,
                        raw.issue_type,
                        raw.cwe_id,
                        raw.owasp_category,
                    )
                    cvss_result = score_cvss_vector(raw.cvss_vector)
                    f = Finding(
                        id=uuid.uuid4(),
                        analysis_job_id=job.id,
                        project_id=job.project_id,
                        engine_severity=raw.engine_severity,
                        risk_level=r_level,
                        risk_score=r_score,
                        risk_score_version=SCORING_VERSION,
                        issue_type=raw.issue_type,
                        title=raw.title,
                        rule_key=raw.rule_key,
                        file_path=raw.file_path,
                        line_number=raw.line_number,
                        description=raw.description,
                        status="Open",
                        cwe_id=raw.cwe_id,
                        owasp_category=raw.owasp_category,
                        cvss_vector=raw.cvss_vector,
                        cvss_version=raw.cvss_version,
                        cvss_score=cvss_result.score,
                    )
                    db.add(f)

                await db.flush()

                bugs = sum(1 for r in analysis_result.findings if r.issue_type == "Bug")
                vulns = sum(1 for r in analysis_result.findings if r.issue_type == "Vulnerability")
                smells = sum(1 for r in analysis_result.findings if r.issue_type == "Code Smell")
                hotspots = sum(1 for r in analysis_result.findings if r.issue_type == "Security Hotspot")

                debt_minutes = _calculate_technical_debt(analysis_result.findings)

                try:
                    dup = detect_duplications(Path(source_path))
                    dup_pct = dup.pct
                except Exception:
                    logger.warning("Duplication detection failed for git job %s", job_id, exc_info=True)
                    dup_pct = None

                job.status = "completed"
                job.completed_at = now
                job.engine_name = analysis_result.engine_name
                job.engine_version = analysis_result.engine_version
                job.bugs_count = bugs
                job.vulnerabilities_count = vulns
                job.code_smells_count = smells
                job.security_hotspots_count = hotspots
                job.technical_debt_minutes = debt_minutes
                job.duplications_pct = dup_pct
                job.scoring_model_version = SCORING_VERSION
                gate_pass = vulns <= max_vulnerabilities and bugs <= max_bugs
                if enforce_coverage and job.coverage_pct is not None:
                    if job.coverage_pct < coverage_target_pct:
                        gate_pass = False
                job.quality_gate_passed = gate_pass
                db.add(job)

            await db.commit()
            logger.info(
                "Git job %s finished status=%s findings=%s",
                job_id,
                job.status,
                len(analysis_result.findings) if analysis_result else 0,
            )
        except Exception:
            logger.exception("Failed to finalise git job %s", job_id)
            await db.rollback()
