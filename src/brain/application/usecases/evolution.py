from dataclasses import dataclass
from datetime import datetime, timezone

from brain.application.usecases.models import EvolutionRequest, EvolutionSummary
from brain.evolution.evolution import EvolutionEngine
from brain.evolution.evolution_context import EvolutionContext


@dataclass(frozen=True)
class EvolutionUseCase:
    engine: EvolutionEngine

    def execute(
        self,
        request: EvolutionRequest,
        context: EvolutionContext | None = None,
    ) -> EvolutionSummary:
        start = datetime.now(timezone.utc)

        if context is None:
            context = EvolutionContext()

        plan = self.engine.plan(
            targets=request.targets,
            category=request.context,
            context=context,
        )

        end = datetime.now(timezone.utc)

        quarantined = 0
        for key, value in plan.metadata:
            if key == "quarantined_skipped":
                quarantined = int(value)

        return EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=end - start,
            planned_operations_count=len(plan.operations),
            affected_targets_count=len(plan.affected_targets),
            quarantined_skipped=quarantined,
        )
