# Hypothesis Engine

"""
Constitutional implementation of the Hypothesis Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Tuple, Optional, Sequence
from uuid import UUID, uuid4
from enum import Enum

from brain.engine.base import EngineContract, EngineContext, EngineMetadata
from brain.engine.exceptions import (
    HypothesisValidationError,
    InsufficientObservationsError,
    PolicyViolationError,
)
from brain.engine.validation import Validator, validate_uuid, validate_non_empty_string, ValidationReport
from brain.domain.problem import Hypothesis, HypothesisSpace, HypothesisCategory


@dataclass(frozen=True)
class HypothesisPolicy:
    """Policy governing hypothesis generation."""
    min_hypotheses: int = 2  # H-2: Multiple hypotheses per observation
    max_hypotheses: int = 10
    required_categories: Tuple[str, ...] = ("causal", "correlational")
    min_confidence: float = 0.1
    max_confidence: float = 1.0


@dataclass(frozen=True)
class HypothesisRequest:
    observation_ids: Tuple[UUID, ...]
    observations: Tuple['SystemObservation', ...]
    evidence: Tuple['ObservationEvidence', ...]
    policy: 'HypothesisPolicy' = None

    def __post_init__(self):
        # HIGH-1: normalize caller-provided collections to immutable tuples
        object.__setattr__(self, 'observation_ids', tuple(self.observation_ids))
        object.__setattr__(self, 'observations', tuple(self.observations))
        object.__setattr__(self, 'evidence', tuple(self.evidence))


class HypothesisEngine:
    """
    Constitutional contract: Pure function of observations + policy -> hypothesis space.
    No state. No side effects. No ranking.
    
    Constitutional Laws Enforced:
    - H-1: Hypothesis is not a solution. It explains observations. Never recommends action.
    - H-2: Multiple hypotheses per observation. Engine must support competing explanations.
    - H-3: ProblemStatement may reference multiple hypotheses.
    - H-4: Observations remain immutable regardless of later conclusions.
    - H-6: Hypotheses never contain execution information.
    - H-7: Hypothesis formulation independent from Proposal generation.
    - H-8: Traceability preserved: Observation -> Hypothesis -> Problem -> Proposal
    """
    
    def __init__(
        self,
        policy: 'HypothesisPolicy' = None,
        engine_id: str = "hypothesis-engine",
        version: str = "1.0.0",
    ):
        self._policy = policy or HypothesisPolicy()
        self._engine_id = engine_id
        self._version = "1.0.0"
    
    @property
    def engine_name(self) -> str:
        return "hypothesis-engine"
    
    @property
    def contract_version(self) -> str:
        return "1.0.0"
    
    def validate_input(self, request: 'HypothesisRequest') -> tuple[bool, str]:
        """Validate input before processing."""
        if not request.observation_ids:
            return False, "observation_ids is required"
        if len(request.observation_ids) < 1:
            return False, "At least one observation_id required"
        if not request.observations:
            return False, "observations is required"
        if not request.evidence:
            return False, "evidence is required"
        if len(request.observations) != len(request.evidence):
            return False, "observations and evidence must have same length"
        return True, ""
    
    def validate_output(self, space: 'HypothesisSpace') -> tuple[bool, str]:
        """Validate output after processing."""
        if space.space_id is None:
            return False, "space_id is required"
        if not space.hypotheses:
            return False, "At least one hypothesis required"
        if len(space.hypotheses) < 2:
            return False, "H-2: Must produce multiple competing hypotheses"
        if space.observation_ids is None:
            return False, "observation_ids is required"
        return True, ""
    
    def generate(self, request: 'HypothesisRequest') -> 'HypothesisSpace':
        """
        Generate competing hypotheses for observations.
        
        Constitutional Laws Enforced:
        - H-1: Hypothesis is not a solution. It explains observations. Never recommends action.
        - H-2: Multiple hypotheses may originate from the same observations.
        - H-4: Observations remain immutable regardless of later conclusions.
        - H-6: Hypotheses never contain execution information.
        - H-7: Hypothesis formulation independent from Proposal generation.
        - H-8: Traceability preserved: Observation -> Hypothesis -> Problem -> Proposal
        """
        # Validate input
        is_valid, error = self.validate_input(request)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        # Get policy
        policy = request.policy or self._default_policy()
        self._validate_policy(policy)
        
        # Generate competing hypotheses
        hypotheses = self._generate_hypotheses(request, policy)
        
        # Verify minimum hypotheses (H-2)
        if len(hypotheses) < 2:
            raise ValueError("H-2: Must generate at least 2 competing hypotheses")
        
        # Create space
        space = HypothesisSpace(
            space_id=uuid4(),
            observation_ids=request.observation_ids,
            hypotheses=tuple(hypotheses),
            created_at=datetime.now(timezone.utc),
        )
        
        # Validate output
        is_valid, error = self.validate_output(space)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return space
    
    def _default_policy(self) -> 'HypothesisPolicy':
        return HypothesisPolicy()
    
    def _validate_policy(self, policy: 'HypothesisPolicy') -> None:
        if policy.min_hypotheses < 2:
            raise ValueError("H-2: min_hypotheses must be >= 2")
        if policy.min_confidence < 0.0 or policy.max_confidence > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if policy.min_confidence >= policy.max_confidence:
            raise ValueError("min_confidence must be < max_confidence")
    
    def _generate_hypotheses(self, request: 'HypothesisRequest', policy: 'HypothesisPolicy') -> list:
        """Generate competing hypotheses — distinct explanations per observation."""
        hypotheses = []

        # Build one hypothesis per observation; vary category and confidence by evidence content.
        observations = request.observations or ()
        evidence_items = request.evidence or ()

        for idx, obs in enumerate(observations):
            evidence = evidence_items[idx] if idx < len(evidence_items) else None
            # Deterministic content-derived signal strengths.
            signal_strength = getattr(getattr(obs, "signal", None), "value", 0.5)
            evidence_confidence = getattr(evidence, "confidence", 0.5)

            # Category determined by signal characteristics, not call order.
            category = (
                HypothesisCategory.CAUSAL
                if signal_strength >= 0.6
                else HypothesisCategory.CORRELATIONAL
                if evidence_confidence >= 0.5
                else HypothesisCategory.STRUCTURAL
            )

            # Confidence bounded by both policy and observed evidence strength.
            confidence = max(
                policy.min_confidence,
                min(policy.max_confidence, 0.5 * signal_strength + 0.5 * evidence_confidence),
            )

            hypotheses.append(
                Hypothesis(
                    hypothesis_id=uuid4(),
                    title=(
                        f"{category.value.title()} explanation for observation "
                        f"in {getattr(getattr(obs, 'category', None), 'value', 'unknown')} domain"
                    ),
                    description=(
                        f"Signal strength {signal_strength:.3f} and evidence confidence "
                        f"{evidence_confidence:.3f} jointly suggest a {category.value} relationship. "
                        "This hypothesis explains the observation without prescribing action."
                    ),
                    confidence=confidence,
                    supporting_observation_ids=request.observation_ids,
                    category=category.value,
                    created_at=datetime.now(timezone.utc),
                )
            )

        # Guarantee minimum competing hypotheses (H-2) even for single-observation input.
        if len(hypotheses) < policy.min_hypotheses and observations:
            base = observations[0]
            hypotheses.append(
                Hypothesis(
                    hypothesis_id=uuid4(),
                    title="Structural explanation for observed pattern",
                    description=(
                        "Fallback structural hypothesis: observed pattern may arise from "
                        "system topology rather than direct causation."
                    ),
                    confidence=policy.min_confidence,
                    supporting_observation_ids=request.observation_ids,
                    category=HypothesisCategory.STRUCTURAL,
                    created_at=datetime.now(timezone.utc),
                )
            )

        return hypotheses
    
    def execute(self, input_data: 'HypothesisRequest') -> 'HypothesisSpace':
        """Execute the engine with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        output = self.generate(input_data)
        
        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return output


# Supporting dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, Sequence
from enum import Enum

@dataclass(frozen=True)
class Hypothesis:
    """A single hypothesis explaining observations. Not a solution."""
    hypothesis_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    supporting_observation_ids: Tuple[UUID, ...] = field(default_factory=tuple)
    category: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.supporting_observation_ids:
            raise ValueError("supporting_observation_ids must not be empty")


@dataclass(frozen=True)
class HypothesisSpace:
    space_id: UUID = field(default_factory=uuid4)
    observation_ids: Tuple[UUID, ...] = field(default_factory=tuple)
    hypotheses: Tuple = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    @property
    def hypothesis_count(self) -> int:
        return len(self.hypotheses)
    
    @property
    def has_hypotheses(self) -> bool:
        return len(self.hypotheses) > 0