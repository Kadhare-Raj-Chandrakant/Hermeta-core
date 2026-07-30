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
from brain.domain.observation import (
    ObservationSignal,
    SignalCategory,
    ObservationEvidence,
    SystemObservation,
    ObservationCategory,
    ObservationSnapshot,
)
from brain.domain.problem import (
    HypothesisCategory,
    ProblemCategory,
    ProblemSeverity,
    Hypothesis,
    HypothesisSpace,
    ProblemStatement,
)
from brain.domain.proposal import (
    ProposalCategory,
    RiskLevel,
    ProposalComplexity,
    ProposalState,
    Proposal,
    ProposalSpace,
)
from brain.domain.evaluation import (
    EvaluationDimension,
    EvidenceType,
    EvaluationState,
    Evaluation,
    EvaluationSpace,
    Tradeoff,
    EvaluationEvidence,
    DimensionalAnalysis,
)
from brain.domain.governance import (
    DecisionState,
    PolicyCategory,
    FindingSeverity,
    DecisionMode,
    GovernanceDecision,
    DecisionContext,
    GovernanceHistory,
    GovernancePolicy,
    GovernanceRationale,
    GovernanceFinding,
    GovernancePolicy,
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
    "ObservationSignal",
    "SignalCategory",
    "ObservationEvidence",
    "SystemObservation",
    "ObservationCategory",
    "ObservationSnapshot",
    "HypothesisCategory",
    "ProblemCategory",
    "ProblemSeverity",
    "Hypothesis",
    "HypothesisSpace",
    "ProblemStatement",
    "ProposalCategory",
    "RiskLevel",
    "ProposalComplexity",
    "ProposalState",
    "Proposal",
    "ProposalSpace",
    "EvaluationDimension",
    "EvidenceType",
    "EvaluationState",
    "Evaluation",
    "EvaluationSpace",
    "Tradeoff",
    "EvaluationEvidence",
    "DimensionalAnalysis",
    "DecisionState",
    "PolicyCategory",
    "FindingSeverity",
    "DecisionMode",
    "GovernanceDecision",
    "DecisionContext",
    "GovernanceHistory",
    "GovernancePolicy",
    "GovernanceRationale",
    "GovernanceFinding",
]