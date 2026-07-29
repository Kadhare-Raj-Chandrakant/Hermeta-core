"""Smoke tests for the architecture audit infrastructure.

Verifies that:
- The architecture test package exists
- Helper utilities can be imported
- Test infrastructure works correctly
"""

from pathlib import Path
import pytest


class TestArchitectureSetup:
    """Smoke tests for architecture audit infrastructure setup."""

    def test_package_exists(self):
        """Architecture test package must be importable."""
        import tests.architecture
        assert tests.architecture.__file__ is not None

    def test_helpers_module_exists(self):
        """Helpers module must be importable."""
        from tests.architecture import helpers
        assert hasattr(helpers, "get_imports")
        assert hasattr(helpers, "has_forbidden_dependencies")
        assert hasattr(helpers, "get_project_root")

    def test_helpers_get_project_root(self):
        """get_project_root must return a valid path."""
        from tests.architecture.helpers import get_project_root
        root = get_project_root()
        assert root.exists()
        assert (root / "src").exists()

    def test_helpers_get_src_root(self):
        """get_src_root must return a valid src path."""
        from tests.architecture.helpers import get_src_root
        src_root = get_src_root()
        assert src_root.exists()
        assert (src_root / "brain").is_dir()

    def test_helpers_parse_ast(self):
        """parse_ast must parse a Python file without errors."""
        from tests.architecture.helpers import parse_ast, get_src_root
        test_file = get_src_root() / "brain" / "domain" / "task.py"
        assert test_file.exists()
        tree = parse_ast(test_file)
        assert tree is not None

    def test_helpers_get_imports(self):
        """get_imports must return a set of imported module names."""
        from tests.architecture.helpers import get_imports, get_src_root
        test_file = get_src_root() / "brain" / "domain" / "task.py"
        imports = get_imports(test_file)
        assert isinstance(imports, set)

    def test_helpers_get_class_definition_names(self):
        """get_class_definition_names must return top-level class names."""
        from tests.architecture.helpers import get_class_definition_names, get_src_root
        test_file = get_src_root() / "brain" / "domain" / "task.py"
        classes = get_class_definition_names(test_file)
        assert len(classes) > 0
        assert "Task" in classes

    def test_helpers_get_function_definition_names(self):
        """get_function_definition_names must return top-level function names."""
        from tests.architecture.helpers import get_function_definition_names, get_src_root
        test_file = get_src_root() / "brain" / "domain" / "task.py"
        funcs = get_function_definition_names(test_file)
        assert isinstance(funcs, list)

    def test_helpers_has_forbidden_dependencies_clean(self):
        """has_forbidden_dependencies must return empty list for a clean file."""
        from tests.architecture.helpers import has_forbidden_dependencies, get_src_root
        test_file = get_src_root() / "brain" / "domain" / "task.py"
        forbidden = has_forbidden_dependencies(
            test_file,
            ("brain.application", "brain.runtime"),
        )
        assert forbidden == []

    def test_helpers_get_package_modules(self):
        """get_package_modules must discover Python files in a package."""
        from tests.architecture.helpers import get_package_modules, get_src_root
        modules = get_package_modules(get_src_root() / "brain" / "domain")
        assert len(modules) > 0
        assert all(m.suffix == ".py" for m in modules)

    def test_helpers_get_module_tree(self):
        """get_module_tree must return a dict of module -> imports."""
        from tests.architecture.helpers import get_module_tree, get_src_root
        tree = get_module_tree(get_src_root() / "brain" / "domain")
        assert len(tree) > 0
        for mod_name, imports in tree.items():
            assert isinstance(mod_name, str)
            assert isinstance(imports, set)
