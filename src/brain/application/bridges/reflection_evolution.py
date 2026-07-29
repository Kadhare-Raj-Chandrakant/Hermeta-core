from dataclasses import dataclass

from brain.application.usecases.models import EvolutionRequest, FindingType, ReflectionFindingDTO


@dataclass(frozen=True)
class ReflectionEvolutionBridge:

    def translate(self, finding: ReflectionFindingDTO) -> EvolutionRequest:
        return EvolutionRequest(
            targets=finding.affected_versions,
            context=finding.finding_type.value,
            metadata=(
                ("source", "reflection"),
                ("confidence", str(finding.confidence)),
            ),
        )
