"""Proposal Evaluation Architecture Verification Tests.

Verifies the B.4 Evaluation domain models comply with constitutional laws E-1 through E-16.
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


# ── E-1, E-2, E-3, E-4, E-5, E-6, E-7, E-11, E-12: Domain Purity ──────────

class TestEvaluationDomainPurity:
    """Evaluation models must remain in domain layer with zero forbidden dependencies."""

    EVALUATION_FILES = [
        "enums.py",
        "tradeoff.py",
        "evidence.py",
        "dimension.py",
        "evaluation.py",
        "evaluation_space.py",
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

    def test_evaluation_models_no_forbidden_imports(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for filename in self.EVALUATION_FILES:
            file_path = evaluation_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "EvaluationDomain", "E-1/E-2/E-3/E-4/E-5/E-6/E-7/E-11/E-12")
        assert not violations, msg


# ── E-6, E-9, E-10, E-11: Read-Only & No Decision/Execution Fields ────────

class TestEvaluationReadOnlyDesign:
    """Evaluation models must not contain decision, execution, or mutation methods."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
        "optimize", "filter", "rank", "sort", "choose", "pick",
    )

    def test_evaluation_models_no_mutation_methods(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for py_file in evaluation_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "EvaluationModels", "E-6/E-9/E-10/E-11")
        assert not violations, msg


# ── E-2, E-6: No Decision/Approval/Scoring Fields ─────────────────────────

class TestEvaluationNoDecisionFields:
    """Evaluation must not contain decision, approval, ranking, or scoring fields."""

    FORBIDDEN_FIELDS = (
        "approved:", "rejected:", "accepted:", "score:", "confidence:",
        "ranking:", "priority:", "severity:", "probability:", "usefulness:",
        "decision:", "decision_id:", "governance:", "execution_plan:",
    )

    def test_evaluation_no_decision_fields(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")

        violations = []
        for forbidden in self.FORBIDDEN_FIELDS:
            if forbidden in source:
                violations.append(f"evaluation.py contains decision field '{forbidden}'")

        msg = _violation_msg(violations, "Evaluation", "E-2/E-6")
        assert not violations, msg


# ── E-4: Evaluation Never Mutates Proposal ────────────────────────────────

class TestEvaluationNoProposalMutation:
    """Evaluation must not reference mutation or execution of proposals."""

    def test_evaluation_no_execution_references(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")

        forbidden = (
            "execution_plan:", "mutation:", "execution:", "mutation:",
            "execution:", "mutation:", "runtime:",
        )

        violations = []
        for forbidden in forbidden:
            if forbidden in source:
                violations.append(f"evaluation.py contains execution reference '{forbidden}'")

        msg = _violation_msg(violations, "Evaluation", "E-4")
        assert not violations, msg


# ── E-5: Evaluation Never Creates Proposal ────────────────────────────────

class TestEvaluationNoProposalCreation:
    """Evaluation must not create proposals (E-5)."""

    def test_evaluation_no_proposal_creation_fields(self):
        """Evaluation must not have fields that create proposals."""
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")

        # Fields that would indicate proposal creation (not just reference)
        creation_fields = (
            "create_proposal:", "generate_proposal:", "new_proposal:",
            "proposal_factory:", "builder:",
        )

        violations = []
        for forbidden in creation_fields:
            if forbidden in source:
                violations.append(f"evaluation.py contains proposal creation field '{forbidden}'")

        msg = _violation_msg(violations, "EvaluationModels", "E-5")
        assert not violations, msg


# ── E-7: Explicit Evidence ─────────────────────────────────────────────────

class TestEvaluationExplicitEvidence:
    """Evaluation conclusions must trace back to explicit evidence."""

    def test_evaluation_has_evidence_ids(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "evidence_ids" in source, "Evaluation missing evidence_ids"

    def test_dimensional_analysis_has_evidence(self):
        src_root = get_src_root()
        dim_file = src_root / "brain" / "domain" / "evaluation" / "dimension.py"
        source = dim_file.read_text(encoding="utf-8")
        assert "evidence" in source, "DimensionalAnalysis missing evidence field"

    def test_evidence_has_traceability(self):
        src_root = get_src_root()
        evidence_file = src_root / "brain" / "domain" / "evaluation" / "evidence.py"
        source = evidence_file.read_text(encoding="utf-8")
        for field in ("observation_ids", "hypothesis_ids", "problem_ids", "proposal_ids"):
            assert field in source, f"EvaluationEvidence missing {field}"


# ── E-8: Explicit Tradeoffs ────────────────────────────────────────────────

class TestEvaluationExplicitTradeoffs:
    """Tradeoffs must be explicit first-class cognitive objects."""

    def test_tradeoff_model_exists(self):
        src_root = get_src_root()
        tradeoff_file = src_root / "brain" / "domain" / "evaluation" / "tradeoff.py"
        assert tradeoff_file.exists(), "Tradeoff model missing"

    def test_tradeoff_has_benefit_cost_dimension(self):
        src_root = get_src_root()
        tradeoff_file = src_root / "brain" / "domain" / "evaluation" / "tradeoff.py"
        source = tradeoff_file.read_text(encoding="utf-8")
        for field in ("benefit", "cost", "dimension"):
            assert field in source, f"Tradeoff missing {field} field"

    def test_evaluation_has_global_tradeoffs(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "global_tradeoffs" in source, "Evaluation missing global_tradeoffs"

    def test_dimensional_analysis_has_tradeoffs(self):
        src_root = get_src_root()
        dim_file = src_root / "brain" / "domain" / "evaluation" / "dimension.py"
        source = dim_file.read_text(encoding="utf-8")
        assert "tradeoff_ids" in source, "DimensionalAnalysis missing tradeoff_ids"


# ── E-9: Evaluation Never Ranks ────────────────────────────────────────────

class TestEvaluationSpaceNoRanking:
    """EvaluationSpace preserves all evaluations — never ranks, filters, selects."""

    FORBIDDEN_METHODS = (
        "rank", "sort", "filter", "select", "choose", "pick", "best",
        "evaluate", "score", "compare", "judge", "prefer",
        "merge", "optimize", "reduce", "eliminate",
    )

    def test_evaluation_space_no_ranking_methods(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "evaluation" / "evaluation_space.py"
        source = space_file.read_text(encoding="utf-8")

        violations = []
        for pattern in self.FORBIDDEN_METHODS:
            if f"def {pattern}" in source:
                violations.append(f"evaluation_space.py contains ranking method 'def {pattern}'")

        msg = _violation_msg(violations, "EvaluationSpace", "E-9/E-10")
        assert not violations, msg


# ── E-10: Evaluation Never Filters ─────────────────────────────────────────

class TestEvaluationSpaceNoFiltering:
    """EvaluationSpace never filters or discards evaluations."""

    def test_evaluation_space_preserves_all(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "evaluation" / "evaluation_space.py"
        source = space_file.read_text(encoding="utf-8")

        # Space should have evaluation_count and proposal_count properties
        assert "evaluation_count" in source, "EvaluationSpace missing evaluation_count"
        assert "proposal_count" in source, "EvaluationSpace missing proposal_count"

        # Should have evaluations_by_proposal for deterministic access
        assert "evaluations_by_proposal" in source, "EvaluationSpace missing evaluations_by_proposal"


# ── E-11: Evaluation Never Approves ────────────────────────────────────────

class TestEvaluationNoApproval:
    """Evaluation never approves, rejects, or accepts."""

    def test_no_approval_fields(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")

        approval_terms = ("approved:", "rejected:", "accepted:", "acceptance:")
        violations = []
        for term in approval_terms:
            if term in source:
                violations.append(f"evaluation.py contains approval field '{term}'")

        msg = _violation_msg(violations, "Evaluation", "E-11")
        assert not violations, msg


# ── E-12: Evaluation Deterministic ─────────────────────────────────────────

class TestEvaluationDeterministic:
    """Same Proposal + Same Context = Same Evaluation."""

    def test_evaluation_immutable(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "Evaluation must be frozen dataclass"

    def test_evaluation_space_immutable(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "evaluation" / "evaluation_space.py"
        source = space_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "EvaluationSpace must be frozen dataclass"


# ── E-13: Comparison ≠ Ranking ─────────────────────────────────────────────

class TestComparativeReasoning:
    """EvaluationSpace supports comparison without ranking."""

    def test_comparison_without_ranking(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "evaluation" / "evaluation_space.py"
        source = space_file.read_text(encoding="utf-8")

        # Should have evaluations_by_proposal for deterministic access
        assert "evaluations_by_proposal" in source

        # Should NOT have ranking/selecting methods
        ranking_terms = ("def rank", "def select", "def choose", "def best", "def worst")
        for term in ranking_terms:
            assert term not in source, f"EvaluationSpace contains ranking method '{term}'"


# ── E-14: Every Proposal Receives Independent Evaluation ──────────────────

class TestIndependentEvaluation:
    """Every proposal must have its own independent evaluation."""

    def test_evaluation_links_proposal(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "proposal_id" in source, "Evaluation missing proposal_id"

    def test_evaluation_space_links_proposals(self):
        src_root = get_src_root()
        space_file = src_root / "brain" / "domain" / "evaluation" / "evaluation_space.py"
        source = space_file.read_text(encoding="utf-8")
        assert "proposal_ids" in source, "EvaluationSpace missing proposal_ids"


# ── E-15: Evaluation History Immutable ──────────────────────────────────────

class TestEvaluationHistoryImmutable:
    """Evaluation history is immutable — superseded, never mutated."""

    def test_evaluation_can_be_superseded(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "superseded_by" in source, "Evaluation missing superseded_by"

    def test_evaluation_state_tracking(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "evaluation" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        assert "SUPERSEDED" in source, "EvaluationState missing SUPERSEDED"


# ── E-16: Evaluation Conclusions Explainable Through Evidence ───────────────

class TestEvaluationExplainable:
    """Evaluation conclusions must be traceable to evidence."""

    def test_evaluation_has_summary_judgment(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "summary_judgment" in source, "Evaluation missing summary_judgment"

    def test_evaluation_has_uncertainties(self):
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "known_uncertainties" in source, "Evaluation missing known_uncertainties"


# ── E-1, E-2, E-3: Independence From Proposal/Decision/Execution ──────────

class TestEvaluationIndependence:
    """Evaluation must not depend on Proposal, Decision, Execution, Governance, Runtime."""

    def test_no_proposal_import(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for py_file in evaluation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "proposal" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "EvaluationModels", "E-1")
        assert not violations, msg

    def test_no_decision_import(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for py_file in evaluation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "decision" in imp.lower() or "governance" in imp.lower() or "approval" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "EvaluationModels", "E-2")
        assert not violations, msg

    def test_no_execution_import(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for py_file in evaluation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "execution" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "EvaluationModels", "E-3")
        assert not violations, msg

    def test_no_runtime_imports(self):
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        violations = []
        for py_file in evaluation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain.runtime") or imp.startswith("brain.application") or imp.startswith("brain.adapter"):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "EvaluationModels", "RuntimeIsolation")
        assert not violations, msg


# ── Tradeoff Architecture ──────────────────────────────────────────────────

class TestTradeoffArchitecture:
    """Tradeoffs are first-class cognitive objects, not flattened text."""

    def test_tradeoff_is_separate_model(self):
        src_root = get_src_root()
        tradeoff_file = src_root / "brain" / "domain" / "evaluation" / "tradeoff.py"
        assert tradeoff_file.exists(), "Tradeoff model missing"

    def test_tradeoff_not_embedded_in_evaluation(self):
        """Tradeoffs must be referenceable independently."""
        src_root = get_src_root()
        eval_file = src_root / "brain" / "domain" / "evaluation" / "evaluation.py"
        source = eval_file.read_text(encoding="utf-8")
        assert "global_tradeoffs" in source and "tuple" in source


# ── EvaluationEvidence Architecture ─────────────────────────────────────────

class TestEvaluationEvidenceArchitecture:
    """EvaluationEvidence is explicit and traceable."""

    def test_evidence_type_enum_exists(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "evaluation" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        assert "EvidenceType" in source

    def test_evidence_references_cognitive_objects(self):
        """Evidence must trace back to Observation/Hypothesis/Problem/Proposal."""
        src_root = get_src_root()
        evidence_file = src_root / "brain" / "domain" / "evaluation" / "evidence.py"
        source = evidence_file.read_text(encoding="utf-8")
        for field in ("observation_ids", "hypothesis_ids", "problem_ids", "proposal_ids"):
            assert field in source, f"EvaluationEvidence missing {field}"


# ── Facts vs Judgments Separation ───────────────────────────────────────────

class TestFactsVsJudgmentsSeparation:
    """Facts and judgments must be separated in dimensional analysis."""

    def test_dimensional_analysis_separates_facts_judgments(self):
        src_root = get_src_root()
        dim_file = src_root / "brain" / "domain" / "evaluation" / "dimension.py"
        source = dim_file.read_text(encoding="utf-8")
        assert "facts" in source, "DimensionalAnalysis missing facts"
        assert "judgments" in source, "DimensionalAnalysis missing judgments"

    def test_facts_and_judgments_separate_fields(self):
        """Facts and judgments must be separate tuple fields."""
        src_root = get_src_root()
        dim_file = src_root / "brain" / "domain" / "evaluation" / "dimension.py"
        source = dim_file.read_text(encoding="utf-8")
        assert "facts:" in source
        assert "judgments:" in source


# ── Proposal Independence ──────────────────────────────────────────────────

class TestProposalIndependence:
    """Proposal must not import Evaluation."""

    def test_proposal_no_evaluation_import(self):
        src_root = get_src_root()
        proposal_dir = src_root / "brain" / "domain" / "proposal"

        violations = []
        for py_file in proposal_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "ProposalModels", "E-1")
        assert not violations, msg


# ── Dependency Direction ────────────────────────────────────────────────────

class TestDependencyDirection:
    """Evaluation depends on Proposal/Problem/Hypothesis/Observation only."""

    def test_evaluation_allowed_dependencies_only(self):
        """Evaluation may import from allowed domain packages."""
        src_root = get_src_root()
        evaluation_dir = src_root / "brain" / "domain" / "evaluation"

        for py_file in evaluation_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain."):
                    allowed = (
                        "brain.domain",
                        "brain.domain.observation",
                        "brain.domain.problem",
                        "brain.domain.proposal",
                        "brain.domain.evaluation",
                    )
                    if not any(imp.startswith(a) for a in allowed):
                        rel = py_file.relative_to(src_root)
                        violations = [f"{rel} imports disallowed dependency: {imp}"]
                        msg = _violation_msg(violations, "EvaluationModels", "DependencyDirection")
                        assert False, msg