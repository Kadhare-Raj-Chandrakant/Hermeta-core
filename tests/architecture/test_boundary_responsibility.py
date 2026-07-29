"""Boundary Responsibility Audit Tests.

Detects responsibility ownership violations:
  - Workflow creating cognitive objects
  - UseCase performing cognitive algorithms or direct repo access
  - Bridge importing/using engines
  - Planner holding transaction or persistence logic
  - Executor creating plans
  - Reflection executing evolution
  - Repository leaking semantic reasoning
"""

from pathlib import Path
from tests.architecture.helpers import (
    get_src_root,
    get_imports,
    has_forbidden_dependencies,
    get_class_method_names,
    find_ast_calls_by_name,
)


def _violation_msg(violations: list[str], component: str, rule: str) -> str:
    if not violations:
        return ""
    lines = [f"[RULE {rule}] {component} responsibility violation:"]
    lines.extend(f"  - {v}" for v in violations)
    return "\n".join(lines)


# ── Rule 1: BrainWorkflow ──────────────────────────────────────────────

class TestWorkflowResponsibility:
    """BrainWorkflow must coordinate only — no cognitive domain objects, no strategy."""

    COGNITIVE_CLASSES = {
        "Goal", "Action", "Plan", "Dependency", "Blocker",
        "EvolutionPlan", "EvolutionOperation", "EvolutionContext",
        "EvolutionRecord", "PlanningEngine", "EvolutionPlanner",
        "EvolutionExecutor", "EvolutionUseCase",
    }

    def test_does_not_instantiate_cognitive_domain_objects(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        calls = find_ast_calls_by_name(file_path, self.COGNITIVE_CLASSES)
        violations = [
            f"line {lineno}: instantiates {name}"
            for lineno, expr, name in calls
        ]
        msg = _violation_msg(violations, "BrainWorkflow", "1")
        assert not violations, msg

    def test_does_not_import_cognitive_engines(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        forbidden = (
            "brain.planning.planner",
            "brain.planning.goal",
            "brain.planning.action",
            "brain.planning.plan",
            "brain.evolution.planning",
            "brain.evolution.executor",
            "brain.reflection.engine",
            "brain.learning.coordinator",
        )
        violations = has_forbidden_dependencies(file_path, forbidden)
        msg = _violation_msg(violations, "BrainWorkflow", "1")
        assert not violations, msg

    def test_communicates_only_through_usecases(self):
        """Workflow imports use cases, bridges, session, domain — not engines directly."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        imports = get_imports(file_path)
        brain_imports = {i for i in imports if i.startswith("brain.")}
        forbidden_prefixes = (
            "brain.planning",
            "brain.evolution.planning",
            "brain.evolution.executor",
            "brain.reflection.engine",
            "brain.learning.coordinator",
            "brain.execution.executor",
        )
        violations = [
            f"imports {i}" for i in sorted(brain_imports)
            if any(i.startswith(p) for p in forbidden_prefixes)
        ]
        msg = _violation_msg(violations, "BrainWorkflow", "1")
        assert not violations, msg


# ── Rule 2: UseCases ───────────────────────────────────────────────────

class TestUseCaseResponsibility:
    """UseCases orchestrate and translate — no cognitive decisions, no direct repo mutation."""

    REPO_MUTATION_METHODS = {
        "add_version", "replace_version", "create_transition",
        "create_conflict", "create_identity", "save_execution_record",
    }

    USE_CASE_FILES = [
        ("planning", "PlanningUseCase"),
        ("execution", "ExecutionUseCase"),
        ("learning", "LearningUseCase"),
        ("reflection", "ReflectionUseCase"),
        ("evolution", "EvolutionUseCase"),
    ]

    def test_usecases_do_not_call_repo_mutation_directly(self):
        """UseCase methods must not call repo mutation methods directly on repository objects."""
        src_root = get_src_root()
        violations = []
        for filename, label in self.USE_CASE_FILES:
            file_path = src_root / "brain" / "application" / "usecases" / f"{filename}.py"
            if not file_path.exists():
                continue
            calls = find_ast_calls_by_name(file_path, self.REPO_MUTATION_METHODS)
            for lineno, expr, name in calls:
                # Allow UoW method calls (begin/commit/rollback) — those are orchestration
                if name == "save_execution_record":
                    continue
                violations.append(f"{label} line {lineno}: calls repo mutation {name}")
        msg = _violation_msg(violations, "UseCases", "2")
        assert not violations, msg

    def test_usecases_do_not_import_runtime_or_adapter(self):
        """Re-verify use cases don't depend on runtime or adapters (from A.2)."""
        src_root = get_src_root()
        forbidden = ("brain.runtime", "brain.adapter")
        violations = []
        for filename, label in self.USE_CASE_FILES:
            file_path = src_root / "brain" / "application" / "usecases" / f"{filename}.py"
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, forbidden)
            for v in file_violations:
                violations.append(f"{label} imports {v}")
        msg = _violation_msg(violations, "UseCases", "2")
        assert not violations, msg


# ── Rule 3: Bridges ────────────────────────────────────────────────────

class TestBridgeResponsibility:
    """Bridges translate DTOs — no engine imports, no decisions, no side effects."""

    BRIDGE_FILES = [
        ("reflection_evolution", "ReflectionEvolutionBridge"),
        ("execution_learning", "ExecutionLearningMapper"),
    ]

    def test_bridges_do_not_import_engines(self):
        src_root = get_src_root()
        bridge_dir = src_root / "brain" / "application" / "bridges"
        forbidden = (
            "brain.planning",
            "brain.reflection.engine",
            "brain.evolution.planning",
            "brain.evolution.executor",
            "brain.evolution.evolution",
            "brain.learning.coordinator",
            "brain.execution.executor",
            "brain.repositories",
        )
        violations = []
        for py_file in bridge_dir.rglob("*.py"):
            rel = py_file.relative_to(src_root)
            file_violations = has_forbidden_dependencies(py_file, forbidden)
            for v in file_violations:
                violations.append(f"{rel} imports {v}")
        msg = _violation_msg(violations, "Bridges", "3")
        assert not violations, msg

    def test_bridges_import_only_models_and_dtos(self):
        """Bridge files should only import from brain.application.usecases.models and standard library."""
        src_root = get_src_root()
        bridge_dir = src_root / "brain" / "application" / "bridges"
        violations = []
        for py_file in bridge_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            rel = py_file.relative_to(src_root)
            imports = get_imports(py_file)
            brain_imports = {i for i in imports if i.startswith("brain.")}
            for imp in brain_imports:
                if not imp.startswith("brain.application.usecases.models"):
                    violations.append(f"{rel} imports {imp} (only models allowed)")
        msg = _violation_msg(violations, "Bridges", "3")
        assert not violations, msg


# ── Rule 4: Planner Purity ─────────────────────────────────────────────

class TestPlannerResponsibility:
    """Planners reason and generate plans — no persistence, no execution."""

    FORBIDDEN_DEPENDENCIES = (
        "brain.repositories",
        "brain.infrastructure",
        "brain.execution",
    )

    def test_evolution_planner_no_persistence_or_execution_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "planning.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
        msg = _violation_msg(violations, "EvolutionPlanner", "4")
        assert not violations, msg

    def test_planning_engine_no_persistence_or_execution_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "planning" / "planner.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_DEPENDENCIES)
        msg = _violation_msg(violations, "PlanningEngine", "4")
        assert not violations, msg

    def test_planners_do_not_import_transaction_modules(self):
        """Planners must not import transaction/unit-of-work abstractions."""
        src_root = get_src_root()
        forbidden = ("unit_of_work", "EvolutionUnitOfWork")
        planner_files = [
            src_root / "brain" / "evolution" / "planning.py",
            src_root / "brain" / "planning" / "planner.py",
        ]
        violations = []
        for file_path in planner_files:
            if not file_path.exists():
                continue
            for token in forbidden:
                source = file_path.read_text(encoding="utf-8")
                if token in source:
                    rel = file_path.relative_to(src_root)
                    violations.append(f"{rel} contains {token}")
        msg = _violation_msg(violations, "Planners", "4")
        assert not violations, msg


# ── Rule 5: Executor Responsibility ────────────────────────────────────

class TestExecutorResponsibility:
    """Executor applies plans — no planning, no strategy creation."""

    def test_executor_does_not_import_planning(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        forbidden = ("brain.planning", "brain.evolution.planning")
        violations = has_forbidden_dependencies(file_path, forbidden)
        msg = _violation_msg(violations, "EvolutionExecutor", "5")
        assert not violations, msg

    def test_executor_does_not_create_plans(self):
        """Executor must not instantiate EvolutionPlan in its own code."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        calls = find_ast_calls_by_name(file_path, {"EvolutionPlan", "EvolutionOperation"})
        violations = [
            f"line {lineno}: creates {name}"
            for lineno, expr, name in calls
        ]
        msg = _violation_msg(violations, "EvolutionExecutor", "5")
        assert not violations, msg

    def test_executor_does_not_import_transaction_boundary(self):
        """Executor must not import UoW — it does not own transactions."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        source = file_path.read_text(encoding="utf-8")
        if "EvolutionUnitOfWork" in source or "unit_of_work" in source:
            violations = ["EvolutionExecutor references unit_of_work or EvolutionUnitOfWork"]
            msg = _violation_msg(violations, "EvolutionExecutor", "5")
            assert False, msg


# ── Rule 6: Reflection Responsibility ──────────────────────────────────

class TestReflectionResponsibility:
    """Reflection analyzes — no evolution execution, no mutation."""

    def test_reflection_engine_does_not_import_evolution_execution(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "reflection" / "engine.py"
        forbidden = (
            "brain.evolution.executor",
            "brain.evolution.evolution",
            "brain.evolution.evolution_record",
            "brain.evolution.evolution_plan",
        )
        violations = has_forbidden_dependencies(file_path, forbidden)
        msg = _violation_msg(violations, "ReflectionEngine", "6")
        assert not violations, msg

    def test_reflection_detectors_do_not_import_evolution(self):
        """Reflection detectors must stay in brain.reflection and brain.domain."""
        src_root = get_src_root()
        detector_dir = src_root / "brain" / "reflection" / "detectors"
        if not detector_dir.exists():
            return
        forbidden = ("brain.evolution", "brain.application")
        violations = []
        for py_file in detector_dir.rglob("*.py"):
            file_violations = has_forbidden_dependencies(py_file, forbidden)
            for v in file_violations:
                rel = py_file.relative_to(src_root)
                violations.append(f"{rel} imports {v}")
        msg = _violation_msg(violations, "ReflectionDetectors", "6")
        assert not violations, msg


# ── Rule 7: Repository Semantic Leakage ────────────────────────────────

class TestRepositoryResponsibility:
    """Repositories persist — no semantic reasoning, no domain logic."""

    SEMANTIC_NAME_PATTERNS = (
        "merge", "resolve", "infer", "reason", "decide",
        "analyze", "suggest", "recommend", "optimize",
        "consolidate", "adjudicate", "judge", "weigh",
        "prioritize", "strategize", "interpret",
    )

    def test_repository_methods_are_persistence_primitives(self):
        """Repository methods must not have semantic reasoning names."""
        src_root = get_src_root()
        repo_files = [
            src_root / "brain" / "repositories" / "base.py",
            src_root / "brain" / "repositories" / "evolution_base.py",
            src_root / "brain" / "repositories" / "memory.py",
        ]
        violations = []
        for file_path in repo_files:
            if not file_path.exists():
                continue
            class_methods = get_class_method_names(file_path)
            for class_name, method_name in class_methods:
                for pattern in self.SEMANTIC_NAME_PATTERNS:
                    if method_name.startswith(pattern):
                        rel = file_path.relative_to(src_root)
                        violations.append(
                            f"{rel}.{class_name}.{method_name} starts with '{pattern}'"
                        )
        msg = _violation_msg(violations, "Repositories", "7")
        assert not violations, msg

    def test_repository_methods_do_not_contain_cognitive_keywords(self):
        """Source of repository methods must not contain cognitive action keywords."""
        src_root = get_src_root()
        repo_files = [
            src_root / "brain" / "repositories" / "base.py",
            src_root / "brain" / "repositories" / "evolution_base.py",
            src_root / "brain" / "repositories" / "memory.py",
        ]
        cognitive_keywords = {
            "merge", "resolve_conflict", "infer", "reason_about",
            "decide", "analyze", "suggest", "recommend", "optimize",
            "consolidate", "heuristic", "strategy",
        }
        violations = []
        for file_path in repo_files:
            if not file_path.exists():
                continue
            source = file_path.read_text(encoding="utf-8")
            class_methods = get_class_method_names(file_path)
            for class_name, method_name in class_methods:
                for kw in cognitive_keywords:
                    if kw in method_name:
                        rel = file_path.relative_to(src_root)
                        violations.append(
                            f"{rel}.{class_name}.{method_name} contains '{kw}'"
                        )
        msg = _violation_msg(violations, "Repositories (cognitive keywords)", "7")
        assert not violations, msg
