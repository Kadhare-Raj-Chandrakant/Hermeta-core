import uuid
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion
from brain.services.factors import (
    IntentMatch,
    KnowledgePriority,
    LifecycleStateFactor,
    RecencyFactor,
    RelationshipDistance,
)
from brain.services.relevance import RelevanceEngine, ScoredVersion
from brain.services.scoring import ScoringFactor


def make_version(
    title: str = "Event Sourcing",
    understanding: str = "System uses event sourcing for audit trail",
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    lifecycle_state: LifecycleState = LifecycleState.ACTIVE,
    version_number: int = 1,
    relationships: tuple[Relationship, ...] = (),
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=version_number,
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=0.8,
        lifecycle_state=lifecycle_state,
        evidence=(),
        relationships=relationships,
        created_at=datetime.now(timezone.utc),
    )


class TestDeterministicRanking:
    def test_same_input_same_output(self):
        engine = RelevanceEngine()
        versions = [
            make_version(title="Alpha", version_number=1),
            make_version(title="Beta", version_number=2),
        ]
        r1 = engine.rank("Alpha", versions)
        r2 = engine.rank("Alpha", versions)
        assert [s.version.title for s in r1] == [s.version.title for s in r2]

    def test_relevant_version_ranks_higher(self):
        engine = RelevanceEngine()
        relevant = make_version(title="Event Sourcing", version_number=1)
        irrelevant = make_version(title="Database Migration", version_number=1)
        results = engine.rank("Event Sourcing", [irrelevant, relevant])
        assert results[0].version is relevant


class TestStableOrdering:
    def test_equal_scores_stable(self):
        engine = RelevanceEngine(factors=[])
        v1 = make_version(title="A", version_number=1)
        v2 = make_version(title="B", version_number=1)
        results = engine.rank("query", [v1, v2])
        assert len(results) == 2

    def test_input_order_independent(self):
        engine = RelevanceEngine()
        v1 = make_version(title="Event Sourcing", version_number=1)
        v2 = make_version(title="Database", version_number=1)
        r1 = engine.rank("Event", [v1, v2])
        r2 = engine.rank("Event", [v2, v1])
        assert [s.version.title for s in r1] == [s.version.title for s in r2]


class TestFactorWeighting:
    def test_higher_weight_more_influence(self):
        strong_intent = IntentMatch(weight=0.9)
        weak_priority = KnowledgePriority(weight=0.1)
        engine = RelevanceEngine(factors=[strong_intent, weak_priority])

        v = make_version(title="Event Sourcing", knowledge_type=KnowledgeType.DISCOVERY)
        results = engine.rank("Event Sourcing", [v])
        assert results[0].score > 0.5

    def test_weight_affects_ranking(self):
        engine_a = RelevanceEngine(factors=[IntentMatch(weight=0.9), KnowledgePriority(weight=0.1)])
        engine_b = RelevanceEngine(factors=[IntentMatch(weight=0.1), KnowledgePriority(weight=0.9)])

        v1 = make_version(title="Match", knowledge_type=KnowledgeType.DISCOVERY)
        v2 = make_version(title="No Match", knowledge_type=KnowledgeType.DECISION)

        r_a = engine_a.rank("Match", [v1, v2])
        r_b = engine_b.rank("Match", [v1, v2])
        assert r_a[0].version is v1
        assert r_b[0].version is v2


class TestTieHandling:
    def test_ties_do_not_crash(self):
        engine = RelevanceEngine(factors=[])
        versions = [make_version(title="A", version_number=1) for _ in range(5)]
        results = engine.rank("query", versions)
        assert len(results) == 5

    def test_ties_preserve_all(self):
        engine = RelevanceEngine(factors=[])
        v1 = make_version(title="X", version_number=1)
        v2 = make_version(title="Y", version_number=1)
        results = engine.rank("query", [v1, v2])
        returned = {s.version.title for s in results}
        assert returned == {"X", "Y"}


class TestEmptyInput:
    def test_empty_versions_returns_empty(self):
        engine = RelevanceEngine()
        results = engine.rank("anything", [])
        assert results == []

    def test_empty_intent_still_scores(self):
        engine = RelevanceEngine()
        v = make_version(title="Something")
        results = engine.rank("", [v])
        assert len(results) == 1


class TestScoringBreakdown:
    def test_breakdown_contains_all_factors(self):
        engine = RelevanceEngine()
        v = make_version()
        results = engine.rank("test", [v])
        assert len(results) == 1
        breakdown = results[0].breakdown
        assert "intent_match" in breakdown
        assert "knowledge_priority" in breakdown
        assert "relationship_distance" in breakdown
        assert "lifecycle_state" in breakdown
        assert "recency" in breakdown


class TestIntentMatchFactor:
    def test_title_match(self):
        factor = IntentMatch()
        v = make_version(title="Event Sourcing")
        assert factor.score("Event Sourcing", v) == 1.0

    def test_understanding_match(self):
        factor = IntentMatch()
        v = make_version(title="Other", understanding="Uses event sourcing pattern")
        assert factor.score("event sourcing", v) == 0.7

    def test_partial_word_match(self):
        factor = IntentMatch()
        v = make_version(title="Event Store Design")
        assert factor.score("event", v) == 0.5

    def test_no_match(self):
        factor = IntentMatch()
        v = make_version(title="Database", understanding="SQL queries")
        assert factor.score("event sourcing", v) == 0.0


class TestKnowledgePriorityFactor:
    def test_decision_highest(self):
        factor = KnowledgePriority()
        v = make_version(knowledge_type=KnowledgeType.DECISION)
        assert factor.score("", v) == 1.0

    def test_discovery_lowest(self):
        factor = KnowledgePriority()
        v = make_version(knowledge_type=KnowledgeType.DISCOVERY)
        assert factor.score("", v) == 0.3


class TestLifecycleStateFactor:
    def test_active_highest(self):
        factor = LifecycleStateFactor()
        v = make_version(lifecycle_state=LifecycleState.ACTIVE)
        assert factor.score("", v) == 1.0

    def test_archived_lowest(self):
        factor = LifecycleStateFactor()
        v = make_version(lifecycle_state=LifecycleState.ARCHIVED)
        assert factor.score("", v) == 0.2


class TestRecencyFactor:
    def test_higher_version_more_recent(self):
        factor = RecencyFactor()
        v1 = make_version(version_number=1)
        v10 = make_version(version_number=10)
        assert factor.score("", v1) < factor.score("", v10)

    def test_capped_at_1(self):
        factor = RecencyFactor()
        v = make_version(version_number=100)
        assert factor.score("", v) == 1.0


class TestRelationshipDistanceFactor:
    def test_no_relationships(self):
        factor = RelationshipDistance()
        v = make_version(relationships=())
        assert factor.score("", v) == 0.5

    def test_some_relationships(self):
        factor = RelationshipDistance()
        rels = (Relationship(target_id=uuid.uuid4(), relationship_type="uses"),)
        v = make_version(relationships=rels)
        assert factor.score("", v) == 0.6


class TestCustomFactors:
    def test_custom_factor_used(self):
        class ConstantFactor(ScoringFactor):
            @property
            def name(self) -> str:
                return "constant"

            @property
            def weight(self) -> float:
                return 1.0

            def score(self, intent: str, version: KnowledgeVersion) -> float:
                return 0.42

        engine = RelevanceEngine(factors=[ConstantFactor()])
        v = make_version()
        results = engine.rank("test", [v])
        assert abs(results[0].score - 0.42) < 1e-9
