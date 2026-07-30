"""Proposal Generation Architecture Verification Tests.

Verifies the B.3 Proposal domain models comply with constitutional laws P-1 through P-12.
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


# ── P-1, P-3, P-4, P-8, P-9, P-12: Domain Purity & No Forbidden Imports ──────

class TestProposalDomainPurity:
    """Proposal models must remain in domain layer with zero forbidden dependencies."""

    PROPOSAL_FILES = [
        "enums.py",
        "proposal.py",
        "proposal_space.py",
        "assumption.py",
        "outcome.py",
        "proposal_plan.py",
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

    def test_proposal_models_no_forbidden_imports(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for filename in self.PROPOSAL_FILES:
            file_path = proposal_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "ProposalDomain", "P-1/P-3/P-4/P-8/P-9/P-12")
        assert not violations, msg


# ── P-2, P-3, P-4, P-9, P-12: Read-Only & No Self-Evaluation/Mutation ──────

class TestProposalReadOnlyDesign:
    """Proposal models must not contain mutation, execution, or recommendation methods."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "approve", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
        "optimize", "filter", "rank", "sort", "choose", "pick",
    )

    def test_proposal_models_no_mutation_methods(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "ProposalModels", "P-2/P-3/P-4/P-9/P-12")
        assert not violations, msg

    def test_proposal_no_self_evaluation_fields(self):
        """Proposal must not contain score, confidence, ranking, or approval fields."""
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")

        forbidden_fields = (
            "score:", "confidence:", "ranking:", "priority:", "severity:",
            "probability:", "usefulness:", "approved:", "rejected:", "accepted:",
        )

        violations = []
        for forbidden in forbidden_fields:
            if forbidden in source:
                violations.append(f"proposal.py contains self-evaluation field '{forbidden}'")

        msg = _violation_msg(violations, "Proposal", "P-3")
        assert not violations, msg


# ── P-4: No Mutation/Execution References ─────────────────────────────────

class TestProposalNoMutation:
    """Proposal must not reference execution, mutation, or runtime behavior."""

    def test_proposal_no_execution_references(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")

        forbidden = (
            "execution_plan:", "repository:", "strategy:", "mutation:",
            "execution:", "mutation:", "runtime:",
        )

        violations = []
        for forbidden in forbidden:
            if forbidden in source:
                violations.append(f"proposal.py contains execution reference '{forbidden}'")

        msg = _violation_msg(violations, "Proposal", "P-4")
        assert not violations, msg


# ── P-5: Traceability Chain Preserved ─────────────────────────────────────

class TestProposalTraceability:
    """Every Proposal must preserve immutable traceability back to observations."""

    def test_proposal_has_originating_problem_id(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")
        assert "originating_problem_id" in source, "Proposal missing originating_problem_id"

    def test_proposal_has_hypothesis_space_id(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")
        assert "hypothesis_space_id" in source, "Proposal missing hypothesis_space_id"

    def test_proposal_has_observation_ids(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")
        assert "observation_ids" in source, "Proposal missing observation_ids"

    def test_proposal_space_links_problem_statement(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "proposal" / "proposal_space.py"
        source = space_file.read_text(encoding="utf-8")
        assert "problem_statement_id" in source, "ProposalSpace missing problem_statement_id"


# ── P-6: Proposal Preserves Uncertainty ────────────────────────────────────

class TestProposalUncertainty:
    """Proposal represents ONE possible improvement, not THE improvement."""

    def test_proposal_category_not_absolute(self):
        """ProposalCategory names must not imply certainty or absoluteness."""
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "proposal" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        absolute_terms = ("BEST_", "OPTIMAL_", "PERFECT_", "GUARANTEED_", "ONLY_")
        violations = []
        for term in absolute_terms:
            if term in source:
                violations.append(f"enums.py contains absolute term '{term}'")

        msg = _violation_msg(violations, "ProposalCategory", "P-6")
        assert not violations, msg


# ── P-7: ProposalSpace Owns Alternatives ───────────────────────────────────

class TestProposalSpaceContainerOnly:
    """ProposalSpace is a passive container — no ranking, filtering, merging, optimization."""

    FORBIDDEN_METHODS = (
        "rank", "sort", "filter", "select", "choose", "pick", "best",
        "evaluate", "score", "compare", "judge", "prefer",
        "merge", "optimize", "reduce", "eliminate",
    )

    def test_proposal_space_no_ranking_methods(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "proposal" / "proposal_space.py"
        source = space_file.read_text(encoding="utf-8")

        violations = []
        for pattern in self.FORBIDDEN_METHODS:
            if f"def {pattern}" in source:
                violations.append(f"proposal_space.py contains ranking method 'def {pattern}'")

        msg = _violation_msg(violations, "ProposalSpace", "P-7")
        assert not violations, msg


# ── P-8, P-9: Proposal Unaware of Evaluation/Decision/Execution ───────────

class TestProposalEvaluationSeparation:
    """Proposal must not reference Evaluation, Decision, Approval, Execution, Governance."""

    def test_no_evaluation_imports(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProposalModels", "P-8/P-9")
        assert not violations, msg

    def test_no_decision_imports(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "decision" in imp.lower() or "approval" in imp.lower() or "governance" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProposalModels", "P-8/P-9")
        assert not violations, msg

    def test_no_execution_imports(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "execution" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProposalModels", "P-8/P-9")
        assert not violations, msg

    def test_source_no_evaluation_decision_execution_refs(self):
        """Source code must not contain Evaluation/Decision/Execution field references."""
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            for term in ("evaluation_id:", "decision_id:", "execution_plan:", "governance:", "approval_id:"):
                if term in source:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} references {term}")

        msg = _violation_msg(violations, "ProposalModels", "P-8/P-9")
        assert not violations, msg


# ── P-10: Proposal Describes Desired Outcome ────────────────────────────────

class TestProposalIntentNotImplementation:
    """Proposal must describe desired outcome, not implementation mechanism."""

    def test_proposal_has_intended_outcomes(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")
        assert "intended_outcomes" in source, "Proposal missing intended_outcomes field"

    def test_outcome_describes_cognitive_intent(self):
        src_root = get_src_root()
        outcome_file = src_root / "brain" / "domain" / "proposal" / "outcome.py"
        source = outcome_file.read_text(encoding="utf-8")

        # Outcomes should not contain implementation mechanisms as field definitions
        implementation_terms = ("cache:", "lru:", "index:", "algorithm:", "thread:", "lock:", "pool:")
        violations = []
        for term in implementation_terms:
            if term in source.lower():
                violations.append(f"outcome.py contains implementation field '{term}'")

        msg = _violation_msg(violations, "ProposalOutcome", "P-10")
        assert not violations, msg


# ── P-11: Proposal Categories Represent Cognitive Intent ────────────────────

class TestProposalCategoryCognitiveIntent:
    """Proposal categories must represent cognitive intent, not implementation."""

    def test_categories_no_implementation_names(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "proposal" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        implementation_terms = (
            "CACHE_", "INDEX_", "ALGORITHM_", "THREAD_", "LOCK_", "POOL_",
            "DATABASE_", "SQL_", "QUERY_", "SCHEMA_", "TABLE_",
        )

        violations = []
        for term in implementation_terms:
            if term in source:
                violations.append(f"enums.py contains implementation-oriented category '{term}'")

        msg = _violation_msg(violations, "ProposalCategory", "P-11")
        assert not violations, msg

    def test_categories_represent_cognitive_intent(self):
        """Categories should represent cognitive capabilities, not components."""
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "proposal" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        expected_categories = (
            "KNOWLEDGE_IMPROVEMENT", "LEARNING_IMPROVEMENT", "PLANNING_IMPROVEMENT",
            "RETRIEVAL_IMPROVEMENT", "REFLECTION_IMPROVEMENT", "EVOLUTION_IMPROVEMENT",
            "SAFETY_IMPROVEMENT", "RELIABILITY_IMPROVEMENT", "PERFORMANCE_IMPROVEMENT",
            "EXPLAINABILITY_IMPROVEMENT",
        )

        for cat in expected_categories:
            assert cat in source, f"Missing cognitive intent category: {cat}"


# ── P-12: Proposal Models Are Immutable Domain Objects ──────────────────────

class TestProposalImmutableDomain:
    """Proposal models must be immutable with no runtime behavior."""

    def test_proposal_frozen_dataclass(self):
        src_root = get_src_root()
        proposal_file = src_root / "brain" / "domain" / "proposal" / "proposal.py"
        source = proposal_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "Proposal must be frozen dataclass"

    def test_proposal_space_frozen_dataclass(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "proposal" / "proposal_space.py"
        source = space_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "ProposalSpace must be frozen dataclass"

    def test_no_runtime_methods(self):
        """No async, threading, or runtime methods."""
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            for pattern in ("async def", "threading", "multiprocessing", "subprocess", "time.sleep"):
                if pattern in source:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} contains runtime pattern '{pattern}'")

        msg = _violation_msg(violations, "ProposalModels", "P-12")
        assert not violations, msg


# ── Observation Independence ────────────────────────────────────────────────

class TestObservationIndependence:
    """Observations must remain immutable regardless of proposals."""

    def test_proposal_no_observation_mutation(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            if "observation" in source and ("modify" in source or "update" in source or "change" in source):
                if "def " in source and ("modify" in source or "update" in source or "change" in source):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} may contain observation mutation")

        msg = _violation_msg(violations, "ProposalModels", "P-6")
        assert not violations, msg


# ── No Runtime/Application Coupling ──────────────────────────────────────────

class TestNoRuntimeCoupling:
    """Proposal models must not have runtime or application dependencies."""

    def test_no_runtime_imports(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain.runtime") or imp.startswith("brain.application") or imp.startswith("brain.adapter"):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProposalModels", "RuntimeIsolation")
        assert not violations, msg