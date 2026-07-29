"""Generic, reusable audit helpers for architecture verification tests.

This module provides utilities for inspecting Python source code structure.
It does NOT encode specific milestone rules — rules belong in individual tests.
"""

import ast
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Any, Optional


def get_project_root() -> Path:
    """Return the absolute path to the project root (repository root)."""
    return Path(__file__).parent.parent.parent


def get_src_root() -> Path:
    """Return the absolute path to the src directory."""
    return get_project_root() / "src"


def get_module_path(module_name: str) -> Path:
    """Convert a dotted module name (e.g. 'brain.evolution.planning') to a file path."""
    src_root = get_src_root()
    parts = module_name.split(".")
    return src_root / "/".join(parts) / "__init__.py" if Path(src_root / "/".join(parts)).is_dir() else src_root / "/".join(parts) + ".py"


def read_source(file_path: Path) -> str:
    """Read the full source code of a Python file."""
    return file_path.read_text(encoding="utf-8")


def parse_ast(file_path: Path) -> ast.Module:
    """Parse a Python file into an AST."""
    return ast.parse(read_source(file_path), filename=str(file_path))


def get_imports(file_path: Path) -> set[str]:
    """Return all imported module names from a Python file, resolving relative imports."""
    src_root = get_src_root()
    rel = file_path.relative_to(src_root)
    mod_parts = list(rel.with_suffix("").parts)
    if mod_parts[-1] == "__init__":
        mod_parts.pop()

    tree = parse_ast(file_path)
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.add(node.module)
            elif node.level > 0:
                base = mod_parts[:-node.level]
                if node.module:
                    imports.add(".".join(base + [node.module]))
                elif base:
                    imports.add(".".join(base))

    return imports


def has_forbidden_dependencies(file_path: Path, forbidden_prefixes: tuple[str, ...]) -> list[str]:
    """Check if a file imports any module whose name starts with a forbidden prefix.

    Returns a list of matching forbidden imports (empty if none found).
    """
    imports = get_imports(file_path)
    return [imp for imp in imports if any(imp.startswith(p) for p in forbidden_prefixes)]


def load_module_safely(module_name: str) -> Optional[Any]:
    """Try to load a module by name. Returns the module object or None if it cannot be loaded."""
    try:
        return importlib.import_module(module_name)
    except (ImportError, ModuleNotFoundError, Exception):
        return None


def get_module_source(module_name: str) -> Optional[str]:
    """Try to get the source of a module by name. Returns source string or None."""
    mod = load_module_safely(module_name)
    if mod is None:
        return None
    try:
        return inspect.getsource(mod)
    except (TypeError, OSError):
        return None


def get_class_definition_names(file_path: Path) -> list[str]:
    """Return a list of class names defined at the top level of a Python file."""
    tree = parse_ast(file_path)
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]


def get_function_definition_names(file_path: Path) -> list[str]:
    """Return a list of function names defined at the top level of a Python file."""
    tree = parse_ast(file_path)
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]


def is_frozen_dataclass(cls: type) -> bool:
    """Check if a class is a frozen dataclass."""
    import dataclasses
    return dataclasses.is_dataclass(cls) and cls.__dataclass_fields__.get("_frozen", False) if hasattr(cls, "__dataclass_fields__") else False


def get_package_modules(package_dir: Path) -> list[Path]:
    """Return all Python files found recursively under a package directory."""
    return sorted(package_dir.rglob("*.py"))


def get_module_tree(package_root: Path) -> dict[str, set[str]]:
    """Build a map of module_name -> set of imports for all modules under a package root.

    Useful for broad dependency analysis across an entire package.
    """
    result: dict[str, set[str]] = {}
    src_root = get_src_root()
    for py_file in get_package_modules(package_root):
        rel = py_file.relative_to(src_root)
        mod_parts = list(rel.with_suffix("").parts)
        if mod_parts[-1] == "__init__":
            mod_parts.pop()
        mod_name = ".".join(mod_parts)
        result[mod_name] = get_imports(py_file)
    return result
