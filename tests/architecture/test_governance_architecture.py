"""Governance Architecture Verification Tests.

Verifies the B.5 Governance domain models comply with constitutional laws G-1 through G-23.
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


# ── G-1, G-2, G-4: Domain Purity & No Forbidden Imports ───────────────────

class TestGovernanceDomainPurity:
    """Governance models must remain in domain layer with zero forbidden dependencies."""

    GOVERNANCE_FILES = [
        "enums.py",
        "governance_decision.py",
        "decision_context.py",
        "governance_history.py",
        "governance_policy.py",
        "governance_rationale.py",
        "governance_finding.py",
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

    def test_governance_models_no_forbidden_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for filename in self.GOVERNANCE_FILES:
            file_path = governance_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "GovernanceDomain", "G-1/G-2/G-4/G-11/G-12")
        assert not violations, msg


# ── G-3, G-11, G-12: Read-Only & No Mutation ──────────────────────────────

class TestGovernanceReadOnlyDesign:
    """Governance models must not contain mutation, execution, or evaluation methods."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
        "optimize", "filter", "rank", "sort", "choose", "pick",
        "evaluate", "score", "compare", "judge", "prefer",
    )

    def test_governance_models_no_mutation_methods(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "GovernanceModels", "G-11/G-12")
        assert not violations, msg


# ── G-1, G-2, G-4: No Evaluation/Execution/Decision Logic in Governance ───

class TestGovernanceNoEvaluationLogic:
    """Governance must not contain evaluation, execution, or proposal logic."""

    def test_no_evaluation_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "G-1/G-2")
        assert not violations, msg

    def test_no_execution_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "execution" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "G-4")
        assert not violations, msg

    def test_no_proposal_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "proposal" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "G-3")
        assert not violations, msg


# ── G-5, G-6: Decision References Evidence and Policies ────────────────────

class TestGovernanceDecisionReferences:
    """GovernanceDecision must reference evidence and policies explicitly."""

    def test_decision_has_evaluation_id(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "evaluation_id" in source, "GovernanceDecision missing evaluation_id"

    def test_decision_has_rationale_id(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "rationale_id" in source, "GovernanceDecision missing rationale_id"

    def test_decision_has_policy_ids(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "GovernanceDecision missing policy_ids"

    def test_decision_context_has_evaluation_ids(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "evaluation_id" in source, "DecisionContext missing evaluation_id"

    def test_decision_context_has_policy_ids(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "DecisionContext missing policy_ids"

    def test_decision_context_has_constitutional_version(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "constitutional_version" in source, "DecisionContext missing constitutional_version"


# ── G-7: Governance Deterministic ──────────────────────────────────────────

class TestGovernanceDeterministic:
    """Governance decisions must be deterministic."""

    def test_decision_immutable(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "GovernanceDecision must be frozen dataclass"

    def test_history_immutable(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "governance" / "governance_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "GovernanceHistory must be frozen dataclass"


# ── G-8: Governance May Defer Decisions ────────────────────────────────────

class TestGovernanceDeferral:
    """Governance may defer decisions via DEFERRED state."""

    def test_decision_state_has_deferred(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "governance" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        assert "DEFERRED" in source, "DecisionState missing DEFERRED"


# ── G-9: Rejected Decisions Immutable ──────────────────────────────────────

class TestGovernanceRejectedImmutable:
    """Rejected decisions remain immutable via supersession."""

    def test_rejected_state_exists(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "governance" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        assert "REJECTED" in source, "DecisionState missing REJECTED"


# ── G-10: Every Decision Explainable ───────────────────────────────────────

class TestGovernanceExplainable:
    """Every decision must be explainable through rationale."""

    def test_rationale_model_exists(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        assert rationale_file.exists(), "GovernanceRationale model missing"

    def test_rationale_has_explanation(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "explanation" in source, "GovernanceRationale missing explanation"

    def test_rationale_has_constitutional_basis(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "constitutional_basis" in source, "GovernanceRationale missing constitutional_basis"


# ── G-11: Governance Never Mutates Evaluation ──────────────────────────────

class TestGovernanceNoEvaluationMutation:
    """Governance must not mutate Evaluation."""

    def test_no_evaluation_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "G-11")
        assert not violations, msg


# ── G-12: Governance Never Mutates Proposal ────────────────────────────────

class TestGovernanceNoProposalMutation:
    """Governance must not mutate Proposal."""

    def test_no_proposal_imports(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "proposal" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "G-12")
        assert not violations, msg


# ── G-13: One Active Decision Per Evaluation ───────────────────────────────

class TestGovernanceOneDecisionPerEvaluation:
    """Governance produces one active decision per evaluation."""

    def test_decision_has_evaluation_id(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "evaluation_id" in source, "GovernanceDecision missing evaluation_id"


# ── G-14: Decision History Immutable ────────────────────────────────────────

class TestGovernanceHistoryImmutable:
    """Decision history is immutable — supersession creates new record."""

    def test_history_immutable(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "governance" / "governance_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "GovernanceHistory must be frozen dataclass"

    def test_history_has_superseded(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "governance" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        assert "SUPERSEDED" in source, "DecisionState missing SUPERSEDED"

    def test_history_append_only(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "governance" / "governance_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "with_decision" in source, "GovernanceHistory missing with_decision method"


# ── G-15: Constitution Overrides Optimization ───────────────────────────────

class TestGovernanceConstitutionOverrides:
    """Governance enforces constitutional policy over optimization."""

    def test_policy_category_constitutional(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "governance" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")
        # Policies should be constitutional categories
        for cat in ("ARCHITECTURAL_INTEGRITY", "STATE_OWNERSHIP", "DEPENDENCY_DIRECTION",
                    "TRANSACTION_BOUNDARIES", "FAILURE_ISOLATION", "RECOVERY_OWNERSHIP",
                    "CONTRACT_COMPLIANCE", "EVOLUTION_SAFETY"):
            assert cat in source, f"PolicyCategory missing {cat}"


# ── G-16: Governance Never Bypasses Constitutional Policy ──────────────────

class TestGovernancePolicyEnforcement:
    """Governance never bypasses constitutional policy."""

    def test_decision_context_requires_policy_ids(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "DecisionContext missing policy_ids"


# ── G-17: Governance Never Invents Evidence ─────────────────────────────────

class TestGovernanceEvidenceTraceability:
    """Governance must not invent evidence; must trace to existing objects."""

    def test_rationale_references_evidence(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "supporting_evidence_ids" in source, "GovernanceRationale missing supporting_evidence_ids"


# ── G-18: Governance Owns Decisions Only ────────────────────────────────────

class TestGovernanceOwnsDecisionsOnly:
    """Governance owns decisions only; execution belongs elsewhere."""

    def test_no_execution_fields(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")

        execution_terms = ("execution_plan", "execution:", "run:", "execute:")
        violations = []
        for term in execution_terms:
            if term in source:
                violations.append(f"governance_decision.py contains execution field '{term}'")

        msg = _violation_msg(violations, "GovernanceDecision", "G-18")
        assert not violations, msg


# ── G-19: Governance Never Performs Optimization ────────────────────────────

class TestGovernanceNoOptimization:
    """Governance never performs optimization."""

    def test_no_optimization_methods(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            for pattern in ("optimize", "optimal", "best_score", "maximize", "minimize"):
                if pattern in source.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} contains optimization pattern '{pattern}'")

        msg = _violation_msg(violations, "GovernanceModels", "G-19")
        assert not violations, msg


# ── G-20: Decision and Rationale Separate ──────────────────────────────────

class TestGovernanceDecisionRationaleSeparation:
    """Decision and Rationale are separate constitutional objects."""

    def test_decision_separate_from_rationale(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "rationale_id" in source, "GovernanceDecision missing rationale_id"

        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "rationale_id" in source, "GovernanceRationale missing rationale_id"

    def test_rationale_has_no_state(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "state:" not in source, "GovernanceRationale must not have state field"
        assert "DecisionState" not in source, "GovernanceRationale must not import DecisionState"


# ── G-21: Policies Immutable ─────────────────────────────────────────────────

class TestGovernancePoliciesImmutable:
    """Policies are immutable constitutional rules."""

    def test_policy_immutable(self):
        src_root = get_src_root()
        policy_file = src_root / "brain" / "domain" / "governance" / "governance_policy.py"
        source = policy_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "GovernancePolicy must be frozen dataclass"


# ── G-22: Governance Deterministic ───────────────────────────────────────────

class TestGovernanceDeterministicOutcomes:
    """Identical inputs always produce identical governance outcomes."""

    def test_all_models_frozen(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        for py_file in governance_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "enums.py"):
                continue
            source = py_file.read_text(encoding="utf-8")
            assert "frozen=True" in source, f"{py_file.name} must be frozen dataclass"


# ── G-23: Governance Never Creates Constitutional Rules ──────────────────────

class TestGovernanceNeverCreatesRules:
    """Governance never creates constitutional rules; only applies existing ones."""

    def test_no_policy_creation_methods(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            for pattern in ("create_policy", "new_policy", "modify_policy", "amend_constitution"):
                if pattern in source.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} contains policy creation pattern '{pattern}'")

        msg = _violation_msg(violations, "GovernanceModels", "G-23")
        assert not violations, msg


# ── Authority vs Reasoning Separation ────────────────────────────────────────

class TestAuthorityReasoningSeparation:
    """GovernanceDecision (authority) and GovernanceRationale (reasoning) must be separate."""

    def test_decision_has_no_reasoning_fields(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")

        # Check for actual field definitions, not docstring mentions
        # Look for field definitions like "evidence:" or "evidence ="
        reasoning_fields = ("evidence:", "reasoning:", "analysis:", "assessment:", "evaluation:", "judgment:")
        violations = []
        for term in reasoning_fields:
            if f" {term}" in source or f"{term} " in source or f"={term}" in source:
                violations.append(f"governance_decision.py contains reasoning field '{term}'")

        msg = _violation_msg(violations, "GovernanceDecision", "Authority/Reasoning")
        assert not violations, msg

    def test_rationale_has_no_authority(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")

        authority_terms = ("state:", "approved", "rejected", "decision_state", "approved:", "rejected:")
        violations = []
        for term in authority_terms:
            if term in source.lower():
                violations.append(f"governance_rationale.py contains authority field '{term}'")

        msg = _violation_msg(violations, "GovernanceRationale", "Authority/Reasoning")
        assert not violations, msg


# ── DecisionContext Verification ────────────────────────────────────────────

class TestDecisionContextVerification:
    """DecisionContext restricts Governance inputs to constitutional set."""

    def test_context_only_allowed_inputs(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")

        required = ("evaluation_id", "policy_ids", "constitutional_version")
        for field in required:
            assert field in source, f"DecisionContext missing {field}"

    def test_context_no_runtime(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")

        # Check for actual field definitions, not docstring mentions
        forbidden = ("runtime:", "repository:", "execution:", "adapter:", "application:")
        violations = []
        for term in forbidden:
            if f" {term}" in source or f"{term} " in source or f"={term}" in source:
                violations.append(f"DecisionContext contains forbidden field '{term}'")

        msg = _violation_msg(violations, "DecisionContext", "ContextVerification")
        assert not violations, msg


# ── GovernancePolicy Verification ────────────────────────────────────────────

class TestGovernancePolicyVerification:
    """GovernancePolicy is immutable constitutional rule."""

    def test_policy_has_governing_principle(self):
        src_root = get_src_root()
        policy_file = src_root / "brain" / "domain" / "governance" / "governance_policy.py"
        source = policy_file.read_text(encoding="utf-8")
        assert "governing_principle" in source, "GovernancePolicy missing governing_principle"

    def test_policy_has_category(self):
        src_root = get_src_root()
        policy_file = src_root / "brain" / "domain" / "governance" / "governance_policy.py"
        source = policy_file.read_text(encoding="utf-8")
        assert "category" in source, "GovernancePolicy missing category"


# ── GovernanceHistory Verification ──────────────────────────────────────────

class TestGovernanceHistoryVerification:
    """GovernanceHistory is immutable append-only record."""

    def test_history_append_only(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "governance" / "governance_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "with_decision" in source, "GovernanceHistory missing with_decision method"

    def test_history_has_constitutional_version(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "governance" / "governance_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "constitutional_version" in source, "GovernanceHistory missing constitutional_version"


# ── Explainability Chain Verification ────────────────────────────────────────

class TestExplainabilityChain:
    """Every decision must trace back through full chain."""

    def test_decision_has_rationale_id(self):
        src_root = get_src_root()
        decision_file = src_root / "brain" / "domain" / "governance" / "governance_decision.py"
        source = decision_file.read_text(encoding="utf-8")
        assert "rationale_id" in source, "GovernanceDecision missing rationale_id"

    def test_rationale_has_findings(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "governance" / "governance_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "findings" in source, "GovernanceRationale missing findings"

    def test_findings_reference_policies(self):
        src_root = get_src_root()
        finding_file = src_root / "brain" / "domain" / "governance" / "governance_finding.py"
        source = finding_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "GovernanceFinding missing policy_ids"

    def test_decision_context_has_evaluation_ids(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "governance" / "decision_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "evaluation_id" in source, "DecisionContext missing evaluation_id"


# ── Dependency Verification ──────────────────────────────────────────────────

class TestGovernanceDependencyDirection:
    """Governance depends on Evaluation/Proposal/Problem/Hypothesis/Observation only."""

    def test_governance_allowed_dependencies_only(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain."):
                    allowed = (
                        "brain.domain",
                        "brain.domain.evaluation",
                        "brain.domain.proposal",
                        "brain.domain.problem",
                        "brain.domain.observation",
                        "brain.domain.governance",
                    )
                    if not any(imp.startswith(a) for a in allowed):
                        rel = py_file.relative_to(src_root)
                        violations = [f"{rel} imports disallowed dependency: {imp}"]
                        msg = _violation_msg(violations, "GovernanceModels", "DependencyDirection")
                        assert False, msg

    def test_no_evaluation_imports_in_governance(self):
        src_root = get_src_root()
        governance_dir = src_root / "brain" / "domain" / "governance"

        violations = []
        for py_file in governance_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "GovernanceModels", "DependencyDirection")
        assert not violations, msg