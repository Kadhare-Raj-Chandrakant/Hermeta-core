from enum import Enum


class ProblemCategory(Enum):
    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    RETRIEVAL = "retrieval"
    LEARNING = "learning"
    EVOLUTION = "evolution"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    ARCHITECTURE = "architecture"
    OPERATIONAL = "operational"


class ProblemSeverity(Enum):
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HypothesisCategory(Enum):
    CAUSAL = "causal"
    CORRELATIONAL = "correlational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    ENVIRONMENTAL = "environmental"