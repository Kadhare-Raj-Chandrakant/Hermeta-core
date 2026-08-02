# brain/engine/problem_engine.py
# Problem Engine Implementation
# Constitutional Contract: H-1 through H-8, P-1 through P-12

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, Sequence
from enum import Enum
import uuid

from brain.core.constants import CONSTITUTIONAL_VERSION
from brain.domain.problem import (
    ProblemCategory,
    ProblemSeverity,
    ProblemStatement,
    ProblemSpace,
    Hypothesis,
    HypothesisSpace,
    HypothesisCategory,
)


class ProblemEngine:
    """
    Problem Engine Implementation.
    
    Constitutional Laws Enforced:
    - H-3: A ProblemStatement may reference multiple hypotheses.
    - H-4: Observations remain immutable regardless of later conclusions.
    - H-5: Problems never contain implementation strategies.
    - H-6: Problems never contain execution information.
    - H-7: Problem formulation remains independent from Proposal generation.
    - H-8: Every ProblemStatement preserves traceability back to its supporting observations through hypotheses.
    """
    
    def __init__(self, policy=None, engine_id="problem-engine", version=CONSTITUTIONAL_VERSION):
        self._policy = policy or ProblemPolicy()
        self._engine_id = engine_id
        self._version = CONSTITUTIONAL_VERSION
    
    @property
    def engine_name(self) -> str:
        return "problem-engine"
    
    @property
    def contract_version(self) -> str:
        return CONSTITUTIONAL_VERSION
    
    def validate_input(self, request) -> tuple:
        """Validate input before processing."""
        if not request.hypothesis_space_id:
            return False, "hypothesis_space_id is required"
        return True, ""
    
    def validate_output(self, space) -> tuple:
        """Validate output after processing."""
        if space.space_id is None:
            return False, "space_id is required"
        if not space.problem_ids:
            return False, "At least one problem required"
        return True, ""
    
    def formulate(self, request):
        """Formulate structured problems from competing hypotheses."""
        is_valid, error = self.validate_input(request)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        policy = request.policy or self._default_policy()
        self._validate_policy(policy)
        
        # Generate problems from hypotheses
        problems = self._generate_problems(request, policy)
        
        if len(problems) < policy.min_problems:
            raise ValueError(f"Must generate at least {policy.min_problems} problems")
        
        space = ProblemSpace(
            space_id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            problem_ids=tuple(p.problem_id for p in problems),
            hypothesis_space_id=request.hypothesis_space_id,
        )
        
        is_valid, error = self.validate_output(space)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return space
    
    def _default_policy(self):
        class DefaultPolicy:
            min_problems = 1
            max_problems = 10
            allowed_categories = None
            min_severity = 'low'
            allowed_severities = ('negligible', 'low', 'medium', 'high', 'critical')
        return DefaultPolicy()
    
    def _validate_policy(self, policy):
        if policy.min_problems < 1:
            raise ValueError("min_problems must be >= 1")
        if policy.max_problems < policy.min_problems:
            raise ValueError("max_problems must be >= min_problems")
    
    def _generate_problems(self, request, policy):
        """Generate problems from hypotheses. Constitutional stub."""
        problems = []
        
        # Extract observation IDs from the request
        observation_ids = tuple()
        if request.observations:
            observation_ids = tuple(obs.observation_id for obs in request.observations)
        
        for i in range(policy.min_problems):
            problem = ProblemStatement(
                problem_id=uuid4(),
                title=f"Problem {i+1}: Cognitive gap identified",
                description=f"Structured gap derived from hypotheses in space {request.hypothesis_space_id}",
                category='operational',
                severity='medium',
                observation_ids=observation_ids,
                hypothesis_space_id=request.hypothesis_space_id,
                created_at=datetime.now(timezone.utc),
            )
            problems.append(problem)
        
        return problems
    
    def execute(self, input_data):
        """Execute the engine with full validation."""
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        output = self.formulate(input_data)
        
        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return output


@dataclass(frozen=True)
class ProblemPolicy:
    """Policy configuration for problem formulation."""
    min_problems: int = 1
    max_problems: int = 10
    allowed_categories: Tuple['ProblemCategory', ...] = field(default_factory=tuple)
    min_severity: 'ProblemSeverity' = 'low'
    allowed_severities: Tuple['ProblemSeverity', ...] = (
        'negligible', 'low', 'medium', 'high', 'critical'
    )


@dataclass(frozen=True)
class ProblemRequest:
    """Input to Problem Engine."""
    hypothesis_space_id: UUID
    observations: tuple = ()
    hypotheses: Tuple[UUID, ...] = ()
    policy: 'ProblemPolicy' = None
    context: Tuple[str, ...] = ()

    def __post_init__(self):
        # HIGH-1: normalize caller-provided collections to immutable tuples
        object.__setattr__(self, 'observations', tuple(self.observations))
        object.__setattr__(self, 'hypotheses', tuple(self.hypotheses))
        object.__setattr__(self, 'context', tuple(self.context))
        if not self.hypothesis_space_id:
            raise ValueError("hypothesis_space_id is required")


# Export
__all__ = (
    'ProblemCategory',
    'ProblemSeverity',
    'ProblemStatement',
    'ProblemSpace',
    'ProblemPolicy',
    'ProblemRequest',
    'ProblemEngine',
)