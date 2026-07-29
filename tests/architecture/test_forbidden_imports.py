"""Forbidden Imports Tests.

Verifies strict component boundary restrictions for Planner, Executor, Reflection, and Planning components.
"""

from pathlib import Path
import pytest
from tests.architecture.utils import get_module_imports, get_src_root


class TestForbiddenImports:
    """Automated tests checking forbidden imports for key architecture components."""

    def test_evolution_planner_forbidden_imports(self):
        """
        EvolutionPlanner (src/brain/evolution/planning.py)
        Must NOT import: brain.application, brain.runtime, brain.reflection, brain.learning, brain.repositories.
        Allowed: brain.evolution, brain.domain, standard library.
        """
        src_root = get_src_root()
        planner_file = src_root / "brain" / "evolution" / "planning.py"
        imports = get_module_imports(planner_file)

        forbidden_prefixes = (
            "brain.application",
            "brain.runtime",
            "brain.reflection",
            "brain.learning",
            "brain.repositories",
            "brain.infrastructure",
        )

        violations = [imp for imp in imports if any(imp.startswith(prefix) for prefix in forbidden_prefixes)]
        assert not violations, f"EvolutionPlanner contains forbidden imports: {violations}"

    def test_evolution_executor_forbidden_imports(self):
        """
        EvolutionExecutor (src/brain/evolution/executor.py)
        Must NOT import: brain.application.workflow, brain.reflection, brain.planning, brain.runtime.
        Allowed: brain.evolution, brain.repositories, brain.domain.
        """
        src_root = get_src_root()
        executor_file = src_root / "brain" / "evolution" / "executor.py"
        imports = get_module_imports(executor_file)

        forbidden_prefixes = (
            "brain.application.workflow",
            "brain.reflection",
            "brain.planning",
            "brain.runtime",
            "brain.learning",
        )

        violations = [imp for imp in imports if any(imp.startswith(prefix) for prefix in forbidden_prefixes)]
        assert not violations, f"EvolutionExecutor contains forbidden imports: {violations}"

    def test_planning_engine_and_strategy_forbidden_imports(self):
        """
        PlanningEngine & PlanningStrategy (src/brain/planning/...)
        Cannot import: brain.application, brain.runtime, brain.repositories, BrainWorkflow, BrainSession.
        """
        src_root = get_src_root()
        planning_dir = src_root / "brain" / "planning"

        forbidden_prefixes = (
            "brain.application",
            "brain.runtime",
            "brain.repositories",
            "brain.infrastructure",
        )

        violations = []
        for py_file in planning_dir.rglob("*.py"):
            imports = get_module_imports(py_file)
            for imp in imports:
                if any(imp.startswith(prefix) for prefix in forbidden_prefixes):
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        assert not violations, f"Planning components contain forbidden imports: {violations}"

    def test_reflection_engine_and_usecase_forbidden_imports(self):
        """
        ReflectionEngine & ReflectionUseCase
        Cannot import: EvolutionExecutor, EvolutionUseCase, BrainWorkflow.
        """
        src_root = get_src_root()
        reflection_engine_file = src_root / "brain" / "reflection" / "engine.py"
        reflection_usecase_file = src_root / "brain" / "application" / "usecases" / "reflection.py"

        forbidden_tokens = (
            "brain.evolution.executor",
            "brain.application.usecases.evolution",
            "brain.application.workflow",
            "BrainWorkflow",
            "EvolutionExecutor",
            "EvolutionUseCase",
        )

        violations = []
        for target_file in (reflection_engine_file, reflection_usecase_file):
            if not target_file.exists():
                continue
            imports = get_module_imports(target_file)
            for imp in imports:
                if any(imp.startswith(token) for token in forbidden_tokens):
                    rel = target_file.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")

        assert not violations, f"Reflection engine/usecase contains forbidden imports: {violations}"
