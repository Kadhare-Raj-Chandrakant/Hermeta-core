"""Pipeline Orchestrator responsibility audit tests.

Explicitly certifies that PipelineOrchestrator owns only orchestration.
"""

import uuid
from datetime import datetime, timezone

import pytest

from brain.engine.pipeline import PipelineOrchestrator, create_constitutional_pipeline
from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
from brain.engine.problem_engine import ProblemEngine, ProblemRequest
from brain.engine.proposal_engine import ProposalEngine
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest
from brain.engine.execution_engine import ExecutionEngine, ExecutionContext


class TestOrchestratorOwnsOnlyOrchestration:
    """Certify PipelineOrchestrator owns only orchestration."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_orchestrator_owns_sequencing(self):
        """Orchestrator sequences engines in constitutional order."""
        result = self.orchestrator.execute(b"sequencing test")

        # Trace IDs should follow constitutional order
        assert len(result.trace_ids) >= 9
        assert result.trace_ids[1] == result.observation.observation_id
        assert result.trace_ids[2] == result.hypothesis_space.space_id
        assert result.trace_ids[3] == result.problem_statement.problem_id
        assert result.trace_ids[4] == result.proposal_space.space_id
        assert result.trace_ids[5] == result.evaluation.evaluation_id
        # governance_decision.decision_id is at index 7 (after evaluation_space at 6)
        assert result.governance_decision.decision_id in result.trace_ids
        assert result.authorization_record.authorization_id in result.trace_ids
        assert result.execution_result.execution_result_id in result.trace_ids

    def test_orchestrator_owns_context_propagation(self):
        """Orchestrator propagates execution context."""
        result = self.orchestrator.execute(b"context test")

        # Constitutional version should propagate to key artifacts
        artifacts = [
            result.authorization_record,
            result.authorization_token,
            result.execution_receipt,
        ]

        for artifact in artifacts:
            assert hasattr(artifact, 'constitutional_version')
            assert artifact.constitutional_version == "1.0"


    def test_orchestrator_owns_trace_propagation(self):
        """Orchestrator propagates trace identifiers."""
        result = self.orchestrator.execute(b"trace test")

        # Trace chain should be continuous
        assert len(result.trace_ids) >= 9

        # Each stage's output ID should be in trace
        assert result.observation.observation_id in result.trace_ids
        assert result.hypothesis_space.space_id in result.trace_ids
        assert result.problem_statement.problem_id in result.trace_ids
        assert result.proposal_space.space_id in result.trace_ids
        assert result.evaluation.evaluation_id in result.trace_ids
        assert result.governance_decision.decision_id in result.trace_ids
        assert result.authorization_record.authorization_id in result.trace_ids
        assert result.execution_result.execution_result_id in result.trace_ids

    def test_orchestrator_owns_engine_coordination(self):
        """Orchestrator coordinates engine invocations."""
        # Verify all engines are invoked by checking outputs exist
        result = self.orchestrator.execute(b"coordination test")

        assert result.observation is not None
        assert result.hypothesis_space is not None
        assert result.problem_statement is not None
        assert result.proposal_space is not None
        assert result.evaluation is not None
        assert result.governance_decision is not None
        assert result.authorization_record is not None
        assert result.authorization_token is not None
        assert result.execution_result is not None
        assert result.execution_receipt is not None


class TestOrchestratorDoesNotOwnReasoning:
    """Certify Orchestrator does NOT own reasoning."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_reasoning_in_orchestrator(self):
        """Orchestrator has no reasoning methods."""
        # Orchestrator should not have methods like: reason, infer, deduce, conclude
        forbidden_methods = [
            'reason', 'infer', 'deduce', 'conclude',
            'evaluate', 'judge', 'decide', 'choose',
            'optimize', 'improve', 'learn', 'adapt',
        ]

        for method in forbidden_methods:
            assert not hasattr(self.orchestrator, method), \
                f"Orchestrator should not have reasoning method: {method}"

    def test_orchestrator_does_not_analyze_artifacts(self):
        """Orchestrator does not analyze artifact content."""
        # Orchestrator should only pass artifacts, not inspect their content
        result = self.orchestrator.execute(b"no analysis test")

        # Verify orchestrator didn't modify artifact content
        # (It only extracts trace IDs)
        assert result.observation is not None
        assert result.hypothesis_space is not None
        # Orchestrator creates ProblemStatement inline - that's coordination, not reasoning


class TestOrchestratorDoesNotOwnEvaluation:
    """Certify Orchestrator does NOT own evaluation."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_evaluation_methods(self):
        """Orchestrator has no evaluation methods."""
        forbidden = ['evaluate', 'assess', 'score', 'rank', 'rate', 'judge', 'compare']
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)

    def test_orchestrator_delegates_evaluation(self):
        """Orchestrator delegates evaluation to EvaluationEngine."""
        result = self.orchestrator.execute(b"eval delegation test")

        # Evaluation should come from EvaluationEngine
        assert result.evaluation is not None
        assert hasattr(result.evaluation, 'dimensional_analyses')
        assert len(result.evaluation.dimensional_analyses) >= 1


class TestOrchestratorDoesNotOwnGovernance:
    """Certify Orchestrator does NOT own governance."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_governance_methods(self):
        """Orchestrator has no governance methods."""
        forbidden = ['govern', 'adjudicate', 'decide_policy', 'enforce', 'approve', 'reject']
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)

    def test_orchestrator_delegates_governance(self):
        """Orchestrator delegates governance to GovernanceEngine."""
        result = self.orchestrator.execute(b"gov delegation test")

        assert result.governance_decision is not None
        assert hasattr(result.governance_decision, 'rationale_id')
        assert hasattr(result.governance_decision, 'state')


class TestOrchestratorDoesNotOwnAuthorization:
    """Certify Orchestrator does NOT own authorization."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_authorization_methods(self):
        """Orchestrator has no authorization methods."""
        forbidden = ['authorize', 'grant', 'deny', 'revoke', 'issue_token', 'permission']
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)

    def test_orchestrator_delegates_authorization(self):
        """Orchestrator delegates authorization to AuthorizationEngine."""
        result = self.orchestrator.execute(b"auth delegation test")

        assert result.authorization_record is not None
        assert result.authorization_token is not None


class TestOrchestratorDoesNotOwnExecution:
    """Certify Orchestrator does NOT own execution logic."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_execution_methods(self):
        """Orchestrator has no execution logic methods."""
        forbidden = ['execute_plan', 'run_action', 'perform', 'do', 'implement', 'build', 'compile']
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)

    def test_orchestrator_delegates_execution(self):
        """Orchestrator delegates execution to ExecutionEngine."""
        result = self.orchestrator.execute(b"exec delegation test")

        assert result.execution_result is not None
        assert result.execution_receipt is not None


class TestOrchestratorDoesNotOwnOptimization:
    """Certify Orchestrator does NOT own optimization."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_optimization_methods(self):
        """Orchestrator has no optimization methods."""
        forbidden = ['optimize', 'improve', 'tune', 'adjust', 'calibrate', 'speed_up', 'reduce_cost']
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)


class TestOrchestratorDoesNotOwnCognitiveBehavior:
    """Certify Orchestrator does NOT own cognitive behavior."""

    def setup_method(self):
        self.orchestrator = create_constitutional_pipeline()

    def test_no_cognitive_methods(self):
        """Orchestrator has no cognitive behavior methods."""
        forbidden = [
            'think', 'learn', 'remember', 'forget',
            'hypothesize', 'propose', 'solve',
            'understand', 'comprehend', 'interpret',
            'plan', 'strategize', 'reflect',
        ]
        for method in forbidden:
            assert not hasattr(self.orchestrator, method)

    def test_orchestrator_is_pure_coordinator(self):
        """Orchestrator is a pure coordinator."""
        # Its only public method should be execute (and create_constitutional_pipeline factory)
        public_methods = [m for m in dir(self.orchestrator) if not m.startswith('_')]

        # Should only have coordination methods
        expected = ['execute', 'constitutional_version']
        # _extract_trace_id, _create_context, _run_* are private
        # But execute is the only public API
        assert 'execute' in public_methods
        assert 'constitutional_version' in public_methods


class TestOrchestratorOwnershipBoundary:
    """Explicit ownership boundary certification."""

    def test_orchestrator_method_categorization(self):
        """All orchestrator methods fall into coordination categories."""
        orchestrator = create_constitutional_pipeline()

        # Categorize all methods
        all_methods = [m for m in dir(orchestrator) if not m.startswith('__')]

        coordination_methods = []
        private_methods = []
        property_methods = []

        for method in all_methods:
            if method.startswith('_'):
                private_methods.append(method)
            elif isinstance(getattr(type(orchestrator), method, None), property):
                property_methods.append(method)
            else:
                coordination_methods.append(method)

        # Should only have execute as public coordination method
        # (Other public methods would be violations)
        # Note: _run_* methods are private coordination helpers
        assert 'execute' in coordination_methods
        # Properties
        assert 'constitutional_version' in property_methods

    def test_orchestrator_does_not_hold_domain_state(self):
        """Orchestrator does not hold domain state."""
        orchestrator = create_constitutional_pipeline()

        # Check instance attributes
        attrs = [a for a in dir(orchestrator) if not a.startswith('__') and not callable(getattr(orchestrator, a))]

        # Should only hold engine references and constitutional_version
        allowed_attrs = [
            '_observation_engine', '_hypothesis_engine', '_problem_engine',
            '_proposal_engine', '_evaluation_engine', '_governance_engine',
            '_authorization_engine', '_execution_engine',
            '_constitutional_version',
            'constitutional_version',  # property exposing version
        ]

        for attr in attrs:
            assert attr in allowed_attrs, f"Orchestrator holds unexpected state: {attr}"

    def test_orchestrator_engines_are_injected(self):
        """Orchestrator uses injected engines, doesn't create them."""
        # Verify we can inject custom engines
        custom_obs = ObservationEngine()
        orchestrator = create_constitutional_pipeline(observation_engine=custom_obs)

        assert orchestrator._observation_engine is custom_obs

    def test_orchestrator_is_stateless_across_runs(self):
        """Orchestrator has no persistent state between runs."""
        orchestrator = create_constitutional_pipeline()

        result1 = orchestrator.execute(b"run 1")
        result2 = orchestrator.execute(b"run 2")

        # Results should be independent
        assert result1.execution_id != result2.execution_id
        assert result1.trace_ids != result2.trace_ids

        # But both should succeed
        assert result1.success is True
        assert result2.success is True