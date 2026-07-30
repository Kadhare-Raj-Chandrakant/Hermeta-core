"""Hypothesis & Problem Formulation Architecture Verification Tests.

Verifies the B.2 Problem domain models comply with constitutional laws H-1 through H-8.
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


# ── H-1, H-6, H-7: Domain Purity & No Forbidden Imports ────────────────

class TestProblemDomainPurity:
    """Problem models must remain in domain layer with zero forbidden dependencies."""

    PROBLEM_FILES = [
        "enums.py",
        "hypothesis.py",
        "hypothesis_space.py",
        "problem_statement.py",
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
        "brain.application.usecases",
        "brain.application.workflow",
        "brain.application.bridges",
    )

    def test_problem_models_no_forbidden_imports(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for filename in self.PROBLEM_FILES:
            file_path = problem_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "ProblemDomain", "H-1/H-6/H-7")
        assert not violations, msg


# ── H-1, H-2, H-4, H-6, H-7: Read-Only & No Mutation/Action Methods ───

class TestProblemReadOnlyDesign:
    """Problem models must not contain mutation, execution, or recommendation methods."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "approve", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
    )

    EXECUTION_PATTERNS = (
        "execute", "run", "perform", "apply", "run_", "execute_",
    )

    RECOMMENDATION_PATTERNS = (
        "recommend", "suggest", "propose", "should", "must_",
    )

    def test_problem_models_no_mutation_methods(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "ProblemModels", "H-1/H-4/H-6/H-7")
        assert not violations, msg

    def test_hypothesis_no_execution_fields(self):
        """Hypothesis must not contain execution-related fields."""
        src_root = get_src_root()
        hypothesis_file = src_root / "brain" / "domain" / "problem" / "hypothesis.py"
        source = hypothesis_file.read_text(encoding="utf-8")

        # Check for actual field definitions (name: type = value), not docstrings
        forbidden_fields = (
            "proposal_id:", "execution_plan:", "mutation:", "governance:",
            "approval:", "decision:", "evaluation:", "execution:",
        )

        violations = []
        for forbidden in forbidden_fields:
            if forbidden in source:
                violations.append(f"hypothesis.py contains execution field '{forbidden}'")

        msg = _violation_msg(violations, "Hypothesis", "H-6")
        assert not violations, msg


# ── H-3: ProblemStatement References Multiple Hypotheses ──────────────

class TestProblemStatementMultipleHypotheses:
    """ProblemStatement may reference multiple hypotheses through hypothesis_space_id."""

    def test_problem_statement_has_hypothesis_space_reference(self):
        src_root = get_src_root()
        problem_file = src_root / "brain" / "domain" / "problem" / "problem_statement.py"
        source = problem_file.read_text(encoding="utf-8")

        # Must have hypothesis_space_id field
        assert "hypothesis_space_id" in source, "ProblemStatement missing hypothesis_space_id"
        assert "hypothesis_space_id" in source and "uuid.UUID" in source, "hypothesis_space_id must be UUID"

    def test_problem_statement_has_observation_ids(self):
        """ProblemStatement must trace back to observations (H-8)."""
        src_root = get_src_root()
        problem_file = src_root / "brain" / "domain" / "problem" / "problem_statement.py"
        source = problem_file.read_text(encoding="utf-8")

        assert "observation_ids" in source, "ProblemStatement missing observation_ids"


# ── H-5: ProblemStatement Contains No Implementation Strategies ───────

class TestProblemStatementNoStrategies:
    """ProblemStatement must not contain implementation strategies."""

    FORBIDDEN_STRATEGIES = (
        "replace_planner:", "modify_retrieval:", "execute_evolution:",
        "improve_scoring:", "modify_:", "replace_:", "implement_:",
        "execution_plan:", "implementation:", "strategy:",
    )

    def test_problem_statement_no_implementation_fields(self):
        src_root = get_src_root()
        problem_file = src_root / "brain" / "domain" / "problem" / "problem_statement.py"
        source = problem_file.read_text(encoding="utf-8")

        violations = []
        for forbidden in self.FORBIDDEN_STRATEGIES:
            if forbidden in source:
                violations.append(f"problem_statement.py contains strategy field '{forbidden}'")

        msg = _violation_msg(violations, "ProblemStatement", "H-5")
        assert not violations, msg


# ── H-7: Proposal/Evaluation/Decision Separation ──────────────────────

class TestProposalEvaluationDecisionSeparation:
    """Problem models must not reference Proposal, Evaluation, or Decision."""

    def test_no_proposal_references(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "proposal" in imp.lower() and "hypothesis" not in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProblemModels", "H-7")
        assert not violations, msg

    def test_no_evaluation_references(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProblemModels", "H-7")
        assert not violations, msg

    def test_no_decision_references(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "decision" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProblemModels", "H-7")
        assert not violations, msg

    def test_source_no_proposal_evaluation_decision(self):
        """Source code must not contain Proposal/Evaluation/Decision field references."""
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            # Check for actual field definitions (name: type)
            for term in ("proposal_id:", "evaluation_id:", "decision_id:"):
                if term in source:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} references {term}")

        msg = _violation_msg(violations, "ProblemModels", "H-7")
        assert not violations, msg


# ── H-8: Traceability Back to Observations ────────────────────────────

class TestTraceability:
    """Every ProblemStatement must preserve traceability to observations via hypotheses."""

    def test_hypothesis_has_observation_ids(self):
        src_root = get_src_root()
        hypothesis_file = src_root / "brain" / "domain" / "problem" / "hypothesis.py"
        source = hypothesis_file.read_text(encoding="utf-8")

        assert "supporting_observation_ids" in source, "Hypothesis missing supporting_observation_ids"

    def test_hypothesis_space_has_observation_ids(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "problem" / "hypothesis_space.py"
        source = space_file.read_text(encoding="utf-8")

        assert "observation_ids" in source, "HypothesisSpace missing observation_ids"

    def test_problem_statement_links_observations_to_hypotheses(self):
        """ProblemStatement → hypothesis_space_id → observation_ids chain."""
        src_root = get_src_root()
        problem_file = src_root / "brain" / "domain" / "problem" / "problem_statement.py"
        source = problem_file.read_text(encoding="utf-8")

        assert "hypothesis_space_id" in source
        assert "observation_ids" in source


# ── Category/Severity Constraints ────────────────────────────────────

class TestCategorySeverityConstraints:
    """Problem categories and severity must not encode action or priority."""

    def test_categories_no_action_names(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "problem" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        forbidden = ("URGENT", "ACTION_REQUIRED", "MUST_FIX", "IMMEDIATE", "HIGH_PRIORITY")
        violations = []
        for f in forbidden:
            if f in source:
                violations.append(f"enums.py contains action-oriented category '{f}'")

        msg = _violation_msg(violations, "ProblemCategory", "H-5/H-6")
        assert not violations, msg

    def test_severity_no_execution_priority(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "problem" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        # Severity values should be impact-only, not execution-oriented
        execution_terms = ("EXECUTE_NOW", "RUN_FIRST", "SCHEDULE_IMMEDIATELY")
        violations = []
        for term in execution_terms:
            if term in source:
                violations.append(f"enums.py contains execution-oriented severity '{term}'")

        msg = _violation_msg(violations, "ProblemSeverity", "H-5")
        assert not violations, msg


# ── HypothesisSpace Container Only ───────────────────────────────────

class TestHypothesisSpaceContainerOnly:
    """HypothesisSpace must be a passive container — no ranking, evaluation, or selection."""

    FORBIDDEN_METHODS = (
        "rank", "sort", "filter", "select", "choose", "pick", "best",
        "evaluate", "score", "compare", "judge", "prefer",
    )

    def test_hypothesis_space_no_ranking_methods(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "problem" / "hypothesis_space.py"
        source = space_file.read_text(encoding="utf-8")

        violations = []
        for pattern in self.FORBIDDEN_METHODS:
            if f"def {pattern}" in source:
                violations.append(f"hypothesis_space.py contains ranking method 'def {pattern}'")

        msg = _violation_msg(violations, "HypothesisSpace", "H-2/H-3/H-7")
        assert not violations, msg


# ── Observation Independence ──────────────────────────────────────────

class TestObservationIndependence:
    """Observations must remain immutable regardless of hypotheses/problems."""

    def test_problem_models_no_observation_mutation(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            # Should not have methods that modify observations
            if "observation" in source and ("modify" in source or "update" in source or "change" in source):
                if "def " in source and ("modify" in source or "update" in source):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} may contain observation mutation")

        msg = _violation_msg(violations, "ProblemModels", "H-4")
        assert not violations, msg


# ── No Runtime/Application Coupling ───────────────────────────────────

class TestNoRuntimeCoupling:
    """Problem models must not have runtime or application dependencies."""

    def test_no_runtime_imports(self):
        src_root = get_src_root()
        problem_dir = src_root / "brain" / "domain" / "problem"

        violations = []
        for py_file in problem_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain.runtime") or imp.startswith("brain.application") or imp.startswith("brain.adapter"):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProblemModels", "RuntimeIsolation")
        assert not violations, msg