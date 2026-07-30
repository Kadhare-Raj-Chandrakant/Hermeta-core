import uuid
from datetime import datetime

from brain.application.ports.knowledge_ingestion import KnowledgeIngestionPort
from brain.application.usecases.models import KnowledgeVersionDTO
from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.version_creator import VersionCreator
from brain.repositories.base import KnowledgeRepository
from brain.services.compiler import ContextCompiler, ContextPackage
from brain.services.relevance import RelevanceEngine
from brain.services.selection import SelectionEngine
from brain.domain.task import Task
from brain.validation.engine import ValidationEngine


def _to_dto(version: KnowledgeVersion) -> KnowledgeVersionDTO:
    return KnowledgeVersionDTO(
        version_id=version.version_id,
        identity_id=version.identity_id,
        version_number=version.version_number,
        knowledge_type=version.knowledge_type.value,
        title=version.title,
        understanding=version.understanding,
        confidence=version.confidence,
        lifecycle_state=version.lifecycle_state.value,
        created_at=version.created_at.isoformat(),
    )


class BrainService(KnowledgeIngestionPort):
    def __init__(
        self,
        repository: KnowledgeRepository,
        validator: ValidationEngine,
        version_creator: VersionCreator,
        relevance_engine: RelevanceEngine,
        selection_engine: SelectionEngine,
        context_compiler: ContextCompiler,
    ) -> None:
        self._repository = repository
        self._validator = validator
        self._version_creator = version_creator
        self._relevance_engine = relevance_engine
        self._selection_engine = selection_engine
        self._context_compiler = context_compiler

    def learn(self, candidate: KnowledgeCandidate) -> KnowledgeVersionDTO:
        report = self._validator.validate(candidate)
        if not report.passed:
            failures = [r.reason for r in report.results if not r.passed]
            raise ValueError(f"Invalid candidate: {'; '.join(failures)}")

        identity = self._repository.create_identity()
        version = self._version_creator.create(candidate, identity_id=identity.id)
        self._repository.add_version(version)
        return _to_dto(version)

    def prepare(self, task: Task) -> ContextPackage:
        all_versions = list(self._repository.list_all_versions())
        ranked = self._relevance_engine.rank(task.objective, all_versions)
        selected = self._selection_engine.select(task, ranked)
        return self._context_compiler.compile(task, selected)

    def history(self, identity_id: uuid.UUID) -> tuple[KnowledgeVersionDTO, ...]:
        return tuple(_to_dto(v) for v in self._repository.list_versions(identity_id))

    def latest(self, identity_id: uuid.UUID) -> KnowledgeVersionDTO:
        return _to_dto(self._repository.get_latest_version(identity_id))