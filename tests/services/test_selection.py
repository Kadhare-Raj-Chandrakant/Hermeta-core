import uuid
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.task import Priority, Task, TaskType
from brain.domain.version import KnowledgeVersion
from brain.services.relevance import ScoredVersion
from brain.services.selection import (
    DEFAULT_POLICIES,
    SelectedKnowledgePackage,
    SelectionEngine,
    SelectionPolicy,
)


def make_version(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test",
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title=title,
        understanding="Understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


def make_scored(version: KnowledgeVersion, score: float = 0.8) -> ScoredVersion:
    return ScoredVersion(version=version, score=score, breakdown={})


def make_task(task_type: TaskType = TaskType.IMPLEMENT) -> Task:
    return Task(
        task_type=task_type,
        project="hermes-brain",
        component="domain",
        objective="Add feature",
        constraints=(),
        priority=Priority.MEDIUM,
    )


class TestRequiredCategorySatisfaction:
    def test_required_types_selected(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        ranked = [make_scored(arch), make_scored(comp)]

        engine = SelectionEngine()
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        types = {v.knowledge_type for v in result.selected}
        assert KnowledgeType.ARCHITECTURE in types
        assert KnowledgeType.COMPONENT in types

    def test_required_always_included(self):
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(),
            optional=(),
            supplemental=(),
        )
        bug = make_version(KnowledgeType.BUG, "Bug")
        ranked = [make_scored(bug)]

        engine = SelectionEngine(policies={TaskType.DEBUG: policy})
        result = engine.select(make_task(TaskType.DEBUG), ranked)

        assert len(result.selected) == 1
        assert result.selected[0].knowledge_type == KnowledgeType.BUG


class TestPreferredCategorySelection:
    def test_preferred_selected_after_required(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        dec = make_version(KnowledgeType.DECISION, "Dec")
        ranked = [make_scored(arch), make_scored(comp), make_scored(dec)]

        engine = SelectionEngine()
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        types = [v.knowledge_type for v in result.selected]
        assert types.index(KnowledgeType.ARCHITECTURE) < types.index(KnowledgeType.DECISION)


class TestOptionalCategoryInclusion:
    def test_optional_included_when_budget_allows(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        rule = make_version(KnowledgeType.RULE, "Rule")
        ranked = [make_scored(arch), make_scored(comp), make_scored(rule)]

        engine = SelectionEngine()
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        types = {v.knowledge_type for v in result.selected}
        assert KnowledgeType.RULE in types


class TestSupplementalCategoryInclusion:
    def test_supplemental_included_when_budget_remains(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        assump = make_version(KnowledgeType.ASSUMPTION, "Assump")
        ranked = [make_scored(arch), make_scored(comp), make_scored(assump)]

        engine = SelectionEngine(max_versions=5)
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        types = {v.knowledge_type for v in result.selected}
        assert KnowledgeType.ASSUMPTION in types

    def test_supplemental_excluded_when_budget_full(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        assump = make_version(KnowledgeType.ASSUMPTION, "Assump")
        ranked = [make_scored(arch), make_scored(comp), make_scored(assump)]

        engine = SelectionEngine(max_versions=2)
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        types = {v.knowledge_type for v in result.selected}
        assert KnowledgeType.ASSUMPTION not in types


class TestBudgetConstraints:
    def test_respects_max_versions(self):
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        versions = [make_version(KnowledgeType.ARCHITECTURE, f"v{i}") for i in range(5)]
        ranked = [make_scored(v) for v in versions]

        engine = SelectionEngine(policies={TaskType.IMPLEMENT: policy}, max_versions=3)
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        assert len(result.selected) == 3
        assert result.budget_used == 3
        assert result.budget_remaining == 0

    def test_budget_remaining_zero_when_full(self):
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        versions = [make_version(KnowledgeType.ARCHITECTURE, f"v{i}") for i in range(5)]
        ranked = [make_scored(v) for v in versions]

        engine = SelectionEngine(policies={TaskType.IMPLEMENT: policy}, max_versions=2)
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        assert result.budget_remaining == 0


class TestStableDeterministicOutput:
    def test_same_input_same_output(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        ranked = [make_scored(arch), make_scored(comp)]

        engine = SelectionEngine()
        r1 = engine.select(make_task(TaskType.IMPLEMENT), ranked)
        r2 = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        assert [v.title for v in r1.selected] == [v.title for v in r2.selected]

    def test_order_independent(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        ranked_a = [make_scored(arch), make_scored(comp)]
        ranked_b = [make_scored(comp), make_scored(arch)]

        engine = SelectionEngine()
        r1 = engine.select(make_task(TaskType.IMPLEMENT), ranked_a)
        r2 = engine.select(make_task(TaskType.IMPLEMENT), ranked_b)

        assert [v.title for v in r1.selected] == [v.title for v in r2.selected]


class TestEmptyInput:
    def test_empty_ranked_returns_empty(self):
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        engine = SelectionEngine(policies={TaskType.IMPLEMENT: policy})
        result = engine.select(make_task(TaskType.IMPLEMENT), [])

        assert result.selected == ()
        assert result.budget_used == 0
        assert result.budget_remaining == 10


class TestMissingRequiredCategories:
    def test_missing_required_not_selected(self):
        rule = make_version(KnowledgeType.RULE, "Rule")
        ranked = [make_scored(rule)]

        engine = SelectionEngine()
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        assert len(result.selected) == 0


class TestDifferentPolicies:
    def test_implement_vs_debug_different_selection(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        bug = make_version(KnowledgeType.BUG, "Bug")
        comp = make_version(KnowledgeType.COMPONENT, "Comp")
        ranked = [make_scored(arch), make_scored(bug), make_scored(comp)]

        engine = SelectionEngine()
        r_impl = engine.select(make_task(TaskType.IMPLEMENT), ranked)
        r_debug = engine.select(make_task(TaskType.DEBUG), ranked)

        impl_types = {v.knowledge_type for v in r_impl.selected}
        debug_types = {v.knowledge_type for v in r_debug.selected}

        assert KnowledgeType.BUG in debug_types
        assert KnowledgeType.BUG not in impl_types


class TestDefaultPolicies:
    def test_all_task_types_have_policies(self):
        for task_type in TaskType:
            assert task_type in DEFAULT_POLICIES

    def test_policies_are_immutable(self):
        for policy in DEFAULT_POLICIES.values():
            assert isinstance(policy, SelectionPolicy)


class TestNoDuplicates:
    def test_no_duplicate_versions(self):
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        ranked = [make_scored(arch), make_scored(arch)]

        engine = SelectionEngine(policies={TaskType.IMPLEMENT: policy})
        result = engine.select(make_task(TaskType.IMPLEMENT), ranked)

        assert len(result.selected) == 1
