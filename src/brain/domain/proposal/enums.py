from enum import Enum


class ProposalCategory(Enum):
    """
    Categories represent COGNITIVE INTENT of a proposal.

    They do NOT represent:
    - Implementation approach
    - Code-level changes
    - Technical strategy
    - Specific components to modify

    They represent WHAT cognitive capability the proposal aims to improve.
    """

    KNOWLEDGE_IMPROVEMENT = "knowledge_improvement"
    LEARNING_IMPROVEMENT = "learning_improvement"
    PLANNING_IMPROVEMENT = "planning_improvement"
    RETRIEVAL_IMPROVEMENT = "retrieval_improvement"
    REFLECTION_IMPROVEMENT = "reflection_improvement"
    EVOLUTION_IMPROVEMENT = "evolution_improvement"
    SAFETY_IMPROVEMENT = "safety_improvement"
    RELIABILITY_IMPROVEMENT = "reliability_improvement"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    EXPLAINABILITY_IMPROVEMENT = "explainability_improvement"


class RiskLevel(Enum):
    """
    Risk levels represent POTENTIAL IMPACT of proposal execution.

    They do NOT represent:
    - Execution priority
    - Governance urgency
    - Resource allocation
    """

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionComplexity(Enum):
    """
    Complexity of executing the proposal.

    Does NOT represent:
    - Timeline
    - Cost
    - Staffing
    """

    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class ProposalComplexity(Enum):
    """
    Overall complexity assessment of the proposal.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProposalState(Enum):
    """
    State represents PROPOSAL LIFECYCLE POSITION only.

    This is NOT approval/rejection.
    This is NOT evaluation result.
    This tracks WHERE the proposal exists in the generation pipeline.
    """

    GENERATED = "generated"
    IN_SPACE = "in_space"
    WITHDRAWN = "withdrawn"