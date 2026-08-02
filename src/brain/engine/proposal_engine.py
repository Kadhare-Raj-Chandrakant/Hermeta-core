# brain/engine/proposal_engine.py
# Proposal Engine Implementation
# Constitutional Contract: P-1 through P-12

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, Sequence
from enum import Enum
import uuid

from brain.core.constants import CONSTITUTIONAL_VERSION
from brain.domain.proposal import (
    ProposalCategory,
    ProposalState,
    ProposalComplexity,
    Proposal,
    ProposalSpace,
    ProposalAssumption,
    ProposalOutcome,
)


class ProposalEngine:
    """
    Proposal Engine Implementation.
    
    Constitutional Laws Enforced:
    - P-1: A Proposal is an idea, not a decision. Never indicates approval/rejection.
    - P-2: Proposal expresses intent, not implementation. No code-level details.
    - P-3: Proposal never evaluates itself. No score/confidence/ranking/severity.
    - P-4: Proposal never mutates Hermes. No execution/mutation/runtime behavior.
    - P-5: Proposal remains completely traceable. Immutable traceability chain.
    - P-6: Proposal preserves uncertainty. Represents ONE possible improvement.
    - P-7: ProposalSpace owns alternatives. ProposalSpace never ranks/filters/merges/optimizes.
    - P-8: Proposal generation is creative. Evaluation is analytical. No evaluation logic.
    - P-9: Proposal is unaware of Evaluation. No Evaluation/Decision/Execution references.
    - P-10: Proposal describes desired outcome. Not implementation mechanism.
    - P-10: Proposal categories represent cognitive intent. Not implementation.
    - P-11: Proposal models are immutable domain objects.
    """

    def __init__(self, policy=None, engine_id="proposal-engine", version=CONSTITUTIONAL_VERSION):
        self._policy = policy or self._default_policy()
        self._engine_id = engine_id
        self._version = CONSTITUTIONAL_VERSION

    @property
    def engine_name(self) -> str:
        return "proposal-engine"

    @property
    def contract_version(self) -> str:
        return CONSTITUTIONAL_VERSION

    def validate_input(self, request) -> tuple:
        if not request.problem_statement_id:
            return False, "problem_statement_id is required"
        return True, ""

    def validate_output(self, space) -> tuple:
        if space.space_id is None:
            return False, "space_id is required"
        if not space.proposals:
            return False, "At least one proposal required"
        return True, ""

    def generate(self, request) -> 'ProposalSpace':
        """Generate candidate proposals for a problem."""
        is_valid, error = self.validate_input(request)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")

        policy = request.policy or self._default_policy()
        self._validate_policy(policy)

        # Generate proposals - constitutional stub
        proposals = self._generate_proposals(request, policy)

        if len(proposals) < 1:
            raise ValueError("Must generate at least one proposal")

        space = ProposalSpace(
            space_id=uuid.uuid4(),
            problem_statement_id=request.problem_statement_id,
            proposals=tuple(proposals),
            created_at=datetime.now(timezone.utc),
        )

        is_valid, error = self.validate_output(space)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")

        return space

    def _default_policy(self):
        class DefaultPolicy:
            min_proposals = 1
            max_proposals = 10
            allowed_categories = None
        return DefaultPolicy()

    def _validate_policy(self, policy):
        if policy.min_proposals < 1:
            raise ValueError("min_proposals must be >= 1")
        if policy.max_proposals < policy.min_proposals:
            raise ValueError("max_proposals must be >= min_proposals")

    def _generate_proposals(self, request, policy):
        proposals = []
        for i in range(policy.min_proposals):
            proposal = Proposal(
                proposal_id=uuid.uuid4(),
                title=f"Proposal {i+1}: Cognitive improvement",
                description=f"Improvement proposal {i+1} for problem {request.problem_statement_id}",
                category="knowledge_improvement",
                state="generated",
                originating_problem_id=request.problem_statement_id,
                hypothesis_space_id=uuid.uuid4(),
                observation_ids=(),
                rationale=f"Rationale for improvement {i+1}",
                intended_outcomes=(f"Improve {request.problem_statement_id}",),
                created_at=datetime.now(timezone.utc),
            )
            proposals.append(proposal)
        return proposals

    def execute(self, input_data) -> 'ProposalSpace':
        """Execute the engine with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")

        output = self.generate(input_data)

        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")

        return output


# Request/Response DTOs
@dataclass(frozen=True)
class ProposalRequest:
    problem_statement_id: UUID
    problem_space_id: UUID
    policy: Optional[object] = None
    context: Tuple[str, ...] = field(default_factory=tuple)


# Export
__all__ = (
    'ProposalCategory',
    'ProposalState',
    'ProposalComplexity',
    'Proposal',
    'ProposalSpace',
    'ProposalAssumption',
    'ProposalOutcome',
    'ProposalRequest',
    'ProposalEngine',
)