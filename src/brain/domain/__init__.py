"""Brain Domain Package.

Pure domain models with no external dependencies.
"""

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.identity import KnowledgeIdentity
from brain.domain.references import Evidence, Relationship
from brain.domain.task import Task, TaskType, Priority
from brain.domain.version import KnowledgeVersion
from brain.domain.understanding import Understanding
from brain.domain.evolution_domain import (
    EvolutionCategory,
    ProposalRiskLevel,
    DecisionState,
    EvolutionFinding,
    EvolutionProposal,
    EvolutionEvaluation,
    EvolutionDecision,
    EvolutionRecord,
)

__all__ = [
    "KnowledgeType",
    "LifecycleState",
    "KnowledgeIdentity",
    "Evidence",
    "Relationship",
    "Task",
    "TaskType",
    "Priority",
    "KnowledgeVersion",
    "Understanding",
    "EvolutionCategory",
    "ProposalRiskLevel",
    "DecisionState",
    "EvolutionFinding",
    "EvolutionProposal",
    "EvolutionEvaluation",
    "EvolutionDecision",
    "EvolutionRecord",
]