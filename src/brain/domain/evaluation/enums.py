from enum import Enum


class EvaluationDimension(Enum):
    """
    Evaluation dimensions represent descriptive reasoning aspects.

    These are NOT numerical scores.
    They are qualitative lenses through which proposals are analyzed.
    """

    ARCHITECTURAL_INTEGRITY = "architectural_integrity"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    EXPLAINABILITY = "explainability"
    PERFORMANCE = "performance"
    LEARNING_VALUE = "learning_value"
    CONSTITUTIONAL_SAFETY = "constitutional_safety"
    EVOLUTION_POTENTIAL = "evolution_potential"


class EvidenceType(Enum):
    """
    Types of evidence supporting an evaluation.

    Evidence is descriptive, not quantified.
    """

    OBSERVATION_BASED = "observation_based"
    HYPOTHESIS_BASED = "hypothesis_based"
    PROBLEM_BASED = "problem_based"
    PROPOSAL_BASED = "proposal_based"
    HISTORICAL_ANALOGY = "historical_analogy"
    THEORETICAL_REASONING = "theoretical_reasoning"


class EvaluationState(Enum):
    """
    Evaluation lifecycle state.

    This is NOT approval/rejection.
    This tracks evaluation completeness.
    """

    DRAFT = "draft"
    COMPLETE = "complete"
    SUPERSEDED = "superseded"