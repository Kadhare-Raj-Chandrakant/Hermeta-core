"""Self Observation Architecture Verification Tests.

Verifies the B.1 Self Observation domain models comply with:
- Domain purity (no forbidden imports)
- Read-only design (no mutation methods)
- Separation from Reflection (Observation ≠ ReflectionFinding)
- Separation from Evolution (Observation ≠ EvolutionProposal)
"""

from pathlib import Path
from tests.architecture.helpers import (
    get_src_root,
    get_imports,
    has_forbidden_dependencies,
    get_class_method_names,
)


def _violation_msg(violations: list[str], component: str, rule: str) -> str:
    if not violations:
        return ""
    lines = [f"[RULE {rule}] {component} violation:"]
    lines.extend(f"  - {v}" for v in violations)
    return "\n".join(lines)


# ── O-1: Domain Purity ─────────────────────────────────────────────────

class TestObservationDomainPurity:
    """Observation models must remain in domain layer with zero forbidden dependencies."""

    OBSERVATION_FILES = [
        "signal.py",
        "evidence.py",
        "observation.py",
        "snapshot.py",
    ]

    FORBIDDEN_DEPENDENCIES = (
        "brain.application",
        "brain.runtime",
        "brain.adapter",
        "brain.repositories",
        "brain.infrastructure",
        "brain.planning",
        "brain.reflection",
        "brain.evolution",
        "brain.learning",
        "brain.execution",
        "brain.validation",
        "brain.detection",
        "brain.retrieval",
        "brain.services",
    )

    def test_observation_models_no_forbidden_imports(self):
        src_root = get_src_root()
        observation_dir = src_root / "brain" / "domain" / "observation"

        violations = []
        for filename in self.OBSERVATION_FILES:
            file_path = observation_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "ObservationDomain", "O-1")
        assert not violations, msg


# ── O-2, O-3, O-4: Read-Only Design ────────────────────────────────────

class TestObservationReadOnly:
    """Observation models must not contain mutation methods or decision logic."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "approve", "trigger", "emit", "publish",
    )

    def test_observation_models_no_mutation_methods(self):
        src_root = get_src_root()
        observation_dir = src_root / "brain" / "domain" / "observation"

        violations = []
        for py_file in observation_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            class_methods = get_class_method_names(py_file)
            for class_name, method_name in class_methods:
                for pattern in self.MUTATION_PATTERNS:
                    if method_name.startswith(pattern):
                        rel = py_file.relative_to(src_root)
                        violations.append(
                            f"{rel}.{class_name}.{method_name} starts with '{pattern}'"
                        )

        msg = _violation_msg(violations, "ObservationModels", "O-2/O-3/O-4")
        assert not violations, msg


# ── O-5: Evidence and Interpretation Separate ──────────────────────────

class TestEvidenceInterpretationSeparation:
    """ObservationEvidence must not contain interpretation logic."""

    INTERPRETATION_PATTERNS = (
        "def interpret", "def diagnose", "def analyze", "def assess", "def evaluate",
        "def judge", "def determine", "def conclude", "def infer", "def recommend",
    )

    def test_evidence_no_interpretation(self):
        src_root = get_src_root()
        evidence_file = src_root / "brain" / "domain" / "observation" / "evidence.py"

        if not evidence_file.exists():
            return

        source = evidence_file.read_text(encoding="utf-8")
        violations = []
        for pattern in self.INTERPRETATION_PATTERNS:
            if pattern in source:
                violations.append(f"evidence.py contains interpretation method '{pattern}'")

        msg = _violation_msg(violations, "ObservationEvidence", "O-5")
        assert not violations, msg


# ── O-6: Observation Does Not Create EvolutionProposal ──────────────────

class TestObservationEvolutionSeparation:
    """Observation models must not create or reference EvolutionProposal."""

    def test_observation_no_evolution_proposal_import(self):
        src_root = get_src_root()
        observation_dir = src_root / "brain" / "domain" / "observation"

        violations = []
        for py_file in observation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evolution" in imp and "proposal" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ObservationModels", "O-6")
        assert not violations, msg

    def test_observation_no_proposal_creation_methods(self):
        src_root = get_src_root()
        observation_dir = src_root / "brain" / "domain" / "observation"

        violations = []
        for py_file in observation_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            if "EvolutionProposal" in source or "evolution_proposal" in source.lower():
                rel = py_file.relative_to(src_root)
                violations.append(f"{rel} references EvolutionProposal")

        msg = _violation_msg(violations, "ObservationModels", "O-6")
        assert not violations, msg


# ── Separation: SystemObservation ≠ EvolutionProposal ──────────────────

class TestObservationVsProposalSeparation:
    """SystemObservation and EvolutionProposal must remain distinct concepts."""

    def test_observation_and_proposal_different_modules(self):
        src_root = get_src_root()
        observation_file = src_root / "brain" / "domain" / "observation" / "observation.py"
        evolution_file = src_root / "brain" / "domain" / "evolution_domain.py"

        assert observation_file.exists(), "Observation module missing"
        assert evolution_file.exists(), "Evolution domain module missing"

        # They should not import each other
        obs_imports = get_imports(observation_file)
        for imp in obs_imports:
            if "evolution" in imp:
                violations = [f"observation.py imports evolution: {imp}"]
                msg = _violation_msg(violations, "ObservationProposalSeparation", "O-6")
                assert not violations, msg

        evo_imports = get_imports(evolution_file)
        for imp in evo_imports:
            if "observation" in imp:
                violations = [f"evolution_domain.py imports observation: {imp}"]
                msg = _violation_msg(violations, "ObservationProposalSeparation", "O-6")
                assert not violations, msg


# ── Separation: Observation ≠ ReflectionFinding ────────────────────────

class TestObservationVsReflectionSeparation:
    """SystemObservation and ReflectionFinding must remain distinct."""

    def test_observation_no_reflection_import(self):
        src_root = get_src_root()
        observation_dir = src_root / "brain" / "domain" / "observation"

        violations = []
        for py_file in observation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "reflection" in imp:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ObservationModels", "ReflectionSeparation")
        assert not violations, msg

    def test_reflection_no_observation_import(self):
        src_root = get_src_root()
        reflection_dir = src_root / "brain" / "reflection"

        if not reflection_dir.exists():
            return

        violations = []
        for py_file in reflection_dir.rglob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "observation" in imp:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ReflectionModels", "ReflectionSeparation")
        assert not violations, msg


# ── Observation Category Constraints ──────────────────────────────────

class TestObservationCategoryConstraints:
    """Observation categories must not encode severity or action."""

    def test_categories_are_descriptive_only(self):
        src_root = get_src_root()
        obs_file = src_root / "brain" / "domain" / "observation" / "observation.py"

        if not obs_file.exists():
            return

        source = obs_file.read_text(encoding="utf-8")

        # Categories should not contain action-oriented names
        forbidden_category_names = (
            "SEVERE", "CRITICAL", "URGENT", "HIGH_PRIORITY",
            "ACTION_REQUIRED", "MUST_CHANGE", "REQUIRES_FIX",
        )

        violations = []
        for forbidden in forbidden_category_names:
            if forbidden in source:
                violations.append(f"observation.py contains action-oriented category '{forbidden}'")

        msg = _violation_msg(violations, "ObservationCategory", "CategoryConstraints")
        assert not violations, msg


# ── Snapshot Constraints ──────────────────────────────────────────────

class TestSnapshotConstraints:
    """ObservationSnapshot must not compare, trend, or analyze."""

    SNAPSHOT_FORBIDDEN_METHODS = (
        "compare", "trend", "diff", "delta", "change", "improvement",
        "regression", "detect", "analyze", "calculate", "compute",
    )

    def test_snapshot_no_analysis(self):
        src_root = get_src_root()
        snapshot_file = src_root / "brain" / "domain" / "observation" / "snapshot.py"

        if not snapshot_file.exists():
            return

        source = snapshot_file.read_text(encoding="utf-8")

        violations = []
        for pattern in self.SNAPSHOT_FORBIDDEN_METHODS:
            if f"def {pattern}" in source:
                violations.append(f"snapshot.py contains analysis method 'def {pattern}'")

        msg = _violation_msg(violations, "ObservationSnapshot", "SnapshotConstraints")
        assert not violations, msg