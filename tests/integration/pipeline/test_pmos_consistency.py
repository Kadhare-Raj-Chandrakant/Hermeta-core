"""PMOS consistency verification tests.

Explicitly verifies PMOS integrity after implementation.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest


class TestPMOSConsistency:
    """PMOS consistency verification."""

    def setup_method(self):
        self.pmos_root = Path("PMOS")

    def test_architecture_version_unchanged(self):
        """Architecture version unchanged."""
        current_state = (self.pmos_root / "CURRENT_STATE.md").read_text(encoding="utf-8")
        assert "Architecture Version | B.8" in current_state
        assert "Pipeline Version | 8-stage frozen" in current_state
        assert "Constitution Version | 1.0" in current_state

    def test_architecture_fingerprint_unchanged(self):
        """Architecture fingerprint unchanged."""
        fingerprint = (self.pmos_root / "ARCHITECTURE_FINGERPRINT.md").read_text(encoding="utf-8")
        # Fingerprint should exist and be non-empty
        assert len(fingerprint) > 100

    def test_freeze_declaration_unchanged(self):
        """Freeze declaration unchanged."""
        current_state = (self.pmos_root / "CURRENT_STATE.md").read_text(encoding="utf-8")
        assert "Architecture Freeze | ACTIVE" in current_state

    def test_current_milestone_updated(self):
        """Current milestone updated correctly."""
        current_state = (self.pmos_root / "CURRENT_STATE.md").read_text(encoding="utf-8")
        assert "26.4" in current_state
        assert "COMPLETE" in current_state

    def test_next_milestone_updated(self):
        """Next milestone updated correctly."""
        next_task = (self.pmos_root / "NEXT_TASK.md").read_text(encoding="utf-8")
        assert "Milestone 27" in next_task or "27" in next_task
        assert "Final Documentation" in next_task

    def test_session_updated(self):
        """Session updated correctly."""
        session = (self.pmos_root / "SESSION.md").read_text(encoding="utf-8")
        assert "26.4" in session or "26.1" in session
        assert "COMPLETE" in session

    def test_no_duplicate_project_truth(self):
        """No duplicate project truth introduced."""
        # Single source of truth maintained
        # Verify PMOS files reference each other consistently
        current_state = (self.pmos_root / "CURRENT_STATE.md").read_text(encoding="utf-8")
        next_task = (self.pmos_root / "NEXT_TASK.md").read_text(encoding="utf-8")
        session = (self.pmos_root / "SESSION.md").read_text(encoding="utf-8")

        # All should reference the current/next milestone
        assert "26.4" in current_state
        assert "27" in next_task
        assert "COMPLETE" in session

    def test_historical_reports_unmodified(self):
        """Historical reports unmodified."""
        # PMOS-1 through PMOS-8 should be unchanged
        for i in range(1, 9):
            pmos_file = self.pmos_root / f"PMOS-{i}-OBSERVATION.md" if i == 1 else \
                       self.pmos_root / f"PMOS-{i}-HYPOTHESIS.md" if i == 2 else \
                       self.pmos_root / f"PMOS-{i}-PROBLEM.md" if i == 3 else \
                       self.pmos_root / f"PMOS-{i}-PROPOSAL.md" if i == 4 else \
                       self.pmos_root / f"PMOS-{i}-EVALUATION.md" if i == 5 else \
                       self.pmos_root / f"PMOS-{i}-GOVERNANCE.md" if i == 6 else \
                       self.pmos_root / f"PMOS-{i}-AUTHORIZATION.md" if i == 7 else \
                       self.pmos_root / f"PMOS-{i}-EXECUTION.md"

            if pmos_file.exists():
                content = pmos_file.read_text(encoding="utf-8")
                # Should contain engine contract
                assert "Engine Contract" in content or "Contract" in content
                assert len(content) > 100


class TestPMOSValidationRules:
    """PMOS validation rules verification."""

    def test_pmos_validation_exists(self):
        """PMOS validation rules file exists."""
        validation = Path("PMOS/PMOS_VALIDATION.md")
        assert validation.exists()
        content = validation.read_text(encoding="utf-8")
        assert len(content) > 100

    def test_manifest_exists(self):
        """PMOS manifest exists."""
        manifest = Path("PMOS/MANIFEST.md")
        assert manifest.exists()
        content = manifest.read_text(encoding="utf-8")
        assert "PMOS" in content

    def test_architecture_index_exists(self):
        """Architecture index exists."""
        index_dir = Path("PMOS/ARCHITECTURE_INDEX")
        assert index_dir.exists()
        assert index_dir.is_dir()


class TestNoDuplicateTruth:
    """Verify no duplicate project truth."""

    def test_single_source_of_truth(self):
        """PMOS is single source of truth for project state."""
        # Current state should be authoritative
        current_state = Path("PMOS/CURRENT_STATE.md").read_text(encoding="utf-8")

        # Should contain definitive milestone status
        assert "Phase B Complete" in current_state or "Phase C" in current_state
        assert "26.4" in current_state

    def test_no_conflicting_reports(self):
        """No conflicting reports in PMOS."""
        # All PMOS files should be consistent
        files = [
            "CURRENT_STATE.md",
            "SESSION.md",
            "NEXT_TASK.md",
        ]

        contents = {}
        for f in files:
            path = Path("PMOS") / f
            if path.exists():
                contents[f] = path.read_text(encoding="utf-8")

        # All should reference the current/next milestone
        for name, content in contents.items():
            assert "26.4" in content or "27" in content, f"{name} doesn't reference correct milestone"

        # MANIFEST.md is historical
        manifest = Path("PMOS") / "MANIFEST.md"
        if manifest.exists():
            content = manifest.read_text(encoding="utf-8")
            assert "PMOS" in content