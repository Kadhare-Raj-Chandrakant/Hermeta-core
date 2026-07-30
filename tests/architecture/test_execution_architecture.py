"""Execution Architecture Verification Tests.

Verifies the B.7 Execution domain models comply with constitutional laws X-1 through X-23.
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


# ── X-1, X-2, X-3, X-4, X-5, X-6: Domain Purity & Separation ──────────────────

class TestExecutionDomainPurity:
    """Execution models must remain in domain layer with zero forbidden dependencies."""

    EXECUTION_FILES = [
        "enums.py",
        "execution_plan.py",
        "execution_context.py",
        "execution_result.py",
        "execution_artifact.py",
        "execution_failure.py",
        "execution_history.py",
        "execution_receipt.py",
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
        "brain.validation",
        "brain.detection",
        "brain.retrieval",
        "brain.services",
        "brain.observation",
        "brain.hypothesis",
        "brain.problem",
        "brain.proposal",
        "brain.evaluation",
        "brain.governance",
        "brain.authorization",
        "brain.application.usecases",
        "brain.application.workflow",
        "brain.application.bridges",
    )

    def test_execution_models_no_forbidden_imports(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        violations = []
        for filename in self.EXECUTION_FILES:
            file_path = execution_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "ExecutionDomain", "X-21/X-22")
        assert not violations, msg


# ── X-3, X-4, X-5, X-6, X-10, X-18: Read-Only & Immutable ────────────────────

class TestExecutionImmutableDesign:
    """Execution models must be immutable with no reasoning/evaluation/governance methods."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
        "optimize", "filter", "rank", "sort", "choose", "pick",
        "evaluate", "score", "compare", "judge", "prefer",
        "authorize", "authorize_", "grant", "revoke",
        "reason", "reason_", "analyze", "analyze_", "interpret", "interpret_",
        "evaluate", "evaluate_", "diagnose", "diagnose_", "retry", "recover",
        "schedule", "orchestrate", "plan", "replan",
    )

    def test_execution_models_no_mutation_methods(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        violations = []
        for py_file in execution_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "ExecutionModels", "X-3/X-4/X-5/X-6/X-10/X-18")
        assert not violations, msg

    def test_all_models_frozen_dataclass(self):
        """All execution models must be frozen dataclasses."""
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "enums.py"):
                continue
            source = py_file.read_text(encoding="utf-8")
            assert "frozen=True" in source, f"{py_file.name} must be frozen dataclass"


# ── X-1, X-2: Execution Consumes AuthorizationToken Only ────────────────────

class TestExecutionAuthorizationGate:
    """Execution must consume AuthorizationToken only."""

    def test_execution_plan_requires_authorization_token(self):
        src_root = get_src_root()
        plan_file = src_root / "brain" / "domain" / "execution" / "execution_plan.py"
        source = plan_file.read_text(encoding="utf-8")
        assert "authorization_token_id" in source, "ExecutionPlan missing authorization_token_id"

    def test_execution_context_requires_token(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "execution" / "execution_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "authorization_token_id" in source, "ExecutionContext missing authorization_token_id"

    def test_receipt_requires_authorization_token(self):
        src_root = get_src_root()
        receipt_file = src_root / "brain" / "domain" / "execution" / "execution_receipt.py"
        source = receipt_file.read_text(encoding="utf-8")
        assert "authorization_token_id" in source, "ExecutionReceipt missing authorization_token_id"


# ── X-7, X-8, X-9: Determinism & Scope ──────────────────────────────────────

class TestExecutionDeterminismAndScope:
    """Execution is deterministic and never expands scope."""

    def test_execution_plan_immutable(self):
        src_root = get_src_root()
        plan_file = src_root / "brain" / "domain" / "execution" / "execution_plan.py"
        source = plan_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "ExecutionPlan must be frozen dataclass"

    def test_result_no_expansion_fields(self):
        src_root = get_src_root()
        result_file = src_root / "brain" / "domain" / "execution" / "execution_result.py"
        source = result_file.read_text(encoding="utf-8")

        # Result should not have fields that expand scope
        forbidden = ("additional_work:", "expanded_scope:", "extra_operations:", "new_proposal:")
        violations = []
        for term in forbidden:
            if term in source:
                violations.append(f"execution_result.py contains scope expansion field '{term}'")

        msg = _violation_msg(violations, "ExecutionResult", "X-8/X-9")
        assert not violations, msg


# ── X-3, X-4, X-5, X-6: No Reasoning/Evaluation/Governance/Authorization ──────

class TestExecutionNoReasoning:
    """Execution must not reason, evaluate, govern, or authorize."""

    def test_no_reasoning_fields(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            reasoning_terms = ("confidence:", "recommendation:", "reasoning:", "explanation:",
                              "interpretation:", "should:", "optimization:", "strategy:")
            violations = []
            for term in reasoning_terms:
                if term in source.lower():
                    violations.append(f"{py_file.name} contains reasoning field '{term}'")

            msg = _violation_msg(violations, "ExecutionModels", "X-3/X-6")
            assert not violations, msg


# ── X-11, X-12, X-13, X-14: Failure Handling ────────────────────────────────

class TestExecutionFailureHandling:
    """Execution failures are facts only; no retry/recovery reasoning."""

    def test_failure_model_no_retry_fields(self):
        src_root = get_src_root()
        failure_file = src_root / "brain" / "domain" / "execution" / "execution_failure.py"
        source = failure_file.read_text(encoding="utf-8")

        retry_terms = ("retry:", "recovery:", "recommendation:", "advice:", "diagnosis:",
                      "auto_retry:", "automatic_recovery:", "retry_count:")
        violations = []
        for term in retry_terms:
            if term in source.lower():
                violations.append(f"execution_failure.py contains retry/recovery field '{term}'")

        msg = _violation_msg(violations, "ExecutionFailure", "X-11/X-12/X-13")
        assert not violations, msg


# ── X-15, X-16, X-17: Evidence & Facts Only ─────────────────────────────────

class TestExecutionEvidenceOnly:
    """Execution reports observable facts only."""

    def test_result_no_interpretation_fields(self):
        src_root = get_src_root()
        result_file = src_root / "brain" / "domain" / "execution" / "execution_result.py"
        source = result_file.read_text(encoding="utf-8")

        interpretation_terms = ("interpretation:", "confidence:", "probability:", "assessment:",
                               "evaluation:", "judgment:", "opinion:", "prediction:")
        violations = []
        for term in interpretation_terms:
            if term in source.lower():
                violations.append(f"execution_result.py contains interpretation field '{term}'")

        msg = _violation_msg(violations, "ExecutionResult", "X-15/X-16")
        assert not violations, msg

    def test_artifact_model_exists(self):
        src_root = get_src_root()
        artifact_file = src_root / "brain" / "domain" / "execution" / "execution_artifact.py"
        assert artifact_file.exists(), "ExecutionArtifact model missing"

    def test_receipt_model_exists(self):
        src_root = get_src_root()
        receipt_file = src_root / "brain" / "domain" / "execution" / "execution_receipt.py"
        assert receipt_file.exists(), "ExecutionReceipt model missing"


# ── X-18, X-19, X-20: Immutability & Ownership ──────────────────────────────

class TestExecutionOwnershipAndImmutability:
    """Execution owns execution only; history is append-only."""

    def test_history_append_only(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "execution" / "execution_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "frozen=True" in source, "ExecutionHistory must be frozen dataclass"
        assert "with_result" in source, "ExecutionHistory missing with_result method"

    def test_models_frozen(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "enums.py"):
                continue
            source = py_file.read_text(encoding="utf-8")
            assert "frozen=True" in source, f"{py_file.name} must be frozen dataclass"


# ── X-21: Receipt is Proof, Not Reasoning ───────────────────────────────────

class TestExecutionReceiptIsProof:
    """ExecutionReceipt is constitutional proof, not reasoning."""

    def test_receipt_minimal_fields(self):
        src_root = get_src_root()
        receipt_file = src_root / "brain" / "domain" / "execution" / "execution_receipt.py"
        source = receipt_file.read_text(encoding="utf-8")

        required = ("receipt_id", "execution_result_id", "authorization_token_id",
                   "issued_at", "constitutional_version")
        for field in required:
            assert field in source, f"ExecutionReceipt missing {field}"


# ── X-22, X-23: Dependency Direction & Minimality ────────────────────────────

class TestExecutionDependencyDirection:
    """Execution depends only on Authorization + Domain + Stdlib."""

    def test_execution_allowed_dependencies_only(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain."):
                    allowed = (
                        "brain.domain",
                        "brain.domain.authorization",
                        "brain.domain.evaluation",
                        "brain.domain.proposal",
                        "brain.domain.problem",
                        "brain.domain.observation",
                        "brain.domain.execution",
                    )
                    if not any(imp.startswith(a) for a in allowed):
                        rel = py_file.relative_to(src_root)
                        violations = [f"{rel} imports disallowed dependency: {imp}"]
                        msg = _violation_msg(violations, "ExecutionModels", "X-22")
                        assert False, msg

    def test_no_authorization_imports_in_execution(self):
        """Execution may depend on Authorization but NOT Governance/Evaluation/Proposal."""
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if any(x in imp.lower() for x in ("governance", "evaluation", "proposal",
                                                  "problem", "hypothesis", "observation")):
                    rel = py_file.relative_to(src_root)
                    violations = [f"{rel} imports forbidden dependency: {imp}"]
                    msg = _violation_msg(violations, "ExecutionModels", "X-22")
                    assert False, msg

    def test_no_runtime_application_imports(self):
        src_root = get_src_root()
        execution_dir = src_root / "brain" / "domain" / "execution"

        for py_file in execution_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain.runtime") or imp.startswith("brain.application") or imp.startswith("brain.adapter"):
                    rel = py_file.relative_to(src_root)
                    violations = [f"{rel} imports runtime/application/adapter: {imp}"]
                    msg = _violation_msg(violations, "ExecutionModels", "RuntimeIsolation")
                    assert False, msg