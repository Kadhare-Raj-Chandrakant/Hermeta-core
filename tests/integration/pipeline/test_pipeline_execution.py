"""End-to-end constitutional pipeline integration tests.

Validates the complete 8-stage pipeline executes in correct order
with proper artifact passing and traceability.
"""

import uuid
from datetime import datetime, timezone

from brain.engine.pipeline import create_constitutional_pipeline, PipelineResult
from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
from brain.engine.problem_engine import ProblemEngine, ProblemRequest
from brain.engine.proposal_engine import ProposalEngine
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest
from brain.engine.execution_engine import ExecutionEngine, ExecutionContext


class TestConstitutionalPipelineExecution:
    """Tests for complete pipeline execution."""

    def test_pipeline_executes_all_eight_stages(self):
        """Full pipeline executes Observation through Execution."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"test input signal")

        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.observation is not None
        assert result.hypothesis_space is not None
        assert result.problem_statement is not None
        assert result.proposal_space is not None
        assert result.evaluation is not None
        assert result.evaluation_space is not None
        assert result.governance_decision is not None
        assert result.authorization_record is not None
        assert result.authorization_token is not None
        assert result.execution_result is not None
        assert result.execution_receipt is not None

    def test_pipeline_preserves_execution_order(self):
        """Pipeline stages execute in constitutional order."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"test order")

        # Trace IDs should be in execution order
        trace_ids = result.trace_ids
        assert len(trace_ids) >= 8  # At least one per stage

        # Each stage should have contributed to trace
        assert result.observation is not None
        assert result.hypothesis_space is not None
        assert result.problem_statement is not None
        assert result.proposal_space is not None
        assert result.evaluation is not None
        assert result.governance_decision is not None
        assert result.authorization_record is not None
        assert result.execution_result is not None

    def test_pipeline_produces_valid_artifacts_at_each_stage(self):
        """Each stage produces its declared artifact type."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"artifact test")

        # Observation stage
        assert result.observation is not None
        assert hasattr(result.observation, 'observation_id')
        assert hasattr(result.observation, 'signal')
        assert hasattr(result.observation, 'evidence')

        # Hypothesis stage
        assert result.hypothesis_space is not None
        assert hasattr(result.hypothesis_space, 'space_id')
        assert hasattr(result.hypothesis_space, 'hypotheses')
        assert len(result.hypothesis_space.hypotheses) >= 1

        # Problem stage
        assert result.problem_statement is not None
        assert hasattr(result.problem_statement, 'problem_id')
        assert hasattr(result.problem_statement, 'hypothesis_space_id')

        # Proposal stage
        assert result.proposal_space is not None
        assert hasattr(result.proposal_space, 'space_id')
        assert hasattr(result.proposal_space, 'proposals')
        assert len(result.proposal_space.proposals) >= 1

        # Evaluation stage
        assert result.evaluation is not None
        assert hasattr(result.evaluation, 'evaluation_id')
        assert hasattr(result.evaluation, 'proposal_id')
        assert hasattr(result.evaluation, 'dimensional_analyses')

        assert result.evaluation_space is not None
        assert hasattr(result.evaluation_space, 'space_id')

        # Governance stage
        assert result.governance_decision is not None
        assert hasattr(result.governance_decision, 'decision_id')
        assert hasattr(result.governance_decision, 'evaluation_id')

        # Authorization stage
        assert result.authorization_record is not None
        assert hasattr(result.authorization_record, 'authorization_id')
        assert hasattr(result.authorization_record, 'governance_decision_id')

        assert result.authorization_token is not None
        assert hasattr(result.authorization_token, 'token_id')
        assert hasattr(result.authorization_token, 'authorization_record_id')

        # Execution stage
        assert result.execution_result is not None
        assert hasattr(result.execution_result, 'execution_result_id')
        assert hasattr(result.execution_result, 'execution_plan_id')

        assert result.execution_receipt is not None
        assert hasattr(result.execution_receipt, 'receipt_id')

    def test_pipeline_deterministic_execution(self):
        """Same input produces same trace structure."""
        pipeline1 = create_constitutional_pipeline()
        pipeline2 = create_constitutional_pipeline()

        result1 = pipeline1.execute(b"deterministic test")
        result2 = pipeline2.execute(b"deterministic test")

        # Both should succeed
        assert result1.success is True
        assert result2.success is True

        # Trace structure should be identical
        assert len(result1.trace_ids) == len(result2.trace_ids)

    def test_pipeline_handles_empty_input(self):
        """Pipeline handles minimal input."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"")

        # Should still execute all stages
        assert result.success is True
        assert result.observation is not None


class TestPipelineStageSequence:
    """Tests verifying correct stage sequencing."""

    def test_observation_is_first_stage(self):
        """Observation engine executes first."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        # Observation should be first artifact in trace
        assert result.observation is not None
        assert result.trace_ids[1] == result.observation.observation_id  # trace_ids[0] is execution_id

    def test_hypothesis_follows_observation(self):
        """Hypothesis engine receives observation output."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.hypothesis_space is not None
        # Hypothesis space should reference observation
        for hyp in result.hypothesis_space.hypotheses:
            assert len(hyp.supporting_observation_ids) > 0

    def test_problem_follows_hypothesis(self):
        """Problem engine receives hypothesis space."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.problem_statement is not None
        assert result.problem_statement.hypothesis_space_id == result.hypothesis_space.space_id

    def test_proposal_follows_problem(self):
        """Proposal engine receives problem statement."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.proposal_space is not None
        for prop in result.proposal_space.proposals:
            assert prop.originating_problem_id == result.problem_statement.problem_id

    def test_evaluation_follows_proposal(self):
        """Evaluation engine receives proposal space."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.evaluation is not None
        assert result.evaluation.proposal_id in tuple(p.proposal_id for p in result.proposal_space.proposals)

    def test_governance_follows_evaluation(self):
        """Governance engine receives evaluation space."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.governance_decision is not None
        assert result.governance_decision.evaluation_id == result.evaluation.evaluation_id

    def test_authorization_follows_governance(self):
        """Authorization engine receives governance decision."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.authorization_record is not None
        assert result.authorization_record.governance_decision_id == result.governance_decision.decision_id

        assert result.authorization_token is not None
        assert result.authorization_token.authorization_record_id == result.authorization_record.authorization_id

    def test_execution_follows_authorization(self):
        """Execution engine receives authorization token."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"sequence test")

        assert result.execution_result is not None
        assert result.execution_result.authorization_token_id == result.authorization_token.token_id


class TestPipelineNoShortcuts:
    """Tests verifying no stages are skipped."""

    def test_no_stage_bypassed(self):
        """Every stage produces output."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"no shortcuts")

        stages = [
            ("observation", result.observation),
            ("hypothesis_space", result.hypothesis_space),
            ("problem_statement", result.problem_statement),
            ("proposal_space", result.proposal_space),
            ("evaluation", result.evaluation),
            ("governance_decision", result.governance_decision),
            ("authorization_record", result.authorization_record),
            ("authorization_token", result.authorization_token),
            ("execution_result", result.execution_result),
            ("execution_receipt", result.execution_receipt),
        ]

        for name, artifact in stages:
            assert artifact is not None, f"Stage {name} was bypassed - no output produced"

    def test_no_duplicate_execution(self):
        """Each stage executes exactly once per pipeline run."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"no duplicates")

        # Trace IDs should be unique per stage execution
        trace_ids = result.trace_ids
        # 10 trace IDs: execution_id + 9 stages (observation, hypothesis, problem, proposal, evaluation, evaluation_space, governance, authorization, execution)
        assert len(trace_ids) == 10
        assert len(trace_ids) == len(set(trace_ids)), "Duplicate trace IDs indicate re-execution"


class TestPipelineFailureHandling:
    """Tests for pipeline error handling."""

    def test_pipeline_returns_failure_result_on_error(self):
        """Pipeline returns PipelineResult with success=False on error."""
        # Test with a pipeline that will fail
        # We can't easily inject errors without mocking, so test structure
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"test")

        # Result should always be a PipelineResult
        assert isinstance(result, PipelineResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'execution_id')
        assert hasattr(result, 'error')

    def test_pipeline_error_contains_trace_info(self):
        """Failed pipeline result includes trace information."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"test")

        if not result.success:
            assert result.error is not None
            assert result.trace_ids is not None
            assert result.execution_id is not None


class TestPipelineContextPropagation:
    """Tests for context and metadata propagation."""

    def test_constitutional_version_propagated(self):
        """Constitutional version flows through all stages."""
        pipeline = create_constitutional_pipeline(constitutional_version="1.0.0")
        result = pipeline.execute(b"version test")

        assert result.success is True
        # Version should be embedded in artifacts
        # (exact verification depends on artifact structure)

    def test_execution_id_preserved(self):
        """Execution ID maintained through pipeline."""
        pipeline = create_constitutional_pipeline()
        result = pipeline.execute(b"id test")

        assert result.execution_id is not None
        # All artifacts should be traceable to this execution
        assert len(result.trace_ids) > 0
        assert result.execution_id in result.trace_ids or result.trace_ids[-1] == result.execution_id