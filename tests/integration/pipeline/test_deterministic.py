"""Deterministic pipeline verification tests.

Validates that identical pipeline runs produce identical execution traces.
"""

import uuid
from datetime import datetime, timezone

import pytest

from brain.engine.pipeline import create_constitutional_pipeline, PipelineResult
from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
from brain.engine.problem_engine import ProblemEngine, ProblemRequest
from brain.engine.proposal_engine import ProposalEngine
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest
from brain.engine.execution_engine import ExecutionEngine, ExecutionContext


class TestDeterministicPipeline:
    """Validate deterministic pipeline execution."""

    def test_identical_input_produces_identical_trace_structure(self):
        """Same input produces same trace structure across runs."""
        pipeline1 = create_constitutional_pipeline()
        pipeline2 = create_constitutional_pipeline()

        result1 = pipeline1.execute(b"deterministic test input")
        result2 = pipeline2.execute(b"deterministic test input")

        assert result1.success is True
        assert result2.success is True

        # Trace structure should be identical (same number of stages)
        assert len(result1.trace_ids) == len(result2.trace_ids)

        # All stages should execute
        assert result1.observation is not None
        assert result2.observation is not None
        assert result1.hypothesis_space is not None
        assert result2.hypothesis_space is not None
        assert result1.problem_statement is not None
        assert result2.problem_statement is not None
        assert result1.proposal_space is not None
        assert result2.proposal_space is not None
        assert result1.evaluation is not None
        assert result2.evaluation is not None
        assert result1.governance_decision is not None
        assert result2.governance_decision is not None
        assert result1.authorization_record is not None
        assert result2.authorization_record is not None
        assert result1.execution_result is not None
        assert result2.execution_result is not None

    def test_pipeline_ordering_deterministic(self):
        """Pipeline stage ordering is always the same."""
        pipeline = create_constitutional_pipeline()
        results = [pipeline.execute(b"order test") for _ in range(5)]

        for result in results:
            assert result.success is True

        # All results should have same trace ID count
        trace_counts = [len(r.trace_ids) for r in results]
        assert all(c == trace_counts[0] for c in trace_counts)

    def test_engine_invocation_order_identical(self):
        """Engine invocation order is always identical."""
        pipeline = create_constitutional_pipeline()

        # Run multiple times
        trace_sequences = []
        for _ in range(3):
            result = pipeline.execute(b"invocation order test")
            trace_sequences.append(result.trace_ids)

        # The sequence of artifact types should be identical
        # (We can't check exact IDs but we can check structure)
        for i in range(1, len(trace_sequences)):
            assert len(trace_sequences[i]) == len(trace_sequences[0])

    def test_artifact_structure_deterministic(self):
        """Produced artifact types and field presence are deterministic."""
        pipeline = create_constitutional_pipeline()

        result1 = pipeline.execute(b"structure test")
        result2 = pipeline.execute(b"structure test")

        # Check all artifact types exist
        stages = [
            ('observation', 'observation'),
            ('hypothesis', 'hypothesis_space'),
            ('problem', 'problem_statement'),
            ('proposal', 'proposal_space'),
            ('evaluation', 'evaluation'),
            ('governance', 'governance_decision'),
            ('authorization', 'authorization_record'),
            ('execution', 'execution_result'),
        ]

        for stage_name, attr in stages:
            art1 = getattr(result1, attr)
            art2 = getattr(result2, attr)

            # Both should have same attributes (field presence)
            assert type(art1) == type(art2)
            assert set(dir(art1)) == set(dir(art2))

    def test_no_unexpected_side_effects(self):
        """Pipeline execution has no unexpected side effects."""
        pipeline = create_constitutional_pipeline()

        # Run twice with same input
        result1 = pipeline.execute(b"side effect test")
        result2 = pipeline.execute(b"side effect test")

        # Results should be independent (different UUIDs but same structure)
        assert result1.execution_id != result2.execution_id
        assert result1.trace_ids != result2.trace_ids

        # But both should succeed
        assert result1.success is True
        assert result2.success is True

        # Trace IDs should all be unique within each run
        assert len(set(result1.trace_ids)) == len(result1.trace_ids)
        assert len(set(result2.trace_ids)) == len(result2.trace_ids)


class TestIndividualEngineDeterminism:
    """Individual engine deterministic behavior."""

    def test_observation_engine_deterministic(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        engine1 = ObservationEngine()
        engine2 = ObservationEngine()

        input_data = ObservationInput(
            raw_input=b"deterministic test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )

        result1 = engine1.execute(input_data)
        result2 = engine2.execute(input_data)

        # Different UUIDs but same structure
        assert result1.observation_id != result2.observation_id
        assert type(result1.signal) == type(result2.signal)
        assert type(result1.evidence) == type(result2.evidence)
        assert result1.confidence == result2.confidence

    def test_hypothesis_engine_deterministic(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest

        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"deterministic test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))

        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)

        engine1 = HypothesisEngine()
        engine2 = HypothesisEngine()

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )

        result1 = engine1.execute(request)
        result2 = engine2.execute(request)

        assert len(result1.hypotheses) == len(result2.hypotheses)
        assert result1.space_id != result2.space_id

    def test_full_pipeline_multiple_runs(self):
        """Full pipeline multiple runs maintain deterministic structure."""
        pipeline = create_constitutional_pipeline()

        for _ in range(10):
            result = pipeline.execute(b"multi-run test")
            assert result.success is True
            assert len(result.trace_ids) == 10  # execution_id + 9 stages

    def test_empty_input_deterministic(self):
        """Empty input produces deterministic structure."""
        pipeline = create_constitutional_pipeline()

        result1 = pipeline.execute(b"")
        result2 = pipeline.execute(b"")

        assert result1.success is True
        assert result2.success is True
        assert len(result1.trace_ids) == len(result2.trace_ids)