# Constitutional Pipeline Orchestrator

"""
Orchestrates the 8-stage constitutional cognitive pipeline.
The orchestrator is responsible ONLY for sequencing:
- invoking engines in order
- passing artifacts between engines
- preserving pipeline order
- maintaining traceability
- handling deterministic flow

The orchestrator knows contracts, NOT engine internals.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Tuple, Any
from uuid import UUID, uuid4

from brain.engine.base import EngineContract, EngineContext, EngineMetadata, EngineResult
from brain.engine.observation_engine import ObservationEngine, ObservationInput, SystemObservation
from brain.engine.hypothesis_engine import HypothesisEngine, HypothesisRequest, HypothesisSpace
from brain.engine.problem_engine import ProblemEngine, ProblemRequest, ProblemStatement, ProblemSpace
from brain.engine.proposal_engine import ProposalEngine, ProposalSpace
from brain.engine.evaluation_engine import EvaluationEngine, EvaluationRequest, Evaluation, EvaluationSpace
from brain.engine.governance_engine import GovernanceEngine, GovernanceRequest, GovernanceDecision
from brain.engine.authorization_engine import AuthorizationEngine, AuthorizationRequest, AuthorizationRecord, AuthorizationToken
from brain.engine.execution_engine import ExecutionEngine, ExecutionResult, ExecutionReceipt, ExecutionContext
from brain.engine.exceptions import EngineException


@dataclass(frozen=True)
class PipelineContext:
    """Context passed through the pipeline for traceability."""
    execution_id: UUID
    constitutional_version: str
    started_at: datetime
    trace_ids: Tuple[UUID, ...]
    metadata: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PipelineResult:
    """Result of full pipeline execution."""
    execution_id: UUID
    success: bool
    completed_at: datetime
    trace_ids: Tuple[UUID, ...]
    observation: Optional[SystemObservation] = None
    hypothesis_space: Optional[HypothesisSpace] = None
    problem_statement: Optional[ProblemStatement] = None
    problem_space: Optional[ProblemSpace] = None
    proposal_space: Optional[ProposalSpace] = None
    evaluation: Optional[Evaluation] = None
    evaluation_space: Optional[EvaluationSpace] = None
    governance_decision: Optional[GovernanceDecision] = None
    authorization_record: Optional[AuthorizationRecord] = None
    authorization_token: Optional[AuthorizationToken] = None
    execution_result: Optional[ExecutionResult] = None
    execution_receipt: Optional[ExecutionReceipt] = None
    error: Optional[str] = None


class PipelineOrchestrator:
    """
    Constitutional pipeline orchestrator.
    
    Sequences the 8 engines in the constitutional order:
    Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
    
    The orchestrator:
    - Knows engine contracts (input/output types)
    - Does NOT know engine internals
    - Does NOT perform reasoning
    - Does NOT generate domain artifacts
    - Only handles sequencing and artifact passing
    """
    
    def __init__(
        self,
        observation_engine: Optional[ObservationEngine] = None,
        hypothesis_engine: Optional[HypothesisEngine] = None,
        problem_engine: Optional[ProblemEngine] = None,
        proposal_engine: Optional[ProposalEngine] = None,
        evaluation_engine: Optional[EvaluationEngine] = None,
        governance_engine: Optional[GovernanceEngine] = None,
        authorization_engine: Optional[AuthorizationEngine] = None,
        execution_engine: Optional[ExecutionEngine] = None,
        constitutional_version: str = "1.0.0",
    ):
        self._observation_engine = observation_engine or ObservationEngine()
        self._hypothesis_engine = hypothesis_engine or HypothesisEngine()
        self._problem_engine = problem_engine or ProblemEngine()
        self._proposal_engine = proposal_engine or ProposalEngine()
        self._evaluation_engine = evaluation_engine or EvaluationEngine()
        self._governance_engine = governance_engine or GovernanceEngine()
        self._authorization_engine = authorization_engine or AuthorizationEngine()
        self._execution_engine = execution_engine or ExecutionEngine()
        self._constitutional_version = constitutional_version
    
    @property
    def constitutional_version(self) -> str:
        return self._constitutional_version
    
    def _create_context(self, parent_trace_ids: Tuple[UUID, ...] = ()) -> PipelineContext:
        """Create a new pipeline context with traceability."""
        execution_id = uuid4()
        started_at = datetime.now(timezone.utc)
        trace_ids = parent_trace_ids + (execution_id,)
        return PipelineContext(
            execution_id=execution_id,
            constitutional_version=self._constitutional_version,
            started_at=started_at,
            trace_ids=trace_ids,
        )
    
    def _extract_trace_id(self, artifact: Any) -> Optional[UUID]:
        """Extract trace ID from an artifact if it has one.
        
        Returns the artifact's primary identifier, not reference IDs.
        Reference IDs are for traceability, not for identifying the artifact itself.
        """
        if hasattr(artifact, 'trace_id'):
            return artifact.trace_id
        # Primary IDs (artifact's own identity)
        if hasattr(artifact, 'observation_id'):
            return artifact.observation_id
        if hasattr(artifact, 'space_id'):  # HypothesisSpace, ProposalSpace, EvaluationSpace, ProblemSpace
            return artifact.space_id
        if hasattr(artifact, 'problem_id'):  # ProblemStatement primary ID
            return artifact.problem_id
        if hasattr(artifact, 'decision_id'):  # GovernanceDecision primary ID
            return artifact.decision_id
        if hasattr(artifact, 'evaluation_id'):  # Evaluation primary ID
            return artifact.evaluation_id
        if hasattr(artifact, 'proposal_id'):  # Proposal primary ID
            return artifact.proposal_id
        if hasattr(artifact, 'authorization_id'):  # AuthorizationRecord primary ID
            return artifact.authorization_id
        if hasattr(artifact, 'token_id'):  # AuthorizationToken primary ID
            return artifact.token_id
        if hasattr(artifact, 'execution_result_id'):  # ExecutionResult primary ID
            return artifact.execution_result_id
        if hasattr(artifact, 'receipt_id'):  # ExecutionReceipt primary ID
            return artifact.receipt_id
        if hasattr(artifact, 'plan_id'):  # ExecutionPlan primary ID
            return artifact.plan_id
        if hasattr(artifact, 'context_id'):  # ExecutionContext primary ID
            return artifact.context_id
        # Reference IDs (for traceability chain, not artifact identity)
        if hasattr(artifact, 'problem_statement_id'):
            return artifact.problem_statement_id
        if hasattr(artifact, 'hypothesis_space_id'):
            return artifact.hypothesis_space_id
        if hasattr(artifact, 'authorization_record_id'):
            return artifact.authorization_record_id
        if hasattr(artifact, 'authorization_token_id'):
            return artifact.authorization_token_id
        if hasattr(artifact, 'execution_receipt_id'):
            return artifact.execution_receipt_id
        return None

    def execute(self, raw_input: Any) -> PipelineResult:
        """
        Execute the full constitutional pipeline.
        
        Args:
            raw_input: Raw environmental input for the Observation engine
            
        Returns:
            PipelineResult with all stage outputs and traceability
        """
        context = self._create_context()
        trace_ids = context.trace_ids
        
        try:
            # Stage 1: Observation
            observation = self._run_observation(raw_input, trace_ids)
            trace_ids += (self._extract_trace_id(observation),)
            
            # Stage 2: Hypothesis
            hypothesis_space = self._run_hypothesis(observation, trace_ids)
            trace_ids += (self._extract_trace_id(hypothesis_space),)
            
            # Stage 3: Problem
            problem_space = self._run_problem(observation, hypothesis_space, trace_ids)
            # ProblemSpace only has IDs, create ProblemStatement inline for pipeline
            if problem_space.problem_ids:
                from brain.engine.problem_engine import ProblemStatement
                problem_statement = ProblemStatement(
                    problem_id=problem_space.problem_ids[0],
                    title="Structured cognitive gap",
                    description="Derived from competing hypotheses",
                    category='operational',
                    severity='medium',
                    observation_ids=(observation.observation_id,),
                    hypothesis_space_id=hypothesis_space.space_id,
                    created_at=datetime.now(timezone.utc),
                )
            trace_ids += (self._extract_trace_id(problem_statement),)
            
            # Stage 4: Proposal
            proposal_space = self._run_proposal(problem_statement, problem_space, trace_ids)
            trace_ids += (self._extract_trace_id(proposal_space),)
            
            # Stage 5: Evaluation
            evaluation, evaluation_space = self._run_evaluation(proposal_space, problem_statement, trace_ids)
            trace_ids += (self._extract_trace_id(evaluation),)
            trace_ids += (self._extract_trace_id(evaluation_space),)
            
            # Stage 6: Governance
            governance_decision = self._run_governance(evaluation, evaluation_space, trace_ids)
            trace_ids += (self._extract_trace_id(governance_decision),)
            
            # Stage 7: Authorization
            authorization_record, authorization_token = self._run_authorization(governance_decision, trace_ids)
            trace_ids += (self._extract_trace_id(authorization_record),)
            
            # Stage 8: Execution
            execution_result, execution_receipt = self._run_execution(authorization_token, trace_ids)
            trace_ids += (self._extract_trace_id(execution_result),)
            
            completed_at = datetime.now(timezone.utc)
            return PipelineResult(
                execution_id=context.execution_id,
                success=True,
                observation=observation,
                hypothesis_space=hypothesis_space,
                problem_statement=problem_statement,
                problem_space=problem_space,
                proposal_space=proposal_space,
                evaluation=evaluation,
                evaluation_space=evaluation_space,
                governance_decision=governance_decision,
                authorization_record=authorization_record,
                authorization_token=authorization_token,
                execution_result=execution_result,
                execution_receipt=execution_receipt,
                trace_ids=trace_ids,
                completed_at=completed_at,
            )
            
        except EngineException as e:
            completed_at = datetime.now(timezone.utc)
            return PipelineResult(
                execution_id=context.execution_id,
                success=False,
                error=str(e),
                trace_ids=trace_ids,
                completed_at=completed_at,
            )
        except Exception as e:
            completed_at = datetime.now(timezone.utc)
            return PipelineResult(
                execution_id=context.execution_id,
                success=False,
                error=f"Pipeline execution failed: {e}",
                trace_ids=trace_ids,
                completed_at=completed_at,
            )
    
    def _run_observation(self, raw_input: Any, trace_ids: Tuple[UUID, ...]) -> SystemObservation:
        """Run Observation engine."""
        from brain.engine.observation_engine import ObservationPolicy
        
        # Reject None input explicitly - constitutional boundary enforcement
        if raw_input is None:
            raise ValueError("raw_input cannot be None")
        if not isinstance(raw_input, bytes):
            raise TypeError("raw_input must be bytes")
        
        input_data = ObservationInput(
            raw_input=raw_input,
            category='operational',
            detection_source='pipeline_orchestrator',
            metadata=tuple(trace_ids),
            policy=ObservationPolicy(),
        )
        return self._observation_engine.execute(input_data)
    
    def _run_hypothesis(self, observation: SystemObservation, trace_ids: Tuple[UUID, ...]) -> HypothesisSpace:
        """Run Hypothesis engine."""
        # Observation.evidence is a single ObservationEvidence, wrap in tuple
        evidence = observation.evidence
        if not isinstance(evidence, tuple):
            evidence = (evidence,)
        request = HypothesisRequest(
            observation_ids=(observation.observation_id,),
            observations=(observation,),
            evidence=evidence,
            policy=None,
        )
        return self._hypothesis_engine.execute(request)
    
    def _run_problem(self, observation: SystemObservation, hypothesis_space: HypothesisSpace, trace_ids: Tuple[UUID, ...]) -> ProblemSpace:
        """Run Problem engine."""
        # hypothesis_space has space_id, not hypothesis_space_id
        # hypothesis_space has hypotheses (tuple of Hypothesis objects)
        hypothesis_ids = tuple(h.hypothesis_id for h in hypothesis_space.hypotheses) if hypothesis_space.hypotheses else tuple()
        
        request = ProblemRequest(
            hypothesis_space_id=hypothesis_space.space_id,
            observations=(observation,),  # Pass the original observation
            hypotheses=hypothesis_ids,
            policy=None,
            context=trace_ids,
        )
        problem_space = self._problem_engine.execute(request)
        return problem_space
    
    def _run_proposal(self, problem_statement: ProblemStatement, problem_space: ProblemSpace, trace_ids: Tuple[UUID, ...]) -> ProposalSpace:
        """Run Proposal engine."""
        # Create a simple request object with required attributes
        class ProposalRequest:
            def __init__(self, problem_statement_id, problem_space_id, policy=None, context=()):
                self.problem_statement_id = problem_statement_id
                self.problem_space_id = problem_space_id
                self.policy = policy
                self.context = context
        
        request = ProposalRequest(
            problem_statement_id=problem_statement.problem_id,
            problem_space_id=problem_space.space_id,
            policy=None,
            context=trace_ids,
        )
        return self._proposal_engine.execute(request)
    
    def _run_evaluation(self, proposal_space: ProposalSpace, problem_statement: ProblemStatement, trace_ids: Tuple[UUID, ...]) -> Tuple[Evaluation, EvaluationSpace]:
        """Run Evaluation engine."""
        # Evaluate all proposals in the space using evaluate_space
        proposal_ids = tuple(p.proposal_id for p in proposal_space.proposals)
        first_proposal_id = proposal_ids[0] if proposal_ids else None
        if first_proposal_id:
            eval_request = EvaluationRequest(
                proposal_id=first_proposal_id,
                proposal_ids=proposal_ids,
                proposal_space_id=proposal_space.space_id,
                problem_statement_id=problem_statement.problem_id,
                policy=None,
                context=trace_ids,
            )
            evaluation = self._evaluation_engine.execute(eval_request)
        else:
            evaluation = None
        
        # Also evaluate all proposals to get the evaluation space
        eval_space_request = EvaluationRequest(
            proposal_id=proposal_ids[0] if proposal_ids else uuid4(),
            proposal_ids=proposal_ids,
            proposal_space_id=proposal_space.space_id,
            problem_statement_id=problem_statement.problem_id,
            policy=None,
            context=trace_ids,
        )
        evaluation_space = self._evaluation_engine.evaluate_space(eval_space_request)
        return evaluation, evaluation_space
    
    def _run_governance(self, evaluation: Evaluation, evaluation_space: EvaluationSpace, trace_ids: Tuple[UUID, ...]) -> GovernanceDecision:
        """Run Governance engine."""
        # Use the evaluation that was produced by _run_evaluation
        request = GovernanceRequest(
            evaluation_id=evaluation.evaluation_id,
            policy_ids=tuple(),
            constitutional_version=self._constitutional_version,
            metadata=tuple(trace_ids),
        )
        return self._governance_engine.adjudicate(request)
    
    def _run_authorization(self, governance_decision: GovernanceDecision, trace_ids: Tuple[UUID, ...]) -> Tuple[AuthorizationRecord, AuthorizationToken]:
        """Run Authorization engine."""
        request = AuthorizationRequest(
            governance_decision_id=governance_decision.decision_id,
            policy_ids=tuple(),
            constitutional_version=self._constitutional_version,
            metadata=tuple(trace_ids),
        )
        auth_record = self._authorization_engine.authorize(request)
        # Issue token from the record - field is authorization_id
        token = self._authorization_engine.issue_token(auth_record.authorization_id)
        return auth_record, token
    
    def _run_execution(self, authorization_token: AuthorizationToken, trace_ids: Tuple[UUID, ...]) -> Tuple[ExecutionResult, ExecutionReceipt]:
        """Run Execution engine."""
        context = ExecutionContext(
            execution_plan_id=uuid4(),  # placeholder
            authorization_token_id=authorization_token.token_id,
            constitutional_version=self._constitutional_version,
            created_at=datetime.now(timezone.utc),
        )
        result = self._execution_engine.execute(context)
        receipt = self._execution_engine.get_receipt(result.execution_result_id)
        return result, receipt


# For backward compatibility and testing
def create_constitutional_pipeline(
    observation_engine: Optional[ObservationEngine] = None,
    hypothesis_engine: Optional[HypothesisEngine] = None,
    problem_engine: Optional[ProblemEngine] = None,
    proposal_engine: Optional[ProposalEngine] = None,
    evaluation_engine: Optional[EvaluationEngine] = None,
    governance_engine: Optional[GovernanceEngine] = None,
    authorization_engine: Optional[AuthorizationEngine] = None,
    execution_engine: Optional[ExecutionEngine] = None,
    constitutional_version: str = "1.0.0",
) -> PipelineOrchestrator:
    """Create a constitutional pipeline with optional custom engines."""
    return PipelineOrchestrator(
        observation_engine=observation_engine,
        hypothesis_engine=hypothesis_engine,
        problem_engine=problem_engine,
        proposal_engine=proposal_engine,
        evaluation_engine=evaluation_engine,
        governance_engine=governance_engine,
        authorization_engine=authorization_engine,
        execution_engine=execution_engine,
        constitutional_version=constitutional_version,
    )


__all__ = (
    'PipelineContext',
    'PipelineResult',
    'PipelineOrchestrator',
    'create_constitutional_pipeline',
)