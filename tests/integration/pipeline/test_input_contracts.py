"""Input contract enforcement tests.

Validates that every engine rejects invalid inputs through its declared contract.
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
from brain.engine.exceptions import EngineInputValidationError


class TestObservationEngineInputContracts:
    """ObservationEngine input contract enforcement."""

    def setup_method(self):
        self.engine = ObservationEngine()

    def test_rejects_missing_raw_input(self):
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
        input_data = ObservationInput(
            raw_input=b"test",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=None,
        )
        with pytest.raises(ValueError, match="policy is required"):
            self.engine.execute(input_data)

    def test_rejects_empty_category(self):
        input_data = ObservationInput(
            raw_input=b"test",
            category="",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        with pytest.raises(ValueError):
            self.engine.execute(input_data)

    def test_rejects_invalid_category(self):
        input_data = ObservationInput(
            raw_input=b"test",
            category="invalid_category",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        )
        with pytest.raises(ValueError):
            self.engine.execute(input_data)


class TestHypothesisEngineInputContracts:
    """HypothesisEngine input contract enforcement."""

    def setup_method(self):
        self.engine = HypothesisEngine()

    def _make_observation(self):
        from brain.engine.observation_engine import ObservationEngine, ObservationInput, ObservationPolicy
        oe = ObservationEngine()
        return oe.execute(ObservationInput(
            raw_input=b"test signal",
            category="operational",
            detection_source="test",
            metadata=(),
            policy=ObservationPolicy(),
        ))

    def test_rejects_empty_observation_ids(self):
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)
        request = HypothesisRequest(
            observation_ids=(),
            observations=(),
            evidence=evidence,
            policy=None,
        )
        with pytest.raises(ValueError, match="observation_ids is required"):
            self.engine.execute(request)

    def test_rejects_empty_observations(self):
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)
        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(),
            evidence=evidence,
            policy=None,
        )
        with pytest.raises(ValueError, match="observations is required"):
            self.engine.execute(request)

    def test_rejects_empty_evidence(self):
        obs = self._make_observation()
        request = HypothesisRequest(
            observation_ids=(obs.observation_id,),
            observations=(obs,),
            evidence=(),
            policy=None,
        )
        with pytest.raises(ValueError, match="evidence is required"):
            self.engine.execute(request)

    def test_rejects_mismatched_observations_evidence(self):
        obs = self._make_observation()
        evidence = obs.evidence if isinstance(obs.evidence, tuple) else (obs.evidence,)
        request = HypothesisRequest(
            observation_ids=(obs.observation_id, obs.observation_id),
            observations=(obs, obs),
            evidence=evidence,
            policy=None,
        )
        with pytest.raises(ValueError, match="observations and evidence must have same length"):
            self.engine.execute(request)


class TestProblemEngineInputContracts:
    """ProblemEngine input contract enforcement."""

    def setup_method(self):
        self.engine = ProblemEngine()

    def test_rejects_missing_hypothesis_space_id(self):
        with pytest.raises(ValueError, match="hypothesis_space_id is required"):
            ProblemRequest(
                hypothesis_space_id=None,
                observations=(),
                hypotheses=(),
                policy=None,
                context=(),
            )


class TestProposalEngineInputContracts:
    """ProposalEngine input contract enforcement."""

    def setup_method(self):
        self.engine = ProposalEngine()

    def test_rejects_missing_problem_statement_id(self):
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context

        request = ProposalRequest(
            problem_statement_id=None,
            problem_space_id=uuid.uuid4(),
            policy=None,
            context=(),
        )
        with pytest.raises(ValueError, match="problem_statement_id is required"):
            self.engine.execute(request)


class TestEvaluationEngineInputContracts:
    """EvaluationEngine input contract enforcement."""

    def setup_method(self):
        self.engine = EvaluationEngine()

    def test_rejects_missing_proposal_id(self):
        request = EvaluationRequest(
            proposal_id=None,
            proposal_space_id=uuid.uuid4(),
            problem_statement_id=uuid.uuid4(),
            policy=None,
            context=(),
        )
        with pytest.raises(ValueError):
            self.engine.execute(request)


class TestGovernanceEngineInputContracts:
    """GovernanceEngine input contract enforcement."""

    def setup_method(self):
        self.engine = GovernanceEngine()

    def test_rejects_missing_evaluation_id(self):
        request = GovernanceRequest(
            evaluation_id=None,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        with pytest.raises(ValueError):
            self.engine.adjudicate(request)


class TestAuthorizationEngineInputContracts:
    """AuthorizationEngine input contract enforcement."""

    def setup_method(self):
        self.engine = AuthorizationEngine()

    def test_rejects_missing_governance_decision_id(self):
        request = AuthorizationRequest(
            governance_decision_id=None,
            policy_ids=tuple(),
            constitutional_version="1.0.0",
            metadata=tuple(),
        )
        with pytest.raises(ValueError):
            self.engine.authorize(request)


class TestExecutionEngineInputContracts:
    """ExecutionEngine input contract enforcement."""

    def setup_method(self):
        self.engine = ExecutionEngine()

    def test_rejects_missing_execution_plan_id(self):
        context = ExecutionContext(
            execution_plan_id=None,
            authorization_token_id=uuid.uuid4(),
            constitutional_version="1.0.0",
            created_at=datetime.now(timezone.utc),
        )
        with pytest.raises(ValueError):
            self.engine.execute(context)


class TestAllEnginesRejectNullInputs:
    """All engines reject None as input."""

    def test_observation_rejects_none(self):
        engine = ObservationEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)

    def test_hypothesis_rejects_none(self):
        engine = HypothesisEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)

    def test_problem_rejects_none(self):
        engine = ProblemEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)

    def test_proposal_rejects_none(self):
        engine = ProposalEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)

    def test_evaluation_rejects_none(self):
        engine = EvaluationEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)

    def test_governance_rejects_none(self):
        engine = GovernanceEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.adjudicate(None)

    def test_authorization_rejects_none(self):
        engine = AuthorizationEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.authorize(None)

    def test_execution_rejects_none(self):
        engine = ExecutionEngine()
        with pytest.raises((ValueError, TypeError, AttributeError)):
            engine.execute(None)