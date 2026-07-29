import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.retrieval.request import RetrievalRequest
from brain.retrieval.trigger import RetrievalTrigger
from brain.retrieval.conditions.task_type import TaskTypeCondition
from brain.services.retrieval_bridge import RetrievalPolicyBridge
from brain.services.selection import SelectionPolicy


def _make_request(knowledge_types: tuple[KnowledgeType, ...]) -> RetrievalRequest:
    task = Task(
        task_type=TaskType.IMPLEMENT,
        project="atlas",
        component="auth",
        objective="Implement login",
        constraints=(),
        priority=Priority.MEDIUM,
    )
    return RetrievalRequest(
        task=task,
        trigger_ids=(uuid.uuid4(),),
        knowledge_types=knowledge_types,
        reason="test reason",
    )


EMPTY_POLICY = SelectionPolicy(
    required=(),
    preferred=(),
    optional=(),
    supplemental=(),
)


class TestRetrievalPolicyBridge:
    def test_empty_retrieval_returns_equivalent_policy(self) -> None:
        bridge = RetrievalPolicyBridge()
        request = _make_request(())
        result = bridge.apply(request, EMPTY_POLICY)
        assert result.required == ()
        assert result.preferred == ()
        assert result.optional == ()
        assert result.supplemental == ()

    def test_adds_to_preferred_when_empty(self) -> None:
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.ARCHITECTURE,))
        result = bridge.apply(request, EMPTY_POLICY)
        assert KnowledgeType.ARCHITECTURE in result.preferred

    def test_preserves_existing_required(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.BUG,))
        result = bridge.apply(request, policy)
        assert result.required == (KnowledgeType.BUG,)

    def test_does_not_downgrade_required(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.BUG,))
        result = bridge.apply(request, policy)
        assert KnowledgeType.BUG not in result.preferred
        assert KnowledgeType.BUG in result.required

    def test_preserves_existing_preferred(self) -> None:
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.ARCHITECTURE,))
        result = bridge.apply(request, policy)
        assert result.preferred == (KnowledgeType.ARCHITECTURE,)

    def test_no_duplicate_when_already_preferred(self) -> None:
        policy = SelectionPolicy(
            required=(),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.ARCHITECTURE,))
        result = bridge.apply(request, policy)
        count = sum(1 for kt in result.preferred if kt == KnowledgeType.ARCHITECTURE)
        assert count == 1

    def test_no_duplicate_when_already_optional(self) -> None:
        policy = SelectionPolicy(
            required=(),
            preferred=(),
            optional=(KnowledgeType.DECISION,),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.DECISION,))
        result = bridge.apply(request, policy)
        count = 0
        for tier in [result.required, result.preferred, result.optional, result.supplemental]:
            count += sum(1 for kt in tier if kt == KnowledgeType.DECISION)
        assert count == 1

    def test_no_duplicate_when_already_supplemental(self) -> None:
        policy = SelectionPolicy(
            required=(),
            preferred=(),
            optional=(),
            supplemental=(KnowledgeType.PATTERN,),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.PATTERN,))
        result = bridge.apply(request, policy)
        count = 0
        for tier in [result.required, result.preferred, result.optional, result.supplemental]:
            count += sum(1 for kt in tier if kt == KnowledgeType.PATTERN)
        assert count == 1

    def test_multiple_categories_added_to_preferred(self) -> None:
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.BUG, KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT))
        result = bridge.apply(request, EMPTY_POLICY)
        assert KnowledgeType.BUG in result.preferred
        assert KnowledgeType.ARCHITECTURE in result.preferred
        assert KnowledgeType.COMPONENT in result.preferred

    def test_mixed_existing_and_new(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.BUG, KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT))
        result = bridge.apply(request, policy)
        assert result.required == (KnowledgeType.BUG,)
        assert result.preferred == (KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT)

    def test_no_mutation_of_original_policy(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(KnowledgeType.ARCHITECTURE,),
            optional=(KnowledgeType.DECISION,),
            supplemental=(KnowledgeType.PATTERN,),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.COMPONENT,))
        _ = bridge.apply(request, policy)
        assert policy.required == (KnowledgeType.BUG,)
        assert policy.preferred == (KnowledgeType.ARCHITECTURE,)
        assert policy.optional == (KnowledgeType.DECISION,)
        assert policy.supplemental == (KnowledgeType.PATTERN,)

    def test_result_is_new_instance(self) -> None:
        policy = SelectionPolicy(
            required=(),
            preferred=(),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.ARCHITECTURE,))
        result = bridge.apply(request, policy)
        assert result is not policy

    def test_deterministic_output(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG,),
            preferred=(),
            optional=(),
            supplemental=(),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT))
        r1 = bridge.apply(request, policy)
        r2 = bridge.apply(request, policy)
        assert r1.required == r2.required
        assert r1.preferred == r2.preferred
        assert r1.optional == r2.optional
        assert r1.supplemental == r2.supplemental

    def test_full_policy_unchanged(self) -> None:
        policy = SelectionPolicy(
            required=(KnowledgeType.BUG, KnowledgeType.COMPONENT),
            preferred=(KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION),
            optional=(KnowledgeType.PATTERN, KnowledgeType.RULE),
            supplemental=(KnowledgeType.QUESTION, KnowledgeType.DISCOVERY),
        )
        bridge = RetrievalPolicyBridge()
        request = _make_request((KnowledgeType.BUG, KnowledgeType.GOAL))
        result = bridge.apply(request, policy)
        assert result.required == (KnowledgeType.BUG, KnowledgeType.COMPONENT)
        assert result.preferred == (KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION, KnowledgeType.GOAL)
        assert result.optional == (KnowledgeType.PATTERN, KnowledgeType.RULE)
        assert result.supplemental == (KnowledgeType.QUESTION, KnowledgeType.DISCOVERY)
