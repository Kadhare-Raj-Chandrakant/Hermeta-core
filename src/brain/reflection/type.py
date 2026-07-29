from enum import Enum


class ReflectionType(Enum):
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
    OBSOLETE = "obsolete"
    GAP = "gap"
