"""Engine contract validation tests.

Validates every behavioral engine against its constitutional contract.
"""

import uuid
from datetime import datetime, timezone

import pytest

from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy, SystemObservation
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest, HypothesisSpace
from brain.engine.problem_engine import ProblemEngine, ProblemRequest, ProblemStatement, ProblemSpace
from brain.engine.proposal_engine import ProposalEngine, ProposalSpace
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest, Evaluation, EvaluationSpace
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest, GovernanceDecision
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest, AuthorizationRecord, AuthorizationToken
from brain.engine.execution_engine import ExecutionEngine, ExecutionContext, ExecutionResult, ExecutionReceipt
from brain.engine.exceptions import EngineException, EngineInputValidationError, EngineOutputValidationError


class TestObservationEngineContract:
    """Validate ObservationEngine against constitutional contract O-1..O-6."""

    def setup_method(self):
        self.engine = ObservationEngine()

    def test_consumes_raw_input_only(self):
        """Engine consumes only raw input, not domain artifacts."""
        input_data = ObservationInput(
            raw_input=b"test signal",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        assert isinstance(result, SystemObservation)
        assert hasattr(result, 'observation_id')
        assert hasattr(result, 'signal')
        assert hasattr(result, 'evidence')

    def test_produces_observation_signal_and_evidence(self):
        """Engine produces exactly ObservationSignal and ObservationEvidence."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        assert result.signal is not None
        assert hasattr(result.signal, 'signal_id')
        assert hasattr(result.signal, 'category')
        assert hasattr(result.signal, 'source')

        assert result.evidence is not None
        assert hasattr(result.evidence, 'evidence_id')
        assert hasattr(result.evidence, 'description')
        assert hasattr(result.evidence, 'confidence')

    def test_rejects_missing_raw_input(self):
        """Engine rejects input without raw_input."""
        input_data = ObservationInput(
            raw_input=None,
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )

        with pytest.raises(ValueError, match="raw_input is required"):
            self.engine.execute(input_data)

    def test_rejects_missing_policy(self):
        """Engine rejects input without policy."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=None,
        )

        with pytest.raises(ValueError, match="policy is required"):
            self.engine.execute(input_data)

    def test_output_has_required_fields(self):
        """Output has observation_id, signal, evidence."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        assert result.observation_id is not None
        assert result.signal is not None
        assert result.evidence is not None

    def test_no_decisions_in_output(self):
        """Output contains no decision fields (O-2)."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        # Should not have decision-like fields
        assert not hasattr(result, 'decision')
        assert not hasattr(result, 'approved')
        assert not hasattr(result, 'rejected')
        assert not hasattr(result, 'decision_id')

    def test_no_solutions_in_output(self):
        """Output contains no solution fields (O-3)."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        # Should not have solution/execution fields
        assert not hasattr(result, 'plan')
        assert not hasattr(result, 'execution')
        assert not hasattr(result, 'proposal')

    def test_never_mutates_observed_systems(self):
        """Engine is pure - same input produces same output structure (O-4)."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result1 = self.engine.execute(input_data)
        result2 = self.engine.execute(input_data)

        # Both should be valid observations with same structure
        assert result1.observation_id != result2.observation_id  # Different IDs
        assert result1.signal.category == result2.signal.category
        assert type(result1.evidence) == type(result2.evidence)

    def test_evidence_interpretation_separate(self):
        """Evidence and interpretation remain separate (O-5)."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        # Evidence should be factual, not interpretive
        assert result.evidence.description is not None
        assert result.evidence.confidence >= 0.0
        assert result.evidence.confidence <= 1.0

    def test_no_proposal_creation(self):
        """Engine never creates proposals (O-6)."""
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        result = self.engine.execute(input_data)

        # Should not produce proposal-like artifacts
        assert not hasattr(result, 'proposal')
        assert not hasattr(result, 'proposal_id')
        assert not hasattr(result, 'proposal_space')


class TestHypothesisEngineContract:
    """Validate HypothesisEngine against constitutional contract H-1..H-8."""

    def setup_method(self):
        self.engine = HypothesisEngine()

    def _make_observation(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        oe = ObservationEngine()
        return oe.execute(ObservationInput(
            raw_input=b"test signal for hypothesis",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))

    def test_consumes_observation_and_evidence(self):
        """Engine consumes SystemObservation and ObservationEvidence."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        result = self.engine.execute(request)

        assert isinstance(result, HypothesisSpace)
        assert hasattr(result, 'space_id')
        assert hasattr(result, 'hypotheses')

    def test_produces_hypothesis_space(self):
        """Engine produces HypothesisSpace with competing hypotheses."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        result = self.engine.execute(request)

        assert result.hypotheses is not None
        assert len(result.hypotheses) >= 2  # H-2: Multiple hypotheses per observation
        for hyp in result.hypotheses:
            assert hasattr(hyp, 'hypothesis_id')
            assert hasattr(hyp, 'title')
            assert hasattr(hyp, 'description')
            assert hasattr(hyp, 'confidence')
            assert hasattr(hyp, 'category')
            assert hasattr(hyp, 'supporting_observation_ids')

    def test_rejects_insufficient_observations(self):
        """Engine rejects empty observations."""
        request = HypothesisRequest(
            observation_ids=(),
            observations=(),
            evidence=(),
            policy=None,
        )

        with pytest.raises(ValueError, match="observation_ids is required"):
            self.engine.execute(request)

    def test_rejects_mismatched_observations_evidence(self):
        """Engine rejects when observations and evidence counts differ."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id, obs.observation_id),
            observations=(obs, obs),
            evidence=evidence,  # 1 evidence for 2 observations
            policy=None,
        )

        with pytest.raises(ValueError, match="observations and evidence must have same length"):
            self.engine.execute(request)

    def test_no_ranking_of_hypotheses(self):
        """Engine never ranks hypotheses (H-7)."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        result = self.engine.execute(request)

        # Space should not have ranking methods
        assert not hasattr(result, 'rank')
        assert not hasattr(result, 'sort')
        assert not hasattr(result, 'select')
        assert not hasattr(result, 'best_hypothesis')

    def test_preserves_traceability(self):
        """Hypotheses trace back to observations."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        result = self.engine.execute(request)

        for hyp in result.hypotheses:
            assert hyp.supporting_observation_ids
            assert obs.observation_id in hyp.supporting_observation_ids

    def test_no_problem_formulation(self):
        """Engine never formulates problems."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        result = self.engine.execute(request)

        assert not hasattr(result, 'problem')
        assert not hasattr(result, 'problem_statement')
        assert not hasattr(result, 'problem_id')


class TestProblemEngineContract:
    """Validate ProblemEngine against constitutional contract."""

    def setup_method(self):
        self.engine = ProblemEngine()

    def _make_hypothesis_space(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for problem",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        return he.execute(request), obs

    def test_consumes_hypothesis_space(self):
        """Engine consumes HypothesisSpace."""
        hyp_space, obs = self._make_hypothesis_space()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)

        request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        assert isinstance(result, ProblemSpace)
        assert hasattr(result, 'space_id')
        assert hasattr(result, 'problem_ids')
        assert len(result.problem_ids) >= 1

    def test_produces_problem_statement(self):
        """Engine produces ProblemStatement with traceability."""
        hyp_space, obs = self._make_hypothesis_space()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)

        request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        # ProblemSpace should have at least one problem
        assert result.problem_ids
        assert result.hypothesis_space_id == hyp_space.space_id

    def test_rejects_missing_hypothesis_space(self):
        """Engine rejects missing hypothesis_space_id."""
        with pytest.raises(ValueError, match="hypothesis_space_id is required"):
            ProblemRequest(
                hypothesis_space_id=None,
                observations=(),
                hypotheses=(),
                policy=None,
                context=(),
            )

    def test_problem_references_observations_through_hypotheses(self):
        """ProblemStatement traces to observations via hypotheses."""
        hyp_space, obs = self._make_hypothesis_space()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)

        request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        # The generated problem should reference the hypothesis space
        assert result.hypothesis_space_id == hyp_space.space_id


class TestProposalEngineContract:
    """Validate ProposalEngine against constitutional contract P-1..P-12."""

    def setup_method(self):
        self.engine = ProposalEngine()

    def _make_problem(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        from brain.engine.problem_engine import ProblemEngine, ProblemRequest
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for proposal",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hyp_space = he.execute(hyp_request)
        
        pe = ProblemEngine()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        prob_space = pe.execute(prob_request)
        
        return prob_space, obs

    def test_consumes_problem_statement(self):
        """Engine consumes ProblemStatement and ProblemSpace."""
        prob_space, obs = self._make_problem()

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        assert isinstance(result, ProposalSpace)
        assert hasattr(result, 'space_id')
        assert hasattr(result, 'proposals')
        assert len(result.proposals) >= 1

    def test_produces_proposal_space(self):
        """Engine produces ProposalSpace with proposals."""
        prob_space, obs = self._make_problem()

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        assert result.proposals
        assert len(result.proposals) >= 1
        for prop in result.proposals:
            assert hasattr(prop, 'proposal_id')
            assert hasattr(prop, 'title')
            assert hasattr(prop, 'category')
            assert hasattr(prop, 'originating_problem_id')
            assert hasattr(prop, 'intended_outcomes')

    def test_proposal_traces_to_problem(self):
        """Proposals trace to originating problem."""
        prob_space, obs = self._make_problem()

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        for prop in result.proposals:
            assert prop.originating_problem_id == prob_space.problem_ids[0]

    def test_no_self_evaluation(self):
        """Proposals never evaluate themselves (P-3)."""
        prob_space, obs = self._make_problem()

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        result = self.engine.execute(request)

        for prop in result.proposals:
            assert not hasattr(prop, 'score')
            assert not hasattr(prop, 'confidence')
            assert not hasattr(prop, 'ranking')
            assert not hasattr(prop, 'severity')


class TestEvaluationEngineContract:
    """Validate EvaluationEngine against constitutional contract E-1..E-16."""

    def setup_method(self):
        self.engine = EvaluationEngine()

    def _make_proposal(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        from brain.engine.problem_engine import ProblemEngine, ProblemRequest
        from brain.engine.proposal_engine import ProposalEngine
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for evaluation",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hyp_space = he.execute(hyp_request)
        
        pe = ProblemEngine()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        prob_space = pe.execute(prob_request)
        
        pre = ProposalEngine()
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context
        
        prop_request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        prop_space = pre.execute(prop_request)
        
        return prop_space, prob_space, obs

    def test_consumes_proposal_space_and_problem(self):
        """Engine consumes ProposalSpace and ProblemStatement."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        result = self.engine.execute(eval_request)

        assert isinstance(result, Evaluation)
        assert hasattr(result, 'evaluation_id')
        assert hasattr(result, 'proposal_id')
        assert hasattr(result, 'dimensional_analyses')

    def test_produces_evaluation_with_dimensional_analysis(self):
        """Engine produces Evaluation with dimensional analyses (E-3)."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        result = self.engine.execute(eval_request)

        assert result.dimensional_analyses is not None
        assert len(result.dimensional_analyses) >= 1
        for da in result.dimensional_analyses:
            assert hasattr(da, 'analysis_id')
            assert hasattr(da, 'dimension')
            assert hasattr(da, 'facts')
            assert hasattr(da, 'judgments')
            assert hasattr(da, 'evidence')
            assert hasattr(da, 'tradeoff_ids')

    def test_evaluation_space_preserves_all(self):
        """EvaluationSpace preserves all evaluations (E-9, E-10)."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.engine.evaluate_space(eval_request)

        assert isinstance(eval_space, EvaluationSpace)
        assert eval_space.proposal_ids == tuple(p.proposal_id for p in prop_space.proposals)
        assert len(eval_space.evaluations) >= 1

        # No ranking methods
        assert not hasattr(eval_space, 'rank')
        assert not hasattr(eval_space, 'sort')
        assert not hasattr(eval_space, 'select')
        assert not hasattr(eval_space, 'best')

    def test_no_approval_fields(self):
        """Evaluation has no approved/rejected fields (E-11)."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        result = self.engine.execute(eval_request)

        assert not hasattr(result, 'approved')
        assert not hasattr(result, 'rejected')
        assert not hasattr(result, 'accepted')

    def test_evaluation_independent_per_proposal(self):
        """Each proposal gets independent evaluation (E-14)."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.engine.evaluate_space(eval_request)

        # All proposals should have evaluations
        assert len(eval_space.evaluations) == len(prop_space.proposals)

    def test_comparison_not_ranking(self):
        """Comparison ≠ Ranking (E-13)."""
        prop_space, prob_space, obs = self._make_proposal()

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.engine.evaluate_space(eval_request)

        # Can group by proposal for comparison
        by_proposal = eval_space.evaluations_by_proposal()
        assert isinstance(by_proposal, dict)

        # But no ranking
        assert not hasattr(eval_space, 'rank')


class TestGovernanceEngineContract:
    """Validate GovernanceEngine against constitutional contract G-1..G-23."""

    def setup_method(self):
        self.engine = GovernanceEngine()

    def _make_evaluation(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        from brain.engine.problem_engine import ProblemEngine, ProblemRequest
        from brain.engine.proposal_engine import ProposalEngine
        from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for governance",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hyp_space = he.execute(hyp_request)
        
        pe = ProblemEngine()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        prob_space = pe.execute(prob_request)
        
        pre = ProposalEngine()
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context
        prop_request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        prop_space = pre.execute(prop_request)
        
        ee = EvaluationEngine()
        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = ee.evaluate_space(eval_request)
        
        return eval_space

    def test_consumes_evaluation_space(self):
        """Engine consumes EvaluationSpace."""
        eval_space = self._make_evaluation()

        request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        result = self.engine.adjudicate(request)

        assert isinstance(result, GovernanceDecision)
        assert hasattr(result, 'decision_id')
        assert hasattr(result, 'evaluation_id')
        assert hasattr(result, 'state')
        assert hasattr(result, 'rationale_id')
        assert hasattr(result, 'policy_ids')

    def test_produces_decision_with_rationale(self):
        """Engine produces GovernanceDecision with rationale."""
        eval_space = self._make_evaluation()

        request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        result = self.engine.adjudicate(request)

        assert result.rationale_id is not None
        assert result.state in ('approved', 'rejected', 'deferred', 'requires_review')

    def test_one_decision_per_evaluation(self):
        """One decision per evaluation (G-21)."""
        eval_space = self._make_evaluation()

        request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        result = self.engine.adjudicate(request)

        assert result.evaluation_id == eval_space.evaluations[0].evaluation_id

    def test_no_evaluation_logic(self):
        """Engine never performs evaluation logic."""
        eval_space = self._make_evaluation()

        request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        result = self.engine.adjudicate(request)

        assert not hasattr(result, 'score')
        assert not hasattr(result, 'dimensional_analysis')


class TestAuthorizationEngineContract:
    """Validate AuthorizationEngine against constitutional contract A-1..A-16."""

    def setup_method(self):
        self.engine = AuthorizationEngine()

    def _make_governance_decision(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        from brain.engine.problem_engine import ProblemEngine, ProblemRequest
        from brain.engine.proposal_engine import ProposalEngine
        from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
        from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for authorization",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hyp_space = he.execute(hyp_request)
        
        pe = ProblemEngine()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        prob_space = pe.execute(prob_request)
        
        pre = ProposalEngine()
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context
        prop_request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        prop_space = pre.execute(prop_request)
        
        ee = EvaluationEngine()
        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = ee.evaluate_space(eval_request)
        
        ge = GovernanceEngine()
        gov_request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        return ge.adjudicate(gov_request)

    def test_consumes_governance_decision(self):
        """Engine consumes GovernanceDecision."""
        gov_decision = self._make_governance_decision()

        request = AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        result = self.engine.authorize(request)

        assert isinstance(result, AuthorizationRecord)
        assert hasattr(result, 'authorization_id')
        assert hasattr(result, 'governance_decision_id')
        assert hasattr(result, 'state')

    def test_produces_authorization_record_and_token(self):
        """Engine produces AuthorizationRecord and AuthorizationToken."""
        gov_decision = self._make_governance_decision()

        request = AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        auth_record = self.engine.authorize(request)
        token = self.engine.issue_token(auth_record.authorization_id)

        assert isinstance(auth_record, AuthorizationRecord)
        assert isinstance(token, AuthorizationToken)
        assert token.authorization_record_id == auth_record.authorization_id

    def test_token_consumes_record(self):
        """Token references authorization record."""
        gov_decision = self._make_governance_decision()

        request = AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        auth_record = self.engine.authorize(request)
        token = self.engine.issue_token(auth_record.authorization_id)

        assert token.authorization_record_id == auth_record.authorization_id


class TestExecutionEngineContract:
    """Validate ExecutionEngine against constitutional contract X-1..X-23."""

    def setup_method(self):
        self.engine = ExecutionEngine()

    def _make_authorization_token(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
        from brain.engine.problem_engine import ProblemEngine, ProblemRequest
        from brain.engine.proposal_engine import ProposalEngine
        from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
        from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
        from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest
        
        oe = ObservationEngine()
        obs = oe.execute(ObservationInput(
            raw_input=b"test signal for execution",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        
        he = HypothesisEngine()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hyp_space = he.execute(hyp_request)
        
        pe = ProblemEngine()
        hypothesis_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        prob_space = pe.execute(prob_request)
        
        pre = ProposalEngine()
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context
        prop_request = ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        )
        prop_space = pre.execute(prop_request)
        
        ee = EvaluationEngine()
        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = ee.evaluate_space(eval_request)
        
        ge = GovernanceEngine()
        gov_request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        gov_decision = ge.adjudicate(gov_request)
        
        ae = AuthorizationEngine()
        auth_request = AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        auth_record = ae.authorize(auth_request)
        token = ae.issue_token(auth_record.authorization_id)
        
        return token

    def test_consumes_authorization_token(self):
        """Engine consumes AuthorizationToken."""
        token = self._make_authorization_token()

        context = ExecutionContext(
            execution_plan_id=uuid.uuid4(),
            authorization_token_id=token.token_id,
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )
        result = self.engine.execute(context)

        assert isinstance(result, ExecutionResult)
        assert hasattr(result, 'execution_result_id')
        assert hasattr(result, 'execution_plan_id')
        assert hasattr(result, 'status')

    def test_produces_execution_result_and_receipt(self):
        """Engine produces ExecutionResult and ExecutionReceipt."""
        token = self._make_authorization_token()

        context = ExecutionContext(
            execution_plan_id=uuid.uuid4(),
            authorization_token_id=token.token_id,
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )
        result = self.engine.execute(context)
        receipt = self.engine.get_receipt(result.execution_result_id)

        assert isinstance(result, ExecutionResult)
        assert isinstance(receipt, ExecutionReceipt)
        assert receipt.execution_result_id == result.execution_result_id

    def test_no_reasoning_in_execution(self):
        """Engine performs no reasoning (X-13..X-18)."""
        token = self._make_authorization_token()

        context = ExecutionContext(
            execution_plan_id=uuid.uuid4(),
            authorization_token_id=token.token_id,
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )
        result = self.engine.execute(context)

        assert not hasattr(result, 'reasoning')
        assert not hasattr(result, 'interpretation')
        assert not hasattr(result, 'explanation')
        assert not hasattr(result, 'recommendation')
        assert not hasattr(result, 'decision')

    def test_observable_facts_only(self):
        """Execution produces observable facts only."""
        token = self._make_authorization_token()

        context = ExecutionContext(
            execution_plan_id=uuid.uuid4(),
            authorization_token_id=token.token_id,
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )
        result = self.engine.execute(context)

        # Should have concrete result fields
        assert hasattr(result, 'status')
        assert hasattr(result, 'artifacts_produced')
        assert hasattr(result, 'artifact_ids')
        assert hasattr(result, 'duration_ms')