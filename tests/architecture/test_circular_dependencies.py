"""Circular Dependency Audit Tests.

Verifies that Hermes architectural layers have no circular dependencies.

The actual Hermes layer hierarchy (from dependencies):
    Domain (bottom) -> Pipeline/Events/Repositories/Infrastructure -> Engines -> Application -> Runtime (top)

Key principle: dependencies flow UP (towards Runtime), never DOWN (towards Domain).
The only cycle allowed is at the composition root (Runtime factory).

This test catches REAL cycles, not legitimate cross-layer dependencies.
"""

from pathlib import Path

from tests.architecture.helpers import get_src_root, get_module_tree, get_imports, get_package_modules


def _violation_msg(violations: list[str], rule: str) -> str:
    if not violations:
        return ""
    lines = [f"[RULE {rule}] Architectural dependency violation:"]
    lines.extend(f"  - {v}" for v in violations)
    return "\n".join(lines)


# ============================================================================
# Layer Definitions (matching actual Hermes architecture)
# ============================================================================

# Layer 0: Domain (foundation - no brain imports)
DOMAIN_MODULES = {"brain.domain"}

# Layer 1: Infrastructure/Contracts (depend on Domain only)
INFRASTRUCTURE_MODULES = {
    "brain.pipeline",
    "brain.events",
    "brain.repositories",
    "brain.infrastructure",
}

# Layer 2: Cognitive Engines (depend on Domain + Infrastructure)
ENGINE_MODULES = {
    "brain.planning",
    "brain.reflection",
    "brain.evolution",
    "brain.execution",
    "brain.learning",
    "brain.validation",
    "brain.detection",
    "brain.retrieval",
    "brain.services",
}

# Layer 3: Application (orchestrates engines)
APPLICATION_MODULES = {"brain.application"}

# Layer 4: Adapter (external boundary)
ADAPTER_MODULES = {"brain.adapter"}

# Layer 5: Runtime (composition root)
RUNTIME_MODULES = {"brain.runtime"}

ALL_BRAIN_MODULES = (
    DOMAIN_MODULES | INFRASTRUCTURE_MODULES | ENGINE_MODULES |
    APPLICATION_MODULES | ADAPTER_MODULES | RUNTIME_MODULES
)

# Valid upward dependencies (lower -> higher layer numbers)
VALID_UPWARD_DEPS = {
    # Domain: no brain imports allowed
    # Infrastructure: can import Domain
    frozenset(INFRASTRUCTURE_MODULES): DOMAIN_MODULES,
    # Engines: can import Domain + Infrastructure
    frozenset(ENGINE_MODULES): DOMAIN_MODULES | INFRASTRUCTURE_MODULES,
    # Application: can import Domain + Infrastructure + Engines
    frozenset(APPLICATION_MODULES): DOMAIN_MODULES | INFRASTRUCTURE_MODULES | ENGINE_MODULES,
    # Adapter: can import Domain + Infrastructure + Engines + Application
    frozenset(ADAPTER_MODULES): DOMAIN_MODULES | INFRASTRUCTURE_MODULES | ENGINE_MODULES | APPLICATION_MODULES,
    # Runtime (composition root): can import anything
    frozenset(RUNTIME_MODULES): ALL_BRAIN_MODULES,
}


class TestNoCyclesInFullGraph:
    """The complete brain module graph must be acyclic."""

    def test_full_brain_graph_is_acyclic(self):
        """Entire brain package must form a DAG (no cycles anywhere)."""
        src_root = get_src_root()
        brain_dir = src_root / "brain"
        tree = get_module_tree(brain_dir)

        # Filter to only brain modules
        brain_tree = {k: v for k, v in tree.items() if k in ALL_BRAIN_MODULES}

        cycles = self._find_all_cycles(brain_tree)

        msg = _violation_msg(cycles, "C1")
        assert not cycles, msg

    def _find_all_cycles(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Find all elementary cycles using Johnson's algorithm variant."""
        visited = set()
        rec_stack = set()
        path = []
        cycles = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycle = path[idx:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)
            path.pop()

        for node in graph:
            if node not in visited:
                dfs(node)

        # Deduplicate
        unique = []
        seen = set()
        for cycle in cycles:
            min_idx = cycle.index(min(cycle))
            norm = tuple(cycle[min_idx:] + cycle[:min_idx])
            if norm not in seen:
                seen.add(norm)
                unique.append(list(norm))

        return unique


class TestLayerOrdering:
    """Dependencies must only flow upward (toward Runtime)."""

    def test_no_downward_dependencies(self):
        """No layer may import from a layer above it (higher layer number)."""
        src_root = get_src_root()
        brain_dir = src_root / "brain"
        tree = get_module_tree(brain_dir)

        # Filter to brain modules
        brain_tree = {k: v for k, v in tree.items() if k in ALL_BRAIN_MODULES}

        violations = []
        for mod, imports in brain_tree.items():
            mod_layer = self._get_layer(mod)
            for imp in imports:
                if imp not in ALL_BRAIN_MODULES:
                    continue  # stdlib or external
                imp_layer = self._get_layer(imp)
                if imp_layer < mod_layer:
                    violations.append(
                        f"{mod} (layer {mod_layer}) imports {imp} (layer {imp_layer}) - downward dependency"
                    )

        msg = _violation_msg(violations, "C2")
        assert not violations, msg

    def test_runtime_is_composition_root(self):
        """Runtime is the only layer that can import anything (composition root)."""
        src_root = get_src_root()
        runtime_dir = src_root / "brain" / "runtime"
        tree = get_module_tree(runtime_dir)

        # Runtime CAN import anything - this is by design
        # Just verify runtime doesn't have upward cycles with itself
        cycles = []
        for mod, imports in tree.items():
            for imp in imports:
                if imp in tree and imp in tree.get(mod, set()) and mod in tree.get(imp, set()):
                    cycles.append(f"{mod} <-> {imp}")

        msg = _violation_msg(cycles, "C3")
        assert not cycles, msg

    def _get_layer(self, module: str) -> int:
        """Return layer number (0=Domain, 5=Runtime)."""
        if module in DOMAIN_MODULES:
            return 0
        if module in INFRASTRUCTURE_MODULES:
            return 1
        if module in ENGINE_MODULES:
            return 2
        if module in APPLICATION_MODULES:
            return 3
        if module in ADAPTER_MODULES:
            return 4
        if module in RUNTIME_MODULES:
            return 5
        return -1  # external


class TestDomainPurity:
    """Domain must not import Application, Engines, Adapter, Runtime, or Infrastructure."""

    def test_domain_imports_only_stdlib_and_itself(self):
        """Domain must not import engines, application, adapter, runtime, or infrastructure."""
        src_root = get_src_root()
        domain_dir = src_root / "brain" / "domain"
        tree = get_module_tree(domain_dir)

        # Domain CAN import: other domain modules, stdlib
        # Domain CANNOT import: engines, application, adapter, runtime, infrastructure, pipeline, events, repositories
        forbidden = ENGINE_MODULES | APPLICATION_MODULES | ADAPTER_MODULES | RUNTIME_MODULES | INFRASTRUCTURE_MODULES

        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if imp in forbidden:
                    violations.append(f"{mod} imports {imp} (domain must not import {imp.split('.')[1]})")

        msg = _violation_msg(violations, "C4")
        assert not violations, msg

    def _is_stdlib(self, module: str) -> bool:
        stdlib = {
            "abc", "uuid", "datetime", "dataclasses", "enum", "typing",
            "collections", "pathlib", "functools", "itertools", "copy",
            "json", "uuid", "math", "random", "time", "os", "sys",
        }
        return module.split(".")[0] in stdlib


class TestInfrastructureIsolation:
    """Infrastructure layer may only import Domain + stdlib."""

    def test_infrastructure_imports_only_domain_and_stdlib(self):
        """Infrastructure must not import engines, application, or adapter."""
        src_root = get_src_root()
        violations = []

        for infra_mod in INFRASTRUCTURE_MODULES:
            infra_dir = src_root / infra_mod.replace(".", "/")
            if not infra_dir.exists():
                continue
            tree = get_module_tree(infra_dir)
            for mod, imports in tree.items():
                for imp in imports:
                    if imp in ENGINE_MODULES or imp in APPLICATION_MODULES or imp in ADAPTER_MODULES or imp in RUNTIME_MODULES:
                        violations.append(f"{mod} imports {imp} (infrastructure must not import engines/application/adapter)")

        msg = _violation_msg(violations, "C5")
        assert not violations, msg


class TestEngineLayerIsolation:
    """Engines may import Domain + Infrastructure, but NOT Application/Adapter/Runtime."""

    def test_engines_import_only_domain_and_infrastructure(self):
        """Engines must not import application, adapter, or runtime."""
        src_root = get_src_root()
        violations = []

        for engine_mod in ENGINE_MODULES:
            engine_dir = src_root / engine_mod.replace(".", "/")
            if not engine_dir.exists():
                continue
            tree = get_module_tree(engine_dir)
            for mod, imports in tree.items():
                for imp in imports:
                    if imp in APPLICATION_MODULES or imp in ADAPTER_MODULES or imp in RUNTIME_MODULES:
                        violations.append(f"{mod} imports {imp} (engines must not import application/adapter/runtime)")

        msg = _violation_msg(violations, "C6")
        assert not violations, msg


class TestApplicationLayer:
    """Application may import Domain + Infrastructure + Engines, NOT Adapter/Runtime."""

    def test_application_imports_only_lower_layers(self):
        """Application must not import adapter or runtime."""
        src_root = get_src_root()
        app_dir = src_root / "brain" / "application"
        tree = get_module_tree(app_dir)

        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if imp in ADAPTER_MODULES or imp in RUNTIME_MODULES:
                    violations.append(f"{mod} imports {imp} (application must not import adapter/runtime)")

        msg = _violation_msg(violations, "C7")
        assert not violations, msg


class TestAdapterBoundary:
    """Adapter may import Application and below, NOT Runtime."""

    def test_adapter_imports_allowed_layers(self):
        """Adapter may import Application + lower, but NOT Runtime."""
        src_root = get_src_root()
        adapter_dir = src_root / "brain" / "adapter"
        tree = get_module_tree(adapter_dir)

        violations = []
        for mod, imports in tree.items():
            for imp in imports:
                if imp in RUNTIME_MODULES:
                    violations.append(f"{mod} imports {imp} (adapter must not import runtime)")

        msg = _violation_msg(violations, "C8")
        assert not violations, msg


class TestNoMutualDependencies:
    """No direct mutual imports between any two brain modules."""

    def test_no_direct_mutual_imports(self):
        """If A imports B, B must not import A."""
        src_root = get_src_root()
        brain_dir = src_root / "brain"
        tree = get_module_tree(brain_dir)

        mutual = []
        for a, a_imports in tree.items():
            for b in a_imports:
                if b in tree and a in tree[b]:
                    if a < b:  # report once
                        mutual.append(f"{a} <-> {b}")

        msg = _violation_msg(mutual, "C9")
        assert not mutual, msg


def _violation_msg(items: list[str], rule: str) -> str:
    if not items:
        return ""
    lines = [f"[RULE {rule}] Architectural dependency violation:"]
    lines.extend(f"  - {item}" for item in items)
    return "\n".join(lines)