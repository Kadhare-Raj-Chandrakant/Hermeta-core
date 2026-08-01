"""State Ownership Audit Tests.

Verifies every piece of state has clear owner, lifecycle, and mutation authority.

Rules verified:
  1. BrainSession owns session lifecycle
  2. BrainWorkflow coordinates but doesn't become state container
  3. Planning components remain stateless
  4. Reflection doesn't become memory storage
  5. Repository owns persistence only
  6. EvolutionUnitOfWork owns transaction lifecycle
  7. Mutable state has explicit ownership
  8. No cross-session contamination
"""

from pathlib import Path
import ast
from tests.architecture.helpers import (
    get_src_root,
    get_imports,
    has_forbidden_dependencies,
    get_class_method_names,
    get_function_definition_names,
    get_class_definition_names,
    get_package_modules,
)


def _violation_msg(violations: list[str], component: str, rule: str) -> str:
    if not violations:
        return ""
    lines = [f"[RULE {rule}] {component} state ownership violation:"]
    lines.extend(f"  - {v}" for v in violations)
    return "\n".join(lines)


# ── Rule 1: BrainSession Owns Session Lifecycle ──────────────────────

class TestSessionOwnership:
    """BrainSession is the sole owner of session lifecycle state."""

    def test_brainsession_owns_session_lifecycle_attrs(self):
        """BrainSession has clear session lifecycle attributes."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "brain_session.py"
        class_names = get_class_definition_names(file_path)
        assert "BrainSession" in class_names

    def test_no_engine_owns_session_state(self):
        """Cognitive engines must not store session state."""
        src_root = get_src_root()
        engine_packages = [
            "brain/planning",
            "brain/reflection",
            "brain/evolution",
            "brain/learning",
            "brain/validation",
            "brain/detection",
            "brain/retrieval",
            "brain/services",
            "brain/execution",
        ]
        forbidden_attrs = {
            "session_id",
            "current_session",
            "session_context",
            "workflow_state",
            "session_cache",
            "current_task",
        }
        violations = []
        for pkg in engine_packages:
            pkg_dir = src_root / pkg.replace(".", "/")
            if not pkg_dir.exists():
                continue
            for py_file in pkg_dir.rglob("*.py"):
                class_names = get_class_definition_names(py_file)
                for cls_name in class_names:
                    class_attrs = self._get_class_attributes(py_file, cls_name)
                    for attr in forbidden_attrs:
                        if attr in class_attrs:
                            rel = py_file.relative_to(src_root)
                            violations.append(f"{rel}.{cls_name}.{attr}")
        msg = _violation_msg(violations, "Cognitive engines", "1")
        assert not violations, msg

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        """Get instance attributes defined in a class's __init__ or body."""
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attrs.add(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.add(target.id)
        return attrs


# ── Rule 2: BrainWorkflow Does Not Own Cognitive State ──────────────────

class TestWorkflowStateOwnership:
    """BrainWorkflow coordinates but never becomes a state container."""

    FORBIDDEN_WORKFLOW_ATTRS = {
        "current_strategy",
        "pending_plan",
        "planning_cache",
        "evolution_state",
        "memory_cache",
        "strategy_state",
        "cognitive_memory",
        "plan_history",
        "execution_history",
    }

    def test_workflow_no_cognitive_state_attributes(self):
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        class_names = get_class_definition_names(file_path)
        assert "BrainWorkflow" in class_names

        class_attrs = self._get_class_attributes(file_path, "BrainWorkflow")
        violations = [f"BrainWorkflow.{attr}" for attr in class_attrs if attr in self.FORBIDDEN_WORKFLOW_ATTRS]
        msg = _violation_msg(violations, "BrainWorkflow", "2")
        assert not violations, msg

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attrs.add(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.add(target.id)
        return attrs


# ── Rule 3: Planning Components Must Remain Stateless ──────────────────

class TestPlanningStatelessness:
    """PlanningEngine and EvolutionPlanner must not retain state."""

    def test_planners_have_no_retained_state(self):
        """PlanningEngine and EvolutionPlanner must not have mutable instance state beyond injected deps."""
        src_root = get_src_root()
        planner_files = [
            ("brain/planning/planner.py", "PlanningEngine"),
            ("brain/evolution/planning.py", "EvolutionPlanner"),
        ]
        violations = []
        for rel_path, class_name in planner_files:
            file_path = src_root / rel_path
            class_attrs = self._get_class_attributes(file_path, class_name)
            # Allow only injected dependencies (strategy for PlanningEngine, none for EvolutionPlanner)
            allowed = {"_strategy"} if class_name == "PlanningEngine" else set()
            unexpected = class_attrs - allowed
            for attr in unexpected:
                violations.append(f"{rel_path}.{class_name}.{attr}")
        msg = _violation_msg(violations, "Planners", "3")
        assert not violations, msg

    def test_planners_no_repository_imports(self):
        """Planners must not import repositories."""
        src_root = get_src_root()
        planner_files = [
            src_root / "brain" / "planning" / "planner.py",
            src_root / "brain" / "evolution" / "planning.py",
        ]
        violations = []
        for file_path in planner_files:
            imports = get_imports(file_path)
            for imp in imports:
                if imp.startswith("brain.repositories") or imp.startswith("brain.infrastructure"):
                    rel = file_path.relative_to(src_root)
                    violations.append(f"{rel} imports {imp}")
        msg = _violation_msg(violations, "Planners", "3")
        assert not violations, msg

    def test_planners_pure_methods_no_side_effects(self):
        """Planner public methods must not mutate instance state (only local computation)."""
        src_root = get_src_root()
        planner_files = [
            ("brain/planning/planner.py", "PlanningEngine", "create_plan"),
            ("brain/evolution/planning.py", "EvolutionPlanner", "plan"),
        ]
        violations = []
        for rel_path, class_name, method_name in planner_files:
            file_path = src_root / rel_path
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            for stmt in ast.walk(item):
                                # Only flag Store on self.attribute where attr is NOT in allowed injected deps
                                if (isinstance(stmt, ast.Attribute) and
                                    isinstance(stmt.value, ast.Name) and
                                    stmt.value.id == "self" and
                                    isinstance(stmt.ctx, ast.Store)):
                                    attr = stmt.attr
                                    allowed = {"_strategy"} if class_name == "PlanningEngine" else set()
                                    if attr not in allowed:
                                        violations.append(f"{rel_path}.{class_name}.{method_name} mutates self.{attr}")
        msg = _violation_msg(violations, "Planners", "3")
        assert not violations, msg

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attrs.add(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.add(target.id)
        return attrs


# ── Rule 4: Reflection State Must Not Become Memory Storage ──────────────

class TestReflectionStateOwnership:
    """ReflectionEngine observes and reports; it doesn't own long-term state."""

    def test_reflection_engine_no_persistent_state(self):
        """ReflectionEngine must not have persistent mutable state."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "reflection" / "engine.py"
        class_attrs = self._get_class_attributes(file_path, "ReflectionEngine")
        allowed = {"_detectors"}
        unexpected = class_attrs - allowed
        violations = [f"ReflectionEngine.{attr}" for attr in unexpected]
        msg = _violation_msg(violations, "ReflectionEngine", "4")
        assert not violations, msg

    def test_reflection_detectors_no_persistent_state(self):
        """Reflection detectors must not retain state between calls."""
        src_root = get_src_root()
        detector_dir = src_root / "brain" / "reflection" / "detectors"
        if not detector_dir.exists():
            return
        violations = []
        for py_file in detector_dir.rglob("*.py"):
            class_names = get_class_definition_names(py_file)
            for cls_name in class_names:
                class_attrs = self._get_class_attributes(py_file, cls_name)
                # Allow UPPER_CASE constants (immutable) and private injected deps
                unexpected = {
                    a for a in class_attrs
                    if a not in {"_threshold", "_config"}  # injected deps
                    and not a.startswith("_")  # private attrs
                    and not a.isupper()  # UPPER_CASE constants
                    and a not in forbidden  # known forbidden
                }
                for attr in unexpected:
                    rel = py_file.relative_to(src_root)
                    violations.append(f"{rel}.{cls_name}.{attr}")
        msg = _violation_msg(violations, "ReflectionDetectors", "4")
        assert not violations, msg

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attrs.add(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.add(target.id)
        return attrs


# ── Rule 5: Repository Owns Persistence State Only ──────────────────────

class TestRepositoryStateOwnership:
    """Repositories own persistence state only; no reasoning state."""

    REASONING_ATTRS = {
        "last_strategy", "best_merge_candidate", "recommended_action",
        "cached_analysis", "inferred_state", "heuristic_memory",
        "strategy_memory", "decision_cache", "recommendation_cache",
    }

    def test_repository_methods_are_persistence_primitives(self):
        """Repository methods must be persistence primitives, not semantic operations."""
        src_root = get_src_root()
        repo_files = [
            src_root / "brain" / "repositories" / "base.py",
            src_root / "brain" / "repositories" / "evolution_base.py",
            src_root / "brain" / "repositories" / "memory.py",
        ]
        semantic_verbs = {"merge", "resolve", "infer", "reason", "decide", "analyze",
                          "suggest", "recommend", "optimize", "consolidate", "adjudicate"}
        violations = []
        for file_path in repo_files:
            if not file_path.exists():
                continue
            class_methods = get_class_method_names(file_path)
            for class_name, method_name in class_methods:
                for verb in semantic_verbs:
                    if method_name.startswith(verb):
                        rel = file_path.relative_to(src_root)
                        violations.append(f"{rel}.{class_name}.{method_name} starts with '{verb}'")
        msg = _violation_msg(violations, "Repositories", "5")
        assert not violations, msg

    def test_repository_no_reasoning_state_attributes(self):
        """Repository instances must not have reasoning state attributes."""
        src_root = get_src_root()
        repo_files = [
            src_root / "brain" / "repositories" / "memory.py",
            src_root / "brain" / "infrastructure" / "sqlite" / "repository.py",
        ]
        violations = []
        for file_path in repo_files:
            if not file_path.exists():
                continue
            class_names = get_class_definition_names(file_path)
            for cls_name in class_names:
                if cls_name.endswith("Error") or cls_name.endswith("Repository"):
                    continue
                class_attrs = self._get_class_attributes(file_path, cls_name)
                for attr in self.REASONING_ATTRS:
                    if attr in class_attrs:
                        rel = file_path.relative_to(src_root)
                        violations.append(f"{rel}.{cls_name}.{attr}")
        msg = _violation_msg(violations, "Repositories", "5")
        assert not violations, msg

    def test_repository_instance_state_is_storage_only(self):
        """Repository instance state must be storage primitives only."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "repositories" / "memory.py"
        class_attrs = self._get_class_attributes(file_path, "InMemoryKnowledgeRepository")
        # These are the expected storage structures
        allowed = {"_identities", "_versions", "_transitions", "_conflicts", "_execution_records", "_lock"}
        unexpected = class_attrs - allowed
        violations = [f"InMemoryKnowledgeRepository.{attr}" for attr in unexpected]
        msg = _violation_msg(violations, "Repositories", "5")
        assert not violations, msg

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attrs.add(item.target.id)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.add(target.id)
        return attrs


# ── Rule 6: EvolutionUnitOfWork Owns Transaction Lifecycle ──────────────

class TestTransactionOwnership:
    """Only EvolutionUnitOfWork owns transaction lifecycle."""

    def test_only_uow_manages_transaction_boundary(self):
        """Only EvolutionUnitOfWork should have begin/commit/rollback methods."""
        src_root = get_src_root()
        # Check no other component has begin/commit/rollback
        cognitive_packages = [
            "brain/planning",
            "brain/reflection",
            "brain/evolution",
            "brain/learning",
            "brain/validation",
            "brain/detection",
            "brain/retrieval",
            "brain/services",
            "brain/execution",
        ]
        violations = []
        for pkg in cognitive_packages:
            pkg_dir = src_root / pkg.replace(".", "/")
            if not pkg_dir.exists():
                continue
            for py_file in pkg_dir.rglob("*.py"):
                class_methods = get_class_method_names(py_file)
                for class_name, method_name in class_methods:
                    if method_name in ("begin", "commit", "rollback") and class_name != "EvolutionUnitOfWork":
                        rel = py_file.relative_to(src_root)
                        violations.append(f"{rel}.{class_name}.{method_name}()")
        msg = _violation_msg(violations, "Transaction boundary", "6")
        assert not violations, msg

    def test_uow_has_clear_lifecycle_attrs(self):
        """EvolutionUnitOfWork has clear transaction lifecycle attributes."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "usecases" / "unit_of_work.py"
        class_attrs = self._get_class_attributes(file_path, "EvolutionUnitOfWork")
        expected = {"_knowledge_repo", "_evolution_repo", "_knowledge_snapshot", "_evolution_snapshot", "_active"}
        missing = expected - class_attrs
        assert not missing, f"EvolutionUnitOfWork missing expected attrs: {missing}"

    def test_executor_does_not_own_transaction(self):
        """EvolutionExecutor must not have transaction boundary methods."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "evolution" / "executor.py"
        class_methods = get_class_method_names(file_path)
        tx_methods = [m for c, m in class_methods if m in ("begin", "commit", "rollback")]
        assert not tx_methods, f"EvolutionExecutor has transaction methods: {tx_methods}"

    def _get_class_attributes(self, file_path: Path, class_name: str) -> set[str]:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attrs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.AnnAssign, ast.Assign)):
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            attrs.add(item.target.id)
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    attrs.add(target.id)
                # Also check __init__ for instance attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.value, ast.Name) and stmt.value.id == "self":
                                attrs.add(stmt.attr)
        return attrs


# ── Rule 7: Mutable State Must Have Explicit Ownership ──────────────────

class TestMutableStateOwnership:
    """All mutable state must have clear owner, lifecycle, mutation path."""

    def test_no_module_level_mutable_globals(self):
        """No mutable dict/list/set at module level (except constants)."""
        src_root = get_src_root()
        violations = []
        for py_file in (src_root / "brain").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            # Only check top-level assignments (not inside functions/classes)
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Check if value is mutable literal
                            if isinstance(node.value, (ast.Dict, ast.List, ast.Set)):
                                # Allow UPPER_CASE constants
                                if not target.id.isupper():
                                    rel = py_file.relative_to(src_root)
                                    violations.append(f"{rel}.{target.id} = mutable literal at module level")
        msg = _violation_msg(violations, "Module-level mutable state", "7")
        assert not violations, msg

    def test_no_class_level_mutable_shared_state(self):
        """No mutable class-level attributes that become shared across instances."""
        src_root = get_src_root()
        violations = []
        for py_file in (src_root / "brain").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Check if value is mutable literal (not just a reference)
                                    if isinstance(item.value, (ast.Dict, ast.List, ast.Set)):
                                        rel = py_file.relative_to(src_root)
                                        violations.append(f"{rel}.{node.name}.{target.id} = mutable class attribute")
        msg = _violation_msg(violations, "Class-level mutable state", "7")
        assert not violations, msg

    def test_instance_mutable_state_initialized_in_init(self):
        """All instance mutable state must be initialized in __init__."""
        src_root = get_src_root()
        violations = []
        for py_file in (src_root / "brain").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Skip dataclasses - they use field(init=False) pattern
                    if self._is_dataclass(node):
                        continue
                    init_attrs = set()
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            for stmt in ast.walk(item):
                                if (isinstance(stmt, ast.Attribute) and
                                    isinstance(stmt.value, ast.Name) and
                                    stmt.value.id == "self" and
                                    isinstance(stmt.ctx, ast.Store)):
                                    init_attrs.add(stmt.attr)

                    # Check all Store attributes on self
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            for stmt in ast.walk(item):
                                if (isinstance(stmt, ast.Attribute) and
                                    isinstance(stmt.value, ast.Name) and
                                    stmt.value.id == "self" and
                                    isinstance(stmt.ctx, ast.Store)):
                                    if stmt.attr not in init_attrs:
                                        rel = py_file.relative_to(src_root)
                                        violations.append(f"{rel}.{node.name}.{stmt.attr} mutated but not in __init__")

    def _is_dataclass(self, node: ast.ClassDef) -> bool:
        """Check if a class has @dataclass decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                return True
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                return True
        return False
        msg = _violation_msg(violations, "Instance state not in __init__", "7")
        assert not violations, msg

    def test_no_cross_session_caches(self):
        """No caches that persist across sessions at module/class level."""
        src_root = get_src_root()
        cache_names = {"_cache", "_memo", "_memoize", "_lru_cache", "CACHE", "Memo"}
        violations = []
        for py_file in (src_root / "brain").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            if item.target.id in cache_names:
                                rel = py_file.relative_to(src_root)
                                violations.append(f"{rel}.{node.name}.{item.target.id} = cache attribute")
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id in cache_names:
                                    rel = py_file.relative_to(src_root)
                                    violations.append(f"{rel}.{node.name}.{target.id} = cache attribute")
        msg = _violation_msg(violations, "Cross-session caches", "7")
        assert not violations, msg


# ── Rule 8: No Cross-Session Contamination ─────────────────────────────

class TestCrossSessionIsolation:
    """Session state must not accidentally become global state."""

    def test_brainsession_instance_attrs_not_global(self):
        """BrainSession instance attributes must not be module-level globals."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "brain_session.py"
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        violations = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id in ("_task", "_started_at", "_learned_items", "_brain"):
                            violations.append(f"Module-level session attr: {target.id}")
        msg = _violation_msg(violations, "BrainSession globals", "8")
        assert not violations, msg

    def test_no_module_level_session_state(self):
        """No session-related state at module level."""
        src_root = get_src_root()
        session_keywords = ("session_id", "current_session", "active_session", "workflow_session")
        violations = []
        for py_file in (src_root / "brain").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)

            # Check top-level assignments only
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id in session_keywords:
                                rel = py_file.relative_to(src_root)
                                violations.append(f"{rel}: {target.id} = ... at module level")
        msg = _violation_msg(violations, "Module-level session state", "8")
        assert not violations, msg

    def test_workflow_does_not_retain_session_state(self):
        """BrainWorkflow run() must not store session state between calls."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "application" / "workflow" / "workflow.py"
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "BrainWorkflow":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "run":
                        for stmt in ast.walk(item):
                            if (isinstance(stmt, ast.Attribute) and
                                isinstance(stmt.value, ast.Name) and
                                stmt.value.id == "self" and
                                isinstance(stmt.ctx, ast.Store)):
                                attr = stmt.attr
                                if attr in ("session_id", "task", "plan", "execution", "learning"):
                                    violations.append(f"run() stores session state: self.{attr}")
        msg = _violation_msg(violations, "Workflow session retention", "8")
        assert not violations, msg

    def test_planning_engine_no_cross_call_state(self):
        """PlanningEngine must not retain state between plan() calls."""
        src_root = get_src_root()
        file_path = src_root / "brain" / "planning" / "planner.py"
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PlanningEngine":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "create_plan":
                        for stmt in ast.walk(item):
                            if (isinstance(stmt, ast.Attribute) and
                                isinstance(stmt.value, ast.Name) and
                                stmt.value.id == "self" and
                                isinstance(stmt.ctx, ast.Store)):
                                violations.append(f"create_plan() stores state: self.{stmt.attr}")
        msg = _violation_msg(violations, "PlanningEngine cross-call state", "8")
        assert not violations, msg


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])