"""Dependency Direction Audit Tests.

Verifies architectural layer boundaries cannot drift over time.

Application → Cognitive Modules → Infrastructure

Rules verified:
  Rule 1: EvolutionPlanner dependencies
  Rule 2: EvolutionExecutor dependencies
  Rule 3: PlanningEngine dependencies
  Rule 4: ReflectionEngine dependencies
  Rule 5: BrainWorkflow dependencies
  Rule 6: UseCase dependencies
  Rule 7: Runtime dependencies
"""

from pathlib import Path
import pytest
from tests.architecture.helpers import (
    get_src_root,
    get_imports,
    has_forbidden_dependencies,
    get_module_tree,
    get_package_modules,
)


# ── Helpers ─────────────────────────────────────────────────────────────

def _forbidden_msg(violations: list[str], module_label: str, rule_ref: str) -> str:
    if not violations:
        return ""
    lines = [f"[RULE {rule_ref}] {module_label} imports forbidden:"]
    lines.extend(f"  - {v}" for v in violations)
    return "\n".join(lines)


# ── Rule 1: EvolutionPlanner ───────────────────────────────────────────

class TestEvolutionPlannerDependencies:
    """Rule 1: EvolutionPlanner must remain pure — no application, runtime, or repository imports."""

    MODULE_PATH = "brain.evolution.planning"
    FORBIDDEN = (
        "brain.application",
        "brain.runtime",
        "brain.repositories",
        "brain.reflection",
        "brain.learning",
        "brain.workflow",
        "brain.infrastructure",
    )

    def test_no_forbidden_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "planning.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN)
        msg = _forbidden_msg(violations, "EvolutionPlanner", "1")
        assert not violations, msg

    def test_allowed_imports_are_present(self):
        """EvolutionPlanner may import brain.evolution.* and brain.domain.*."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "planning.py"
        imports = get_imports(file_path)
        brain_imports = [i for i in imports if i.startswith("brain.")]
        for imp in brain_imports:
            assert imp.startswith("brain.evolution") or imp.startswith("brain.domain"), (
                f"EvolutionPlanner imports unexpected brain module: {imp}"
            )


# ── Rule 2: EvolutionExecutor ──────────────────────────────────────────

class TestEvolutionExecutorDependencies:
    """Rule 2: EvolutionExecutor must never plan, reflect, or depend on runtime."""

    MODULE_PATH = "brain.evolution.executor"
    FORBIDDEN = (
        "brain.application.workflow",
        "brain.reflection",
        "brain.learning",
        "brain.planning",
        "brain.runtime",
    )

    def test_no_forbidden_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN)
        msg = _forbidden_msg(violations, "EvolutionExecutor", "2")
        assert not violations, msg

    def test_allowed_imports_are_present(self):
        """EvolutionExecutor may import brain.evolution.*, brain.repositories.*, brain.domain.*."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        imports = get_imports(file_path)
        brain_imports = [i for i in imports if i.startswith("brain.")]
        allowed_prefixes = ("brain.evolution", "brain.repositories", "brain.domain")
        for imp in brain_imports:
            assert any(imp.startswith(p) for p in allowed_prefixes), (
                f"EvolutionExecutor imports unexpected brain module: {imp}"
            )


# ── Rule 3: Planning Engine ────────────────────────────────────────────

class TestPlanningDependencies:
    """Rule 3: PlanningEngine and PlanningStrategy must have zero application or repository deps."""

    FORBIDDEN = (
        "brain.application",
        "brain.runtime",
        "brain.repositories",
        "brain.infrastructure",
    )

    def test_planning_engine_no_forbidden_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "planning" / "planner.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN)
        msg = _forbidden_msg(violations, "PlanningEngine", "3")
        assert not violations, msg

    def test_planning_strategy_no_forbidden_imports(self):
        src_root = get_src_root()
        strategy_dir = src_root / "brain" / "planning" / "strategies"
        for py_file in get_package_modules(strategy_dir):
            violations = has_forbidden_dependencies(py_file, self.FORBIDDEN)
            if violations:
                rel = py_file.relative_to(src_root)
                msg = _forbidden_msg(violations, f"PlanningStrategy ({rel})", "3")
                assert False, msg

    def test_entire_planning_package_no_forbidden_imports(self):
        """Verify the entire brain.planning package has zero forbidden deps."""
        src_root = get_src_root()
        planning_dir = src_root / "brain" / "planning"
        tree = get_module_tree(planning_dir)
        forbidden_prefixes = self.FORBIDDEN
        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if any(imp.startswith(p) for p in forbidden_prefixes):
                    violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "brain.planning package", "3")
        assert not violations, msg


# ── Rule 4: ReflectionEngine ───────────────────────────────────────────

class TestReflectionDependencies:
    """Rule 4: ReflectionEngine must not depend on evolution execution or workflow."""

    def test_reflection_engine_no_forbidden_imports(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "reflection" / "engine.py"
        forbidden = (
            "brain.application.workflow",
            "brain.evolution.executor",
            "brain.evolution.executor",
            "brain.evolution.evolution_record",
            "brain.application.usecases.evolution",
            "brain.runtime",
        )
        violations = has_forbidden_dependencies(file_path, forbidden)
        msg = _forbidden_msg(violations, "ReflectionEngine", "4")
        assert not violations, msg

    def test_reflection_engine_imports_allowed(self):
        """ReflectionEngine may import brain.domain and brain.reflection."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "reflection" / "engine.py"
        imports = get_imports(file_path)
        brain_imports = [i for i in imports if i.startswith("brain.")]
        allowed_prefixes = ("brain.domain", "brain.reflection")
        for imp in brain_imports:
            assert any(imp.startswith(p) for p in allowed_prefixes), (
                f"ReflectionEngine imports unexpected brain module: {imp}"
            )

    def test_reflection_usecase_no_forbidden_imports(self):
        """ReflectionUseCase must also avoid EvolutionUseCase/Executor and workflow."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "usecases" / "reflection.py"
        forbidden = (
            "brain.application.workflow.brain_workflow",
            "brain.evolution.executor",
            "brain.evolution.evolution_record",
            "brain.application.usecases.evolution",
            "brain.runtime",
        )
        violations = has_forbidden_dependencies(file_path, forbidden)
        msg = _forbidden_msg(violations, "ReflectionUseCase", "4")
        assert not violations, msg


# ── Rule 5: BrainWorkflow ─────────────────────────────────────────────

class TestWorkflowDependencies:
    """Rule 5: BrainWorkflow must not import engines directly — only through UseCases."""

    FORBIDDEN_PREFIXES = (
        "brain.planning.planner",
        "brain.execution.executor",
        "brain.learning.coordinator",
        "brain.reflection.engine",
        "brain.evolution.evolution",
        "brain.evolution.planning",
        "brain.evolution.executor",
    )

    def test_workflow_does_not_import_engines_directly(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        violations = has_forbidden_dependencies(file_path, self.FORBIDDEN_PREFIXES)
        msg = _forbidden_msg(violations, "BrainWorkflow", "5")
        assert not violations, msg

    def test_entire_workflow_package_no_direct_engine_imports(self):
        src_root = get_src_root()
        workflow_dir = src_root / "brain" / "application" / "workflow"
        violations = []
        for py_file in get_package_modules(workflow_dir):
            file_violations = has_forbidden_dependencies(py_file, self.FORBIDDEN_PREFIXES)
            for v in file_violations:
                rel = py_file.relative_to(src_root)
                violations.append(f"{rel} imports {v}")
        msg = _forbidden_msg(violations, "brain.application.workflow package", "5")
        assert not violations, msg


# ── Rule 6: UseCase Dependencies ───────────────────────────────────────

class TestUseCaseDependencies:
    """Rule 6: UseCases must never depend on runtime, adapters, or workflow internals."""

    FORBIDDEN = (
        "brain.runtime",
        "brain.adapter",
    )

    USE_CASE_FILES = (
        ("planning", "PlanningUseCase"),
        ("execution", "ExecutionUseCase"),
        ("learning", "LearningUseCase"),
        ("reflection", "ReflectionUseCase"),
        ("evolution", "EvolutionUseCase"),
    )

    def test_usecases_no_runtime_or_adapter_imports(self):
        src_root = get_src_root()
        violations = []
        for filename, label in self.USE_CASE_FILES:
            file_path = src_root / "brain" / "application" / "usecases" / f"{filename}.py"
            if not file_path.exists():
                continue
            file_violations = has_forbidden_dependencies(file_path, self.FORBIDDEN)
            for v in file_violations:
                violations.append(f"{label} imports {v}")
        msg = _forbidden_msg(violations, "Application UseCases", "6")
        assert not violations, msg


# ── Rule 7: Runtime Dependencies ───────────────────────────────────────

class TestRuntimeDependencies:
    """Rule 7: Runtime may wire everything, but components must not depend on runtime."""

    def test_cognitive_modules_do_not_import_runtime(self):
        """Verify no cognitive engine imports brain.runtime."""
        src_root = get_src_root()
        cognitive_packages = (
            "brain.planning",
            "brain.reflection",
            "brain.evolution",
            "brain.validation",
            "brain.detection",
            "brain.retrieval",
            "brain.services",
            "brain.execution",
        )
        violations = []
        for pkg in cognitive_packages:
            pkg_dir = Path(str(src_root).replace("\\", "/") + "/" + pkg.replace(".", "/"))
            if not pkg_dir.exists():
                continue
            tree = get_module_tree(pkg_dir)
            for mod, imports in tree.items():
                for imp in imports:
                    if imp.startswith("brain.runtime"):
                        violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "Cognitive modules", "7")
        assert not violations, msg


# ── Macro Layer Boundaries ─────────────────────────────────────────────

class TestMacroLayerDependencies:
    """Macro layer direction checks: Domain, Repositories, Infrastructure, Events."""

    def test_domain_does_not_import_higher_layers(self):
        src_root = get_src_root()
        domain_dir = src_root / "brain" / "domain"
        tree = get_module_tree(domain_dir)
        forbidden = (
            "brain.application",
            "brain.repositories",
            "brain.infrastructure",
            "brain.runtime",
            "brain.planning",
            "brain.reflection",
            "brain.evolution",
            "brain.learning",
            "brain.validation",
            "brain.detection",
            "brain.retrieval",
            "brain.services",
            "brain.execution",
        )
        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if any(imp.startswith(p) for p in forbidden):
                    violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "brain.domain", "macro")
        assert not violations, msg

    def test_repositories_do_not_import_application_or_runtime(self):
        src_root = get_src_root()
        repo_dir = src_root / "brain" / "repositories"
        tree = get_module_tree(repo_dir)
        forbidden = ("brain.application", "brain.runtime")
        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if any(imp.startswith(p) for p in forbidden):
                    violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "brain.repositories", "macro")
        assert not violations, msg

    def test_infrastructure_does_not_import_application_or_runtime(self):
        src_root = get_src_root()
        infra_dir = src_root / "brain" / "infrastructure"
        if not infra_dir.exists():
            return
        tree = get_module_tree(infra_dir)
        forbidden = ("brain.application", "brain.runtime")
        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if any(imp.startswith(p) for p in forbidden):
                    violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "brain.infrastructure", "macro")
        assert not violations, msg

    def test_events_do_not_import_application_or_runtime(self):
        src_root = get_src_root()
        events_dir = src_root / "brain" / "events"
        if not events_dir.exists():
            return
        tree = get_module_tree(events_dir)
        forbidden = ("brain.application", "brain.runtime", "brain.infrastructure")
        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if any(imp.startswith(p) for p in forbidden):
                    violations.append(f"{mod} imports {imp}")
        msg = _forbidden_msg(violations, "brain.events", "macro")
        assert not violations, msg
