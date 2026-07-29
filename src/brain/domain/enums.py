from enum import Enum


class KnowledgeType(Enum):
    DECISION = "decision"
    ARCHITECTURE = "architecture"
    GOAL = "goal"
    TASK = "task"
    BUG = "bug"
    PATTERN = "pattern"
    COMPONENT = "component"
    RULE = "rule"
    QUESTION = "question"
    DISCOVERY = "discovery"
    ASSUMPTION = "assumption"


class LifecycleState(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
