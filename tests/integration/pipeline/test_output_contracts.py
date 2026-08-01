"""Output contract validation tests.

Validates that every engine produces artifacts satisfying the downstream
engine's declared input contract.
"""

import uuid
from datetime import datetime, timezone

import pytest

from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest
from brain.engine.problem_engine import ProblemEngine, ProblemRequest
from brain.engine.proposal_engine import ProposalEngine
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest
from brain.engine.execution_engine import ExecutionEngine, ExecutionContext


class TestOutputContractValidation:
    """Validate produced artifacts are immediately consumable by downstream engine."""

    def setup_method(self):
        self.obs_engine = ObservationEngine()
        self.hyp_engine = HypothesisEngine()
        self.prob_engine = ProblemEngine()
        self.prop_engine = ProposalEngine()
        self.eval_engine = EvaluationEngine()
        self.gov_engine = GovernanceEngine()
        self.auth_engine = AuthorizationEngine()
        self.exec_engine = ExecutionEngine()

    def _make_observation(self):
        return self.obs_engine.execute(ObservationInput(
            raw_input=b"test signal for output validation",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))

    def test_observation_output_satisfies_hypothesis_input(self):
        """Observation output must be valid HypothesisEngine input."""
        obs = self._make_observation()

        # HypothesisEngine requires: observation_ids, observations, evidence
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )

        # Should not raise validation error
        result = self.hyp_engine.execute(request)
        assert result is not None
        assert len(result.hypotheses) >= 2

    def test_hypothesis_output_satisfies_problem_input(self):
        """HypothesisSpace output must be valid ProblemEngine input."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hypothesis_space = self.hyp_engine.execute(hyp_request)

        # ProblemEngine requires: hypothesis_space_id, observations, hypotheses
        hypothesis_ids = tuple(h.hypothesis_id for h in hypothesis_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hypothesis_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )

        result = self.prob_engine.execute(prob_request)
        assert result is not None
        assert len(result.problem_ids) >= 1

    def test_problem_output_satisfies_proposal_input(self):
        """ProblemSpace output must be valid ProposalEngine input."""
        obs = self._make_observation()
        evidence = obs.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)

        hyp_request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        )
        hypothesis_space = self.hyp_engine.execute(hyp_request)

        hypothesis_ids = tuple(h.hypothesis_id for h in hypothesis_space.hypotheses)
        prob_request = ProblemRequest(
            hypothesis_space_id=hypothesis_space.space_id,
            observations=(obs,),
            hypotheses=hypothesis_ids,
            policy=None,
            context=(),
        )
        problem_space = self.prob_engine.execute(prob_request)

        # ProposalEngine requires: problem_statement_id, problem_space_id
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=problem_space.problem_ids[0],
            problem_space_id=problem_space.space_id,
            policy=None,
            context=(),
        )

        result = self.prop_engine.execute(request)
        assert result is not None
        assert len(result.proposals) >= 1

    def test_proposal_output_satisfies_evaluation_input(self):
        """ProposalSpace output must be valid EvaluationEngine input."""
        # Build full chain up to proposal
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)

        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))

        hyp_ids = tuple(h.hypothesis_id for h in hyp_space.hypotheses)
        prob_space = self.prob_engine.execute(ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=tuple(h.hypothesis_id for h in hyp_space.hypotheses),
            policy=None,
            context=(),
        ))

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        prop_space = self.prop_engine.execute(ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        ))

        # EvaluationEngine requires: proposal_id, proposal_space_id, problem_statement_id
        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )

        result = self.eval_engine.execute(eval_request)
        assert result is not None
        assert len(result.dimensional_analyses) >= 1

    def test_evaluation_output_satisfies_governance_input(self):
        """EvaluationSpace output must be valid GovernanceEngine input."""
        # Build full chain
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)

        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))

        prob_space = self.prob_engine.execute(ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=tuple(h.hypothesis_id for h in hyp_space.hypotheses),
            policy=None,
            context=(),
        ))

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        prop_space = self.prop_engine.execute(ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        ))

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.eval_engine.evaluate_space(eval_request)

        # GovernanceEngine requires: evaluation_id
        gov_request = GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )

        result = self.gov_engine.adjudicate(gov_request)
        assert result is not None
        assert result.decision_id is not None

    def test_governance_output_satisfies_authorization_input(self):
        """GovernanceDecision output must be valid AuthorizationEngine input."""
        # Build chain up to governance
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)

        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))

        prob_space = self.prob_engine.execute(ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=tuple(h.hypothesis_id for h in hyp_space.hypotheses),
            policy=None,
            context=(),
        ))

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        prop_space = self.prop_engine.execute(ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        ))

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.eval_engine.evaluate_space(eval_request)

        gov_decision = self.gov_engine.adjudicate(GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        ))

        # AuthorizationEngine requires: governance_decision_id
        auth_request = AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )

        result = self.auth_engine.authorize(auth_request)
        assert result is not None
        assert result.authorization_id is not None

    def test_authorization_output_satisfies_execution_input(self):
        """AuthorizationToken output must be valid ExecutionEngine input."""
        # Build full chain
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)

        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))

        prob_space = self.prob_engine.execute(ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=tuple(h.hypothesis_id for h in hyp_space.hypotheses),
            policy=None,
            context=(),
        ))

        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        prop_space = self.prop_engine.execute(ProposalRequest(
            problem_statement_id=prob_space.problem_ids[0],
            problem_space_id=prob_space.space_id,
            policy=None,
            context=(),
        ))

        proposal_ids = tuple(p.proposal_id for p in prop_space.proposals)
        eval_request = EvaluationRequest(
            proposal_id=prop_space.proposals[0].proposal_id,
            proposal_ids=proposal_ids,
            proposal_space_id=prop_space.space_id,
            problem_statement_id=prob_space.problem_ids[0],
            policy=None,
            context=(),
        )
        eval_space = self.eval_engine.evaluate_space(eval_request)

        gov_decision = self.gov_engine.adjudicate(GovernanceRequest(
            evaluation_id=eval_space.evaluations[0].evaluation_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        ))

        auth_record = self.auth_engine.authorize(AuthorizationRequest(
            governance_decision_id=gov_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        ))

        token = self.auth_engine.issue_token(auth_record.authorization_id)

        # ExecutionEngine requires: execution_plan_id, authorization_token_id
        exec_context = ExecutionContext(
            execution_plan_id=uuid.uuid4(),
            authorization_token_id=token.token_id,
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )

        result = self.exec_engine.execute(exec_context)
        assert result is not None
        assert result.execution_result_id is not None


class TestOutputFieldIntegrity:
    """Verify produced artifacts have required field integrity."""

    def setup_method(self):
        self.obs_engine = ObservationEngine()
        self.hyp_engine = HypothesisEngine()
        self.prob_engine = ProblemEngine()
        self.prop_engine = ProposalEngine()
        self.eval_engine = EvaluationEngine()
        self.gov_engine = GovernanceEngine()
        self.auth_engine = AuthorizationEngine()
        self.exec_engine = ExecutionEngine()

    def test_observation_has_required_fields(self):
        obs = self.obs_engine.execute(ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))
        assert obs.observation_id is not None
        assert obs.signal is not None
        assert obs.evidence is not None
        assert obs.confidence >= 0.0 and obs.confidence <= 1.0

    def test_hypothesis_has_required_fields(self):
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)
        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))
        assert hyp_space.space_id is not None
        assert hyp_space.hypotheses is not None
        assert len(hyp_space.hypotheses) >= 2
        for hyp in hyp_space.hypotheses:
            assert hyp.hypothesis_id is not None
            assert hyp.title is not None
            assert hyp.description is not None
            assert hyp.confidence >= 0.0 and hyp.confidence <= 1.0
            assert hyp.category is not None
            assert hyp.supporting_observation_ids is not None

    def test_problem_statement_has_required_fields(self):
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)
        hyp_space = self.hyp_engine.execute(HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=evidence,
            policy=None,
        ))
        prob_space = self.prob_engine.execute(ProblemRequest(
            hypothesis_space_id=hyp_space.space_id,
            observations=(obs,),
            hypotheses=tuple(h.hypothesis_id for h in hyp_space.hypotheses),
            policy=None,
            context=(),
        ))
        # ProblemSpace has problem_ids
        assert prob_space.space_id is not None
        assert prob_space.problem_ids is not None
        assert len(prob_space.problem_ids) >= 1

    def _make_observation(self):
        return self.obs_engine.execute(ObservationInput(
            raw_input=b"test signal",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))