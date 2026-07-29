import importlib
import sys

import pytest


FORBIDDEN_MODULES = [
    "brain.repositories",
    "brain.infrastructure",
    "brain.validation",
    "brain.detection",
    "brain.evolution",
    "brain.retrieval",
    "brain.services.relevance",
    "brain.services.selection",
    "brain.services.compiler",
    "brain.pipeline.candidate",
    "brain.pipeline.evidence",
    "brain.pipeline.validator",
    "brain.pipeline.version_creator",
]

INTEGRATION_MODULES = [
    "brain.integration.__init__",
    "brain.integration.errors",
    "brain.integration.models",
    "brain.integration.events",
    "brain.integration.state",
    "brain.integration.recorder",
    "brain.integration.coordinator",
    "brain.integration.facade",
    "brain.integration.integration",
]


class TestDependencyBoundary:
    @pytest.mark.parametrize("module_name", INTEGRATION_MODULES)
    def test_integration_module_has_no_forbidden_imports(self, module_name: str) -> None:
        module = importlib.import_module(module_name)
        source_file = getattr(module, "__file__", None)
        if source_file is None:
            pytest.skip("no source file")

        with open(source_file, "r") as f:
            source = f.read()

        for forbidden in FORBIDDEN_MODULES:
            forbidden_base = forbidden.split(".")[-1]
            assert f"from {forbidden}" not in source, (
                f"{module_name} imports from forbidden module {forbidden}"
            )
            assert f"import {forbidden}" not in source, (
                f"{module_name} imports forbidden module {forbidden}"
            )

    def test_coordinator_does_not_import_pipeline(self) -> None:
        import brain.integration.coordinator as mod
        source_file = mod.__file__
        with open(source_file, "r") as f:
            source = f.read()
        assert "from brain.pipeline" not in source
        assert "import brain.pipeline" not in source

    def test_facade_does_not_import_brain_internals(self) -> None:
        import brain.integration.facade as mod
        source_file = mod.__file__
        with open(source_file, "r") as f:
            source = f.read()
        assert "from brain.pipeline" not in source
        assert "from brain.repositories" not in source
        assert "from brain.infrastructure" not in source
        assert "from brain.validation" not in source
        assert "from brain.detection" not in source
        assert "from brain.evolution" not in source
        assert "from brain.retrieval" not in source

    def test_coordinator_only_imports_allowed_modules(self) -> None:
        import brain.integration.coordinator as mod
        source_file = mod.__file__
        with open(source_file, "r") as f:
            source = f.read()
        for line in source.split("\n"):
            stripped = line.strip()
            if stripped.startswith("from brain.") or stripped.startswith("import brain."):
                if "from brain." in stripped:
                    module = stripped.split("from ")[1].split(".")[0:2]
                    module_path = ".".join(module)
                else:
                    module = stripped.split("import ")[1].split(".")[0:2]
                    module_path = ".".join(module)
                allowed = (
                    module_path.startswith("brain.adapter")
                    or module_path.startswith("brain.integration")
                    or module_path == "brain.domain.task"
                    or module_path == "brain.domain.enums"
                ), f"{mod.__name__} has forbidden import: {stripped}"
                assert allowed

    def test_models_expose_no_brain_internals(self) -> None:
        import brain.integration.models as mod
        source_file = mod.__file__
        with open(source_file, "r") as f:
            source = f.read()
        assert "from brain." not in source
        assert "import brain." not in source
