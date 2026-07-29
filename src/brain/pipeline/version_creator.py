import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from brain.domain.enums import LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate


class VersionCreator:
    def create(
        self,
        candidate: KnowledgeCandidate,
        identity_id: uuid.UUID | None = None,
    ) -> KnowledgeVersion:
        return KnowledgeVersion(
            identity_id=identity_id or uuid.uuid4(),
            version_number=1,
            knowledge_type=candidate.knowledge_type,
            title=candidate.title,
            understanding=candidate.understanding,
            confidence=candidate.confidence,
            lifecycle_state=LifecycleState.ACTIVE,
            evidence=(
                Evidence(
                    source=candidate.evidence_source.source_type,
                    reference=candidate.evidence_source.content,
                ),
            ),
            relationships=(),
            created_at=candidate.detected_at,
        )
