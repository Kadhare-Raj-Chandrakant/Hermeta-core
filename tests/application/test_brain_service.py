import uuid
from datetime import datetime, timezone

import pytest

from brain.application.brain_service import BrainService
from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.task import Priority, Task, TaskType
from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence as SourceEvidence
from brain.pipeline.version_creator import VersionCreator
from brain.repositories.memory import InMemoryKnowledgeRepository
from brain.services.compiler import ContextCompiler
from brain.services.relevance import RelevanceEngine
from brain.services.selection import SelectionEngine
from brain.validation.engine import ValidationEngine
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.rules.type_rules import TypeRules


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


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Title",
    understanding: str = "Test understanding with rationale and trade-offs",
    confidence: float = 0.9,
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        evidence_source=SourceEvidence(source_type="conversation", content="test content"),
    )


def make_task(
    task_type: TaskType = TaskType.IMPLEMENT,
    objective: str = "Add feature",
) -> Task:
    return Task(
        task_type=task_type,
        project="hermes-brain",
        component="domain",
        objective=objective,
        constraints=(),
        priority=Priority.MEDIUM,
    )


def make_service() -> BrainService:
    repo = InMemoryKnowledgeRepository()
    return BrainService(
        repository=repo,
        validator=ValidationEngine(rules=(
            ConfidenceRule(threshold=0.3),
            CompletenessRule(),
            EvidenceRule(),
            TypeRules(),
        )),
        version_creator=VersionCreator(),
        relevance_engine=RelevanceEngine(),
        selection_engine=SelectionEngine(),
        context_compiler=ContextCompiler(),
    )


def add_version_to_repo(
    repo: InMemoryKnowledgeRepository,
    knowledge_type: KnowledgeType,
    title: str,
) -> uuid.UUID:
    identity = repo.create_identity()
    version = KnowledgeVersion(
        identity_id=identity.id,
        version_number=1,
        knowledge_type=knowledge_type,
        title=title,
        understanding=f"Understanding of {title}",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )
    repo.add_version(version)
    return identity.id


class TestLearnSuccess:
    def test_learn_creates_version(self):
        service = make_service()
        candidate = make_candidate()
        version = service.learn(candidate)

        assert version.knowledge_type == KnowledgeType.DECISION
        assert version.title == "Test Title"
        assert version.version_number == 1

    def test_learn_stores_in_repository(self):
        service = make_service()
        candidate = make_candidate()
        version = service.learn(candidate)

        latest = service._repository.get_latest_version(version.identity_id)
        assert latest.title == "Test Title"

    def test_learn_returns_version(self):
        service = make_service()
        candidate = make_candidate()
        version = service.learn(candidate)

        assert isinstance(version, KnowledgeVersion)


class TestLearnValidationFailure:
    def test_invalid_candidate_rejected(self):
        service = make_service()
        candidate = make_candidate(title="")
        with pytest.raises(ValueError, match="Invalid candidate"):
            service.learn(candidate)

    def test_out_of_range_confidence_rejected(self):
        service = make_service()
        candidate = make_candidate(confidence=1.5)
        with pytest.raises(ValueError):
            service.learn(candidate)


class TestPrepareSuccess:
    def test_prepare_returns_context_package(self):
        service = make_service()
        add_version_to_repo(service._repository, KnowledgeType.ARCHITECTURE, "Arch")

        task = make_task()
        result = service.prepare(task)

        assert result.task == task

    def test_prepare_empty_repository(self):
        service = make_service()
        task = make_task()
        result = service.prepare(task)

        assert result.sections == ()


class TestPrepareDeterminism:
    def test_same_input_same_output(self):
        service = make_service()
        add_version_to_repo(service._repository, KnowledgeType.ARCHITECTURE, "Arch")

        task = make_task()
        r1 = service.prepare(task)
        r2 = service.prepare(task)

        assert [s.section_type for s in r1.sections] == [s.section_type for s in r2.sections]


class TestHistory:
    def test_history_returns_all_versions(self):
        service = make_service()
        identity_id = add_version_to_repo(service._repository, KnowledgeType.DECISION, "V1")
        v2 = KnowledgeVersion(
            identity_id=identity_id,
            version_number=2,
            knowledge_type=KnowledgeType.DECISION,
            title="V2",
            understanding="Understanding of V2",
            confidence=0.8,
            lifecycle_state=LifecycleState.ACTIVE,
            evidence=(),
            relationships=(),
            created_at=datetime.now(timezone.utc),
        )
        service._repository.add_version(v2)

        result = service.history(identity_id)
        assert len(result) == 2

    def test_history_empty(self):
        service = make_service()
        identity = uuid.uuid4()
        with pytest.raises(Exception):
            service.history(identity)


class TestLatest:
    def test_latest_returns_newest(self):
        service = make_service()
        identity_id = add_version_to_repo(service._repository, KnowledgeType.DECISION, "V1")
        v2 = KnowledgeVersion(
            identity_id=identity_id,
            version_number=2,
            knowledge_type=KnowledgeType.DECISION,
            title="V2",
            understanding="Understanding of V2",
            confidence=0.8,
            lifecycle_state=LifecycleState.ACTIVE,
            evidence=(),
            relationships=(),
            created_at=datetime.now(timezone.utc),
        )
        service._repository.add_version(v2)

        result = service.latest(identity_id)
        assert result.title == "V2"

    def test_latest_unknown_identity(self):
        service = make_service()
        with pytest.raises(Exception):
            service.latest(uuid.uuid4())


class TestDependencyInjection:
    def test_all_collaborators_injected(self):
        repo = InMemoryKnowledgeRepository()
        validator = ValidationEngine(rules=(
            ConfidenceRule(threshold=0.3),
            CompletenessRule(),
            EvidenceRule(),
            TypeRules(),
        ))
        creator = VersionCreator()
        relevance = RelevanceEngine()
        selection = SelectionEngine()
        compiler = ContextCompiler()

        service = BrainService(
            repository=repo,
            validator=validator,
            version_creator=creator,
            relevance_engine=relevance,
            selection_engine=selection,
            context_compiler=compiler,
        )

        assert service._repository is repo
        assert service._validator is validator
        assert service._version_creator is creator
        assert service._relevance_engine is relevance
        assert service._selection_engine is selection
        assert service._context_compiler is compiler


class TestOrchestrationOrder:
    def test_learn_validates_before_creating(self):
        call_order = []
        original_validate = ValidationEngine.validate

        class TrackingValidator(ValidationEngine):
            def validate(self, candidate):
                call_order.append("validate")
                return original_validate(self, candidate)

        service = make_service()
        service._validator = TrackingValidator(rules=(
            ConfidenceRule(threshold=0.3),
            CompletenessRule(),
            EvidenceRule(),
            TypeRules(),
        ))

        candidate = make_candidate()
        service.learn(candidate)

        assert call_order == ["validate"]
