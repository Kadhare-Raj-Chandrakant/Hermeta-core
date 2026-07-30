"""Authorization Architecture Verification Tests.

Verifies the B.6 Authorization domain models comply with constitutional laws A-1 through A-16.
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


# ── A-1, A-2, A-3, A-4, A-5: Domain Purity & Separation ────────────────────

class TestAuthorizationDomainPurity:
    """Authorization models must remain in domain layer with zero forbidden dependencies."""

    AUTHORIZATION_FILES = [
        "enums.py",
        "authorization_record.py",
        "authorization_context.py",
        "authorization_history.py",
        "authorization_constraint.py",
        "authorization_rationale.py",
        "authorization_token.py",
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

    def test_authorization_models_no_forbidden_imports(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for filename in self.AUTHORIZATION_FILES:
            file_path = authorization_dir / filename
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
            for v in file_violations:
                rel = file_path.relative_to(src_root)
                violations.append(f"{rel} imports {v}")

        msg = _violation_msg(violations, "AuthorizationDomain", "A-1/A-2/A-3/A-4/A-5")
        assert not violations, msg


# ── A-6, A-7, A-8: Read-Only & Immutable Design ────────────────────────────

class TestAuthorizationImmutableDesign:
    """Authorization models must be immutable and deterministic."""

    MUTATION_PATTERNS = (
        "create", "mutate", "update", "delete", "modify", "change",
        "execute", "run", "perform", "apply", "commit", "save",
        "recommend", "suggest", "propose", "decide", "approve",
        "reject", "trigger", "emit", "publish",
        "generate", "build", "construct", "produce",
        "optimize", "filter", "rank", "sort", "choose", "pick",
        "evaluate", "score", "compare", "judge", "prefer",
        "authorize", "authorize_", "grant", "revoke",
    )

    def test_authorization_models_no_mutation_methods(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
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

        msg = _violation_msg(violations, "AuthorizationModels", "A-6/A-7/A-8")
        assert not violations, msg

    def test_all_models_frozen_dataclass(self):
        """All authorization models must be frozen dataclasses."""
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        for py_file in authorization_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "enums.py"):
                continue
            source = py_file.read_text(encoding="utf-8")
            assert "frozen=True" in source, f"{py_file.name} must be frozen dataclass"


# ── A-3, A-4, A-5: No Evaluation/Governance/Execution Logic ────────────────

class TestAuthorizationNoEvaluationGovernanceExecution:
    """Authorization must not contain evaluation, governance, or execution logic."""

    def test_no_evaluation_imports(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "evaluation" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "AuthorizationModels", "A-3")
        assert not violations, msg

    def test_no_governance_imports(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "governance" in imp.lower() or "decision" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "AuthorizationModels", "A-4")
        assert not violations, msg

    def test_no_execution_imports(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "execution" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "AuthorizationModels", "A-5")
        assert not violations, msg


# ── A-1, A-2: Authorization Owns Permission Only ───────────────────────────

class TestAuthorizationOwnsPermissionOnly:
    """Authorization must own permission only — no evaluation, governance, execution."""

    def test_authorization_record_has_only_permission_fields(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")

        # Must have these fields
        required = (
            "authorization_id", "governance_decision_id", "state",
            "rationale_id", "issued_at", "constitutional_version", "superseded_by"
        )
        for field in required:
            assert field in source, f"AuthorizationRecord missing {field}"

        # Must NOT have these fields (check field definitions with colon)
        forbidden = (
            "execution_metadata:", "runtime:", "scheduling:", "retries:",
            "workflow_state:", "repository:", "planning:", "execution_plan:",
        )
        violations = []
        for field in forbidden:
            if field in source:
                violations.append(f"AuthorizationRecord contains forbidden field {field}")

        msg = _violation_msg(violations, "AuthorizationRecord", "A-1/A-2")
        assert not violations, msg


# ── A-9: Traceability Preserved ────────────────────────────────────────────

class TestAuthorizationTraceability:
    """Authorization must preserve traceability to GovernanceDecision."""

    def test_record_has_governance_decision_id(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")
        assert "governance_decision_id" in source, "AuthorizationRecord missing governance_decision_id"

    def test_context_has_governance_decision_id(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "authorization" / "authorization_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "governance_decision_id" in source, "AuthorizationContext missing governance_decision_id"

    def test_token_references_authorization_record(self):
        src_root = get_src_root()
        token_file = src_root / "brain" / "domain" / "authorization" / "authorization_token.py"
        source = token_file.read_text(encoding="utf-8")
        assert "authorization_record_id" in source, "AuthorizationToken missing authorization_record_id"

    def test_history_references_records(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "authorization" / "authorization_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "authorization_record_ids" in source, "AuthorizationHistory missing authorization_record_ids"


# ── A-10: Never Bypasses Governance ────────────────────────────────────────

class TestAuthorizationGovernanceGate:
    """Authorization never bypasses Governance."""

    def test_record_requires_governance_decision(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")
        assert "governance_decision_id" in source, "AuthorizationRecord must require governance_decision_id"


# ── A-11: Never Invents Permission ────────────────────────────────────────

class TestAuthorizationNoInventedPermission:
    """Authorization never invents permission; derives from GovernanceDecision."""

    def test_no_permission_creation_fields(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")

        # Fields that would indicate permission creation (not just granting)
        creation_fields = (
            "create_authorization:", "generate_authorization:", "new_authorization:",
            "authorization_factory:", "builder:",
        )
        violations = []
        for field in creation_fields:
            if field in source:
                violations.append(f"authorization_record.py contains permission creation field '{field}'")

        msg = _violation_msg(violations, "AuthorizationRecord", "A-11")
        assert not violations, msg


# ── A-12: Never Authorizes Constitutional Violations ────────────────────────

class TestAuthorizationConstitutionalSafety:
    """Authorization never authorizes constitutional violations."""

    def test_constraint_model_exists(self):
        src_root = get_src_root()
        constraint_file = src_root / "brain" / "domain" / "authorization" / "authorization_constraint.py"
        assert constraint_file.exists(), "AuthorizationConstraint model missing"

    def test_constraint_has_policy_ids(self):
        src_root = get_src_root()
        constraint_file = src_root / "brain" / "domain" / "authorization" / "authorization_constraint.py"
        source = constraint_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "AuthorizationConstraint missing policy_ids"


# ── A-13: Never Weakens Constitutional Policy ──────────────────────────────

class TestAuthorizationPolicyPreservation:
    """Authorization never weakens constitutional policy."""

    def test_context_requires_policy_ids(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "authorization" / "authorization_context.py"
        source = context_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "AuthorizationContext missing policy_ids"

    def test_constraint_references_policies(self):
        src_root = get_src_root()
        constraint_file = src_root / "brain" / "domain" / "authorization" / "authorization_constraint.py"
        source = constraint_file.read_text(encoding="utf-8")
        assert "policy_ids" in source, "AuthorizationConstraint missing policy_ids"


# ── A-14: Authorization Lifecycle Independent from Execution ──────────────────

class TestAuthorizationLifecycleIndependence:
    """Authorization lifecycle is independent from execution lifecycle."""

    def test_no_execution_fields_in_record(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")

        execution_terms = ("execution_metadata:", "runtime:", "scheduling:", "retries:",
                          "workflow_state:", "execution_plan:", "orchestration:")
        violations = []
        for term in execution_terms:
            if term in source:
                violations.append(f"authorization_record.py contains execution field '{term}'")

        msg = _violation_msg(violations, "AuthorizationRecord", "A-14")
        assert not violations, msg


# ── A-15: Execution Consumes AuthorizationToken Only ────────────────────────

class TestAuthorizationTokenConsumption:
    """Execution must consume AuthorizationToken only."""

    def test_token_contains_only_permission(self):
        src_root = get_src_root()
        token_file = src_root / "brain" / "domain" / "authorization" / "authorization_token.py"
        source = token_file.read_text(encoding="utf-8")

        # Token should have these minimal fields
        required = ("token_id", "authorization_record_id", "issued_at", "constitutional_version")
        for field in required:
            assert field in source, f"AuthorizationToken missing {field}"

        # Token must NOT have execution fields
        forbidden = ("execution:", "runtime:", "scheduling:", "retries:", "workflow:",
                     "orchestration:", "plan:", "execution_plan:", "repository:")
        violations = []
        for term in forbidden:
            if term in source:
                violations.append(f"AuthorizationToken contains execution field '{term}'")

        msg = _violation_msg(violations, "AuthorizationToken", "A-15")
        assert not violations, msg


# ── A-16: Authorization Contains No Execution Metadata ──────────────────────

class TestAuthorizationNoExecutionMetadata:
    """Authorization contains no execution metadata."""

    def test_context_no_execution_fields(self):
        src_root = get_src_root()
        context_file = src_root / "brain" / "domain" / "authorization" / "authorization_context.py"
        source = context_file.read_text(encoding="utf-8")

        forbidden = ("runtime:", "repository:", "execution:", "adapter:", "application:")
        violations = []
        for term in forbidden:
            if f" {term}" in source or f"={term}" in source or f"{term} " in source:
                violations.append(f"AuthorizationContext contains execution field '{term}'")

        msg = _violation_msg(violations, "AuthorizationContext", "A-16")
        assert not violations, msg


# ── A-6, A-7, A-8: Deterministic & Immutable ────────────────────────────────

class TestAuthorizationDeterministic:
    """Authorization is deterministic and immutable."""

    def test_all_models_frozen(self):
        src_root = get_src_root()
        auth_dir = src_root / "brain" / "domain" / "authorization"

        for py_file in auth_dir.glob("*.py"):
            if py_file.name in ("__init__.py", "enums.py"):
                continue
            source = py_file.read_text(encoding="utf-8")
            assert "frozen=True" in source, f"{py_file.name} must be frozen dataclass"


# ── A-8: Supersession Instead of Mutation ──────────────────────────────────

class TestAuthorizationSupersession:
    """Authorization uses supersession, never mutation."""

    def test_record_has_superseded_by(self):
        src_root = get_src_root()
        record_file = src_root / "brain" / "domain" / "authorization" / "authorization_record.py"
        source = record_file.read_text(encoding="utf-8")
        assert "superseded_by" in source, "AuthorizationRecord missing superseded_by"

    def test_history_append_only(self):
        src_root = get_src_root()
        history_file = src_root / "brain" / "domain" / "authorization" / "authorization_history.py"
        source = history_file.read_text(encoding="utf-8")
        assert "with_record" in source, "AuthorizationHistory missing with_record method"


# ── A-14: Authorization Lifecycle Independent from Execution ────────────────

class TestAuthorizationExecutionIndependence:
    """Authorization lifecycle independent from execution lifecycle."""

    def test_authorization_states_no_execution(self):
        src_root = get_src_root()
        enums_file = src_root / "brain" / "domain" / "authorization" / "enums.py"
        source = enums_file.read_text(encoding="utf-8")

        execution_states = ("EXECUTING", "EXECUTED", "RUNNING", "SCHEDULED", "ORCHESTRATING")
        violations = []
        for state in execution_states:
            if state in source:
                violations.append(f"enums.py contains execution state '{state}'")

        msg = _violation_msg(violations, "AuthorizationState", "A-14")
        assert not violations, msg


# ── A-15: Execution Consumes AuthorizationToken Only ───────────────────────

class TestAuthorizationTokenOnly:
    """Execution must consume AuthorizationToken only."""

    def test_token_minimal_fields(self):
        src_root = get_src_root()
        token_file = src_root / "brain" / "domain" / "authorization" / "authorization_token.py"
        source = token_file.read_text(encoding="utf-8")

        # Token should only have minimal fields
        allowed_fields = ("token_id", "authorization_record_id", "issued_at", "constitutional_version")
        for field in allowed_fields:
            assert field in source, f"AuthorizationToken missing {field}"

        # Must NOT have execution metadata
        forbidden = ("execution:", "runtime:", "scheduling:", "retries:", "workflow:",
                     "orchestration:", "plan:", "execution_plan:", "repository:")
        violations = []
        for term in forbidden:
            if term in source:
                violations.append(f"AuthorizationToken contains execution metadata '{term}'")

        msg = _violation_msg(violations, "AuthorizationToken", "A-15")
        assert not violations, msg


# ── A-1 through A-16: Dependency Direction ─────────────────────────────────

class TestAuthorizationDependencyDirection:
    """Authorization depends only on Governance + Domain + Stdlib."""

    def test_authorization_allowed_dependencies_only(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain."):
                    allowed = (
                        "brain.domain",
                        "brain.domain.governance",
                        "brain.domain.evaluation",
                        "brain.domain.proposal",
                        "brain.domain.problem",
                        "brain.domain.observation",
                        "brain.domain.authorization",
                    )
                    if not any(imp.startswith(a) for a in allowed):
                        rel = py_file.relative_to(src_root)
                        violations = [f"{rel} imports disallowed dependency: {imp}"]
                        msg = _violation_msg(violations, "AuthorizationModels", "DependencyDirection")
                        assert False, msg

    def test_no_governance_imports_in_authorization(self):
        """Authorization must NOT import from Governance (one-way: Governance → Authorization)."""
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if "governance" in imp.lower():
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "AuthorizationModels", "DependencyDirection")
        assert not violations, msg

    def test_no_runtime_imports(self):
        src_root = get_src_root()
        authorization_dir = src_root / "brain" / "domain" / "authorization"

        violations = []
        for py_file in authorization_dir.glob("*.py"):
            imports = get_imports(py_file)
            for imp in imports:
                if imp.startswith("brain.runtime") or imp.startswith("brain.application") or imp.startswith("brain.adapter"):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        msg = _violation_msg(violations, "AuthorizationModels", "RuntimeIsolation")
        assert not violations, msg


# ── A-1 through A-16: Explainability and Traceability ──────────────────────

class TestAuthorizationTraceability:
    """Authorization decisions must be fully traceable."""

    def test_rationale_model_exists(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "authorization" / "authorization_rationale.py"
        assert rationale_file.exists(), "AuthorizationRationale model missing"

    def test_rationale_has_explanation(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "authorization" / "authorization_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "explanation" in source, "AuthorizationRationale missing explanation"

    def test_rationale_has_constitutional_basis(self):
        src_root = get_src_root()
        rationale_file = src_root / "brain" / "domain" / "authorization" / "authorization_rationale.py"
        source = rationale_file.read_text(encoding="utf-8")
        assert "constitutional_basis" in source, "AuthorizationRationale missing constitutional_basis"

    def test_constraint_has_description(self):
        src_root = get_src_root()
        constraint_file = src_root / "brain" / "domain" / "authorization" / "authorization_constraint.py"
        source = constraint_file.read_text(encoding="utf-8")
        assert "description" in source, "AuthorizationConstraint missing description"