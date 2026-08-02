"""Evolution Constitution Domain Models.

These models represent the conceptual foundation for controlled self-evolution.
They implement the separation of concerns mandated by the Evolution Constitution:

Finding ≠ Proposal
Proposal ≠ Execution
Evaluation precedes mutation
Evolution history is preserved
Constitutional laws cannot be changed by normal evolution

These are pure domain objects with no dependencies on application, runtime,
adapters, repositories, infrastructure, or engines.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

from brain.domain.enums import KnowledgeType
from brain.domain.identity import KnowledgeIdentity
from brain.domain.references import Evidence


class EvolutionCategory(Enum):
    """Categories of evolution findings."""

    ARCHITECTURAL = "architectural"
    PERFORMANCE = "performance"
    CORRECTNESS = "correctness"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"


class ProposalRiskLevel(Enum):
    """Risk assessment levels for proposals."""

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionState(Enum):
    """Governance decision states."""

    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


@dataclass(frozen=True)
class EvolutionFinding:
    """
    A discovered improvement opportunity.

    This represents an observation that something may need improvement.
    It contains NO solution, NO execution instructions, NO mutation commands.

    The finding is the starting point — the "what might be wrong".
    """

    identity: KnowledgeIdentity = field(default_factory=KnowledgeIdentity.create)
    category: EvolutionCategory = EvolutionCategory.OPERATIONAL
    target_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    target_knowledge_type: KnowledgeType = KnowledgeType.COMPONENT
    evidence: tuple[Evidence, ...] = ()
    description: str = ""
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detection_source: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.description.strip():
            raise ValueError("Description must not be empty")
        if not self.detection_source.strip():
            raise ValueError("Detection source must not be empty")


@dataclass(frozen=True)
class EvolutionProposal:
    """
    A suggested improvement for a finding.

    This represents a possible solution — the "how we might fix it".
    It does NOT execute anything. It is a passive suggestion.

    A proposal is always linked to a finding but stands independently
    as a candidate for evaluation.
    """

    identity: KnowledgeIdentity = field(default_factory=KnowledgeIdentity.create)
    finding_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    target_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    proposed_change: str = ""
    expected_benefit: str = ""
    risk_level: ProposalRiskLevel = ProposalRiskLevel.MEDIUM
    risk_description: str = ""
    prerequisite_findings: tuple[uuid.UUID, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    author: str = ""

    def __post_init__(self) -> None:
        if not self.proposed_change.strip():
            raise ValueError("Proposed change must not be empty")
        if not self.expected_benefit.strip():
            raise ValueError("Expected benefit must not be empty")
        if not self.risk_description.strip():
            raise ValueError("Risk description must not be empty")
        if not self.author.strip():
            raise ValueError("Author must not be empty")


@dataclass(frozen=True)
class EvolutionEvaluation:
    """
    Analysis of a proposal's merit, risk, and architectural impact.

    Evaluation is the critical thinking step — the "should we do this?".
    It does not decide. It provides the information needed for a decision.
    """

    identity: KnowledgeIdentity = field(default_factory=KnowledgeIdentity.create)
    proposal_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    benefit_assessment: str = ""
    risk_assessment: str = ""
    architecture_impact: str = ""
    constitutional_compliance: str = ""
    confidence: float = 0.0
    evaluation_notes: str = ""
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluator: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.benefit_assessment.strip():
            raise ValueError("Benefit assessment must not be empty")
        if not self.risk_assessment.strip():
            raise ValueError("Risk assessment must not be empty")
        if not self.architecture_impact.strip():
            raise ValueError("Architecture impact must not be empty")
        if not self.constitutional_compliance.strip():
            raise ValueError("Constitutional compliance must not be empty")
        if not self.evaluator.strip():
            raise ValueError("Evaluator must not be empty")


@dataclass(frozen=True)
class EvolutionDecision:
    """
    Governance outcome for a proposal.

    The decision is the authoritative governance result.
    It records WHAT was decided, not WHY (the evaluation captures the why).
    """

    identity: KnowledgeIdentity = field(default_factory=KnowledgeIdentity.create)
    proposal_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    evaluation_identity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    state: DecisionState = DecisionState.REQUIRES_REVIEW
    decision_rationale: str = ""
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decider: str = ""
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_rationale.strip():
            raise ValueError("Decision rationale must not be empty")
        if not self.decider.strip():
            raise ValueError("Decider must not be empty")


@dataclass(frozen=True)
class EvolutionRecord:
    """
    Permanent historical record of an evolution attempt.

    This captures the complete lifecycle: Finding → Proposal → Evaluation → Decision.
    It is a record of history, not execution. Execution (if approved) happens
    through the existing EvolutionExecutor and is recorded separately.

    The record preserves the full decision trail for audit and learning.
    """

    identity: KnowledgeIdentity = field(default_factory=KnowledgeIdentity.create)
    finding: EvolutionFinding | None = None
    proposal: EvolutionProposal | None = None
    evaluation: EvolutionEvaluation | None = None
    decision: EvolutionDecision | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    execution_record_id: uuid.UUID | None = None
    verification_result: str | None = None

    def is_complete(self) -> bool:
        """Check if all stages are present."""
        return (
            self.finding is not None
            and self.proposal is not None
            and self.evaluation is not None
            and self.decision is not None
        )

    def final_decision(self) -> DecisionState | None:
        """Get the final decision state if decided."""
        if self.decision is not None:
            return self.decision.state
        return None

    def is_approved(self) -> bool:
        """Check if the record represents an approved evolution."""
        return self.final_decision() == DecisionState.APPROVED

    def is_rejected(self) -> bool:
        """Check if the record represents a rejected evolution."""
        return self.final_decision() == DecisionState.REJECTED

    def requires_review(self) -> bool:
        """Check if the record requires further review."""
        return self.final_decision() == DecisionState.REQUIRES_REVIEW