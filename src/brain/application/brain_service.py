import uuid

from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.version_creator import VersionCreator
from brain.repositories.base import KnowledgeRepository
from brain.services.compiler import ContextCompiler, ContextPackage
from brain.services.relevance import RelevanceEngine
from brain.services.selection import SelectionEngine
from brain.domain.task import Task
from brain.validation.engine import ValidationEngine


class BrainService:
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

    def learn(self, candidate: KnowledgeCandidate) -> KnowledgeVersion:
        report = self._validator.validate(candidate)
        if not report.passed:
            failures = [r.reason for r in report.results if not r.passed]
            raise ValueError(f"Invalid candidate: {'; '.join(failures)}")

        identity = self._repository.create_identity()
        version = self._version_creator.create(candidate, identity_id=identity.id)
        self._repository.add_version(version)
        return version

    def prepare(self, task: Task) -> ContextPackage:
        all_versions = list(self._repository.list_all_versions())
        ranked = self._relevance_engine.rank(task.objective, all_versions)
        selected = self._selection_engine.select(task, ranked)
        return self._context_compiler.compile(task, selected)

    def history(self, identity_id: uuid.UUID) -> tuple[KnowledgeVersion, ...]:
        return self._repository.list_versions(identity_id)

    def latest(self, identity_id: uuid.UUID) -> KnowledgeVersion:
        return self._repository.get_latest_version(identity_id)
