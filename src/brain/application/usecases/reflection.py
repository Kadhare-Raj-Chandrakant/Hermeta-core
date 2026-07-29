from dataclasses import dataclass
from datetime import datetime, timezone

from brain.application.usecases.models import ReflectionRequest, ReflectionSummary
from brain.reflection.engine import ReflectionEngine
from brain.reflection.type import ReflectionType
from brain.repositories.base import KnowledgeRepository


@dataclass(frozen=True)
class ReflectionUseCase:
    engine: ReflectionEngine
    repository: KnowledgeRepository

    def execute(self, request: ReflectionRequest) -> ReflectionSummary:
        start = datetime.now(timezone.utc)
        versions = self.repository.list_all_versions()
        report = self.engine.reflect(versions)
        end = datetime.now(timezone.utc)

        return ReflectionSummary(
            reflection_started=True,
            reflection_completed=True,
            reflection_success=True,
            reflection_duration=end - start,
            finding_count=len(report.findings),
            duplicate_count=self._count_type(report, ReflectionType.DUPLICATE),
            conflict_count=self._count_type(report, ReflectionType.CONFLICT),
            obsolete_count=self._count_type(report, ReflectionType.OBSOLETE),
            gap_count=self._count_type(report, ReflectionType.GAP),
        )

    @staticmethod
    def _count_type(report, reflection_type: ReflectionType) -> int:
        return sum(
            1 for f in report.findings if f.reflection_type == reflection_type
        )
