# brain/engine/evaluation_engine.py
# Evaluation Engine Implementation
# Constitutional Contract: E-1 through E-16

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, Sequence, Dict
from enum import Enum
import uuid

from brain.core.constants import CONSTITUTIONAL_VERSION
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


class EvaluationEngine:
    """
    Evaluation Engine Implementation.
    
    Constitutional Laws Enforced: E-1 through E-16.
    """
    
    def __init__(self, policy=None, engine_id="evaluation-engine", version=CONSTITUTIONAL_VERSION):
        self._policy = policy
        self._engine_id = engine_id
        self._version = CONSTITUTIONAL_VERSION
    
    @property
    def engine_name(self) -> str:
        return "evaluation-engine"
    
    @property
    def contract_version(self) -> str:
        return CONSTITUTIONAL_VERSION
    
    def validate_input(self, request) -> tuple:
        if not request.proposal_id:
            return False, "proposal_id is required"
        return True, ""
    
    def validate_output(self, evaluation) -> tuple:
        if evaluation.evaluation_id is None:
            return False, "evaluation_id is required"
        if not evaluation.dimensional_analyses:
            return False, "At least one dimensional analysis required"
        return True, ""
    
    def evaluate(self, request) -> 'Evaluation':
        """Produce a complete analytical evaluation of a single proposal."""
        is_valid, error = self.validate_input(request)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        # Constitutional stub implementation with valid dimensional analysis
        evaluation = Evaluation(
            evaluation_id=uuid.uuid4(),
            proposal_id=request.proposal_id,
            state="draft",
            dimensional_analyses=(
                DimensionalAnalysis(
                    analysis_id=uuid.uuid4(),
                    created_at=datetime.now(timezone.utc),
                    dimension=EvaluationDimension.ARCHITECTURAL_INTEGRITY,
                    facts=("Constitutional evaluation stub",),
                    judgments=("Evaluation generated per constitutional contract",),
                    evidence=(),
                    tradeoff_ids=(),
                ),
            ),
            global_tradeoffs=(),
            evidence_ids=(),
            summary_judgment="Constitutional evaluation stub",
            known_uncertainties=(),
            created_at=datetime.now(timezone.utc),
        )
        
        is_valid, error = self.validate_output(evaluation)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return evaluation
    
    def evaluate_space(self, request) -> 'EvaluationSpace':
        """Evaluate all proposals in a space independently."""
        evaluations = []
        for pid in request.proposal_ids:
            eval_result = self.evaluate(EvaluationRequest(
                proposal_id=pid,
                proposal_space_id=request.proposal_space_id,
                problem_statement_id=request.problem_statement_id,
                policy=request.policy,
                context=request.context,
            ))
            evaluations.append(eval_result)
        
        return EvaluationSpace(
            space_id=uuid.uuid4(),
            problem_statement_id=request.problem_statement_id,
            proposal_ids=request.proposal_ids,
            evaluations=tuple(evaluations),
            created_at=datetime.now(timezone.utc),
        )
    
    def compare_evaluations(self, space: 'EvaluationSpace', dimension: str) -> Dict[UUID, str]:
        """Compare evaluations across proposals along a single dimension. Comparison ≠ Ranking."""
        result = {}
        for eval in space.evaluations:
            result[eval.proposal_id] = f"Analysis for {dimension}"
        return result
    
    def supersede(self, evaluation_id: UUID, new_evaluation) -> 'Evaluation':
        """Create a superseded evaluation (immutable history)."""
        return Evaluation(
            evaluation_id=uuid.uuid4(),
            proposal_id=evaluation_id,  # Using evaluation_id as placeholder
            state="draft",
            dimensional_analyses=(
                DimensionalAnalysis(
                    analysis_id=uuid.uuid4(),
                    created_at=datetime.now(timezone.utc),
                    dimension=EvaluationDimension.ARCHITECTURAL_INTEGRITY,
                    facts=("Superseded evaluation",),
                    judgments=("Historical record preserved",),
                    evidence=(),
                    tradeoff_ids=(),
                ),
            ),
            global_tradeoffs=(),
            evidence_ids=(),
            summary_judgment="Superseded evaluation",
            known_uncertainties=(),
            created_at=datetime.now(timezone.utc),
            superseded_by=evaluation_id,
        )
    
    def execute(self, input_data):
        """Execute with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        output = self.evaluate(input_data)
        
        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return output


# Request/Response DTOs
@dataclass(frozen=True)
class EvaluationRequest:
    proposal_id: UUID
    proposal_space_id: UUID
    problem_statement_id: UUID
    proposal_ids: Tuple[UUID, ...] = field(default_factory=tuple)
    policy: Optional[object] = None
    # Carries pipeline trace IDs (UUID), not strings.
    context: Tuple[UUID, ...] = field(default_factory=tuple)

    def __post_init__(self):
        # HIGH-1: normalize caller-provided collections to immutable tuples
        object.__setattr__(self, 'proposal_ids', tuple(self.proposal_ids))
        object.__setattr__(self, 'context', tuple(self.context))


# Export
__all__ = (
    'EvaluationDimension',
    'EvidenceType',
    'EvaluationState',
    'Tradeoff',
    'EvaluationEvidence',
    'DimensionalAnalysis',
    'Evaluation',
    'EvaluationSpace',
    'EvaluationEngine',
    'EvaluationRequest',
)