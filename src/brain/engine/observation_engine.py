# Observation Engine

"""
Constitutional implementation of the Observation Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Tuple, Optional, Sequence
from uuid import UUID, uuid4
from enum import Enum

from brain.domain.observation import (
    ObservationSignal,
    ObservationEvidence,
    SystemObservation,
    ObservationCategory,
    SignalCategory,
)
from brain.engine.base import EngineContract, EngineContext, EngineMetadata
from brain.engine.exceptions import (
    ObservationValidationError,
    InsufficientEvidenceError,
    InvalidSignalError,
)
from brain.engine.validation import Validator, validate_uuid, validate_non_empty_string, ValidationReport


class ObservationCategory(Enum):
    OPERATIONAL = "operational"
    COGNITIVE = "cognitive"
    EVOLUTION_HISTORY = "evolution_history"


class SignalCategory(Enum):
    OPERATIONAL = "operational"
    COGNITIVE = "cognitive"
    EVOLUTION_HISTORY = "evolution_history"


@dataclass(frozen=True)
class ObservationPolicy:
    """Policy governing observation behavior."""
    min_evidence_confidence: float = 0.5
    min_sample_count: int = 1
    allowed_categories: Tuple[str, ...] = (
        "operational", "cognitive", "evolution_history"
    )


class ObservationEngine:
    """
    Constitutional contract: Pure function of input + policy -> observation.
    No state. No side effects. No reasoning.
    
    Constitutional Laws Enforced:
    - O-1: Observation describes facts only
    - O-2: Observation contains no decisions
    - O-3: Observation contains no solutions
    - O-4: Observation cannot mutate observed systems
    - O-5: Evidence and interpretation remain separate
    - O-6: Observation does not create EvolutionProposal objects
    """
    
    def __init__(
        self,
        policy: Optional[ObservationPolicy] = None,
        engine_id: str = "observation-engine",
        version: str = "1.0.0",
    ):
        self._policy = policy or ObservationPolicy()
        self._engine_id = engine_id
        self._version = version
    
    @property
    def engine_name(self) -> str:
        return self._engine_id
    
    @property
    def engine_version(self) -> str:
        return self._version
    
    @property
    def contract_version(self) -> str:
        return "1.0.0"
    
    def validate_input(self, input_data: 'ObservationInput') -> tuple[bool, str]:
        """Validate input before processing."""
        if input_data.raw_input is None:
            return False, "raw_input is required"
        if not input_data.policy:
            return False, "policy is required"
        return True, ""
    
    def validate_output(self, output_data: 'SystemObservation') -> tuple[bool, str]:
        """Validate output after processing."""
        if output_data.observation_id is None:
            return False, "observation_id is required"
        if not output_data.signal:
            return False, "signal is required"
        if not output_data.evidence:
            return False, "evidence is required"
        return True, ""
    
    def process(self, input_data: 'ObservationInput') -> 'SystemObservation':
        """
        Process raw input into a constitutional observation.
        
        Constitutional Laws Enforced:
        - O-1: Output contains only facts (signal + evidence)
        - O-2: Output contains no decisions
        - O-3: Output contains no solutions
        - O-4: No mutation of observed systems
        - O-5: Evidence and interpretation remain separate
        - O-6: No EvolutionProposal creation
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        # Validate policy
        policy = input_data.policy or ObservationPolicy()
        self._validate_policy(policy)
        
        # Create signal from raw input
        signal = self._create_signal(input_data.raw_input, input_data.policy)
        
        # Create evidence
        evidence = self._create_evidence(input_data.raw_input, policy)
        
        # Create observation
        observation = SystemObservation(
            observation_id=uuid4(),
            category=ObservationCategory(input_data.category),
            signal=signal,
            evidence=evidence,
            confidence=self._calculate_confidence(evidence, policy),
            detected_at=datetime.now(timezone.utc),
            detection_source=input_data.detection_source or "observation_engine",
            metadata=input_data.metadata or (),
        )
        
        # Validate output
        is_valid, error = self.validate_output(observation)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return observation
    
    def _validate_policy(self, policy: 'ObservationPolicy') -> None:
        if policy.min_evidence_confidence < 0.0 or policy.min_evidence_confidence > 1.0:
            raise ValueError("min_evidence_confidence must be between 0.0 and 1.0")
        if policy.min_sample_count < 1:
            raise ValueError("min_sample_count must be >= 1")
    
    def _create_signal(self, raw_input: bytes, policy: 'ObservationPolicy') -> 'ObservationSignal':
        # Constitutional: Signal is a fact, not an interpretation
        # This is a simplified implementation - real implementation would parse raw_input
        return ObservationSignal(
            signal_id=uuid4(),
            category=SignalCategory.OPERATIONAL,
            source="observation_engine",
            metric_name="raw_input_size",
            value=float(len(raw_input)),
            unit="bytes",
            timestamp=datetime.now(timezone.utc),
        )
    
    def _create_evidence(self, raw_input: bytes, policy: 'ObservationPolicy') -> 'ObservationEvidence':
        # Constitutional: Evidence supports the signal, doesn't interpret it
        return ObservationEvidence(
            evidence_id=uuid4(),
            description=f"Raw input of {len(raw_input)} bytes received",
            sample_count=1,
            measurement_start=datetime.now(timezone.utc),
            measurement_end=datetime.now(timezone.utc),
            confidence=1.0,
            metadata=(("source", "raw_input"), ("size_bytes", str(len(raw_input)))),
        )
    
    def _calculate_confidence(self, evidence: 'ObservationEvidence', policy: 'ObservationPolicy') -> float:
        # Simple confidence calculation based on evidence
        if evidence.confidence < policy.min_evidence_confidence:
            return policy.min_evidence_confidence
        return min(evidence.confidence, 1.0)
    
    def observe(
        self,
        raw_input: bytes,
        category: str = "operational",
        detection_source: str = "observation_engine",
        metadata: tuple = (),
        policy: 'ObservationPolicy' = None,
    ) -> 'SystemObservation':
        """
        Observe raw input and produce a constitutional observation.
        
        This is the main entry point for external callers.
        """
        from brain.domain.observation import (
            SystemObservation,
            ObservationCategory,
            ObservationSignal,
            ObservationEvidence,
        )
        
        # Build input
        input_data = ObservationInput(
            raw_input=policy.raw_input if policy else b"",
            category=category,
            detection_source=detection_source,
            metadata=metadata,
            policy=policy,
        )
        
        # For now, simplified - real implementation would process raw_input
        # This is a constitutional stub
        signal = self._create_signal(b"", policy or type('Policy', (), {'min_evidence_confidence': 0.5})())
        evidence = self._create_evidence(b"", policy or type('Policy', (), {'min_evidence_confidence': 0.5})())
        
        observation = SystemObservation(
            observation_id=uuid4(),
            category=ObservationCategory(category),
            signal=signal,
            evidence=evidence,
            confidence=1.0,
            detected_at=datetime.now(timezone.utc),
            detection_source=detection_source,
        )
        
        return observation
    
    def execute(self, input_data: 'ObservationInput') -> 'SystemObservation':
        """Execute the engine with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        output = self.process(input_data)
        
        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return output


# Input/Output data classes for the engine
from dataclasses import dataclass
from typing import Optional, Tuple
from uuid import UUID

@dataclass(frozen=True)
class ObservationInput:
    raw_input: bytes
    category: str = "operational"
    detection_source: str = "observation_engine"
    metadata: tuple = ()
    policy: Optional['ObservationPolicy'] = None


@dataclass(frozen=True)
class ObservationPolicy:
    min_evidence_confidence: float = 0.5
    min_sample_count: int = 1
    allowed_categories: tuple = ("operational", "cognitive", "evolution_history")


# Placeholder domain models - actual ones are in brain.domain.observation
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

@dataclass(frozen=True)
class ObservationSignal:
    signal_id: UUID = field(default_factory=uuid4)
    category: str = "operational"
    source: str = ""
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class ObservationEvidence:
    evidence_id: UUID = field(default_factory=uuid4)
    description: str = ""
    sample_count: int = 0
    measurement_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    measurement_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.0
    metadata: tuple = ()

@dataclass(frozen=True)
class SystemObservation:
    observation_id: UUID = field(default_factory=uuid4)
    category: str = "operational"
    signal: object = None
    evidence: object = None
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detection_source: str = ""
    metadata: tuple = ()