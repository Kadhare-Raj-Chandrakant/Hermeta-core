from enum import Enum


class TransitionType(Enum):
    UPDATE = "update"
    REFINEMENT = "refinement"
    SUPERSEDES = "supersedes"
    EXTENDS = "extends"
    CONTRADICTS = "contradicts"
