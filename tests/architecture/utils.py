"""AST and Import Analysis Utilities for Architecture Audit Tests."""

import ast
from pathlib import Path
from typing import Dict, Set


def get_src_root() -> Path:
    """Return the absolute path to the src directory."""
    return Path(__file__).parent.parent.parent / "src"


def get_module_imports(file_path: Path) -> Set[str]:
    """
    Parse a Python file and return all imported module names.
    Handles both absolute imports and relative imports resolved against module location.
    """
    src_root = get_src_root()
    rel = file_path.relative_to(src_root)
    mod_parts = list(rel.with_suffix("").parts)
    if mod_parts[-1] == "__init__":
        mod_parts.pop()

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imported_modules: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imported_modules.add(node.module)
            elif node.level > 0:
                base = mod_parts[:-node.level]
                if node.module:
                    imported_modules.add(".".join(base + [node.module]))
                elif base:
                    imported_modules.add(".".join(base))

    return imported_modules


def get_all_brain_modules() -> Dict[str, Set[str]]:
    """Return a map of module_name -> set of imported module names for all files under src/brain."""
    src_root = get_src_root()
    brain_dir = src_root / "brain"
    module_imports: Dict[str, Set[str]] = {}

    for py_file in brain_dir.rglob("*.py"):
        rel = py_file.relative_to(src_root)
        mod_parts = list(rel.with_suffix("").parts)
        if mod_parts[-1] == "__init__":
            mod_parts.pop()
        current_mod = ".".join(mod_parts)
        module_imports[current_mod] = get_module_imports(py_file)

    return module_imports


def parse_ast_for_file(file_path: Path) -> ast.AST:
    """Parse AST for a given file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return ast.parse(f.read(), filename=str(file_path))
