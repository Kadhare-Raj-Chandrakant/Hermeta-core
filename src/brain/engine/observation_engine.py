# Observation Engine

"""
Constitutional implementation of the Observation Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Tuple, Optional
from uuid import UUID, uuid4

from brain.core.constants import CONSTITUTIONAL_VERSION
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


@dataclass(frozen=True)
class ObservationPolicy:
    """Policy governing observation behavior."""
    min_evidence_confidence: float = 0.5
    min_sample_count: int = 1
    allowed_categories: Tuple[str, ...] = (
        "operational", "cognitive", "evolution_history"
    )


@dataclass(frozen=True)
class ObservationInput:
    raw_input: bytes
    category: str = "operational"
    detection_source: str = "observation_engine"
    metadata: tuple = ()
    policy: Optional[ObservationPolicy] = None


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
        version: str = CONSTITUTIONAL_VERSION,
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
        return CONSTITUTIONAL_VERSION

    def validate_input(self, input_data: ObservationInput) -> tuple[bool, str]:
        """Validate input before processing."""
        if input_data.raw_input is None:
            return False, "raw_input is required"
        if not input_data.policy:
            return False, "policy is required"
        return True, ""

    def validate_output(self, output_data: SystemObservation) -> tuple[bool, str]:
        """Validate output after processing."""
        if output_data.observation_id is None:
            return False, "observation_id is required"
        if not output_data.signal:
            return False, "signal is required"
        if not output_data.evidence:
            return False, "evidence is required"
        return True, ""

    def process(self, input_data: ObservationInput) -> SystemObservation:
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
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")

        policy = input_data.policy or ObservationPolicy()
        self._validate_policy(policy)

        signal = self._create_signal(input_data.raw_input, policy)
        evidence = self._create_evidence(input_data.raw_input, policy)

        observation = SystemObservation(
            observation_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            target=input_data.detection_source or "observation_engine",
            category=ObservationCategory(input_data.category),
            signal=signal,
            evidence=evidence,
            confidence=self._calculate_confidence(evidence, policy),
            metadata=input_data.metadata or (),
        )

        is_valid, error = self.validate_output(observation)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")

        return observation

    def _validate_policy(self, policy: ObservationPolicy) -> None:
        if not 0.0 <= policy.min_evidence_confidence <= 1.0:
            raise ValueError("min_evidence_confidence must be between 0.0 and 1.0")
        if policy.min_sample_count < 1:
            raise ValueError("min_sample_count must be >= 1")

    def _create_signal(self, raw_input: bytes, policy: ObservationPolicy) -> ObservationSignal:
        # Constitutional: Signal is a fact, not an interpretation.
        return ObservationSignal(
            signal_id=uuid4(),
            category=SignalCategory.OPERATIONAL,
            source="observation_engine",
            metric_name="raw_input_size",
            value=float(len(raw_input)),
            unit="bytes",
            timestamp=datetime.now(timezone.utc),
        )

    def _create_evidence(self, raw_input: bytes, policy: ObservationPolicy) -> ObservationEvidence:
        # Constitutional: Evidence supports the signal, doesn't interpret it.
        return ObservationEvidence(
            evidence_id=uuid4(),
            description=f"Raw input of {len(raw_input)} bytes received",
            sample_count=1,
            measurement_start=datetime.now(timezone.utc),
            measurement_end=datetime.now(timezone.utc),
            confidence=1.0,
            metadata=(("source", "raw_input"), ("size_bytes", str(len(raw_input)))),
        )

    def _calculate_confidence(self, evidence: ObservationEvidence, policy: ObservationPolicy) -> float:
        if evidence.confidence < policy.min_evidence_confidence:
            return policy.min_evidence_confidence
        return min(evidence.confidence, 1.0)

    def observe(
        self,
        raw_input: bytes,
        category: str = "operational",
        detection_source: str = "observation_engine",
        metadata: tuple = (),
        policy: Optional[ObservationPolicy] = None,
    ) -> SystemObservation:
        """
        Observe raw input and produce a constitutional observation.

        This is the main entry point for external callers.
        """
        from brain.domain.observation import SystemObservation, ObservationCategory

        input_data = ObservationInput(
            raw_input=raw_input,
            category=category,
            detection_source=detection_source,
            metadata=metadata,
            policy=policy or ObservationPolicy(),
        )
        return self.execute(input_data)

    def execute(self, input_data: ObservationInput) -> SystemObservation:
        """Execute the engine with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")

        output = self.process(input_data)

        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")

        return output


__all__ = (
    "ObservationEngine",
    "ObservationInput",
    "ObservationPolicy",
)
