from dataclasses import dataclass, replace
from datetime import datetime, timezone

from brain.application.usecases.models import (
    EvolutionRequest,
    EvolutionSummary,
    ExecutionMetrics,
    PlanningMetrics,
)
from brain.application.usecases.unit_of_work import EvolutionUnitOfWork
from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_record import OptimisticConcurrencyError
from brain.evolution.executor import EvolutionExecutor
from brain.evolution.planning import EvolutionPlanner
from brain.repositories.base import KnowledgeRepository
from brain.repositories.evolution_base import EvolutionRepository


@dataclass(frozen=True)
class EvolutionUseCase:
    planner: EvolutionPlanner
    executor: EvolutionExecutor
    knowledge_repository: KnowledgeRepository
    evolution_repository: EvolutionRepository

    def execute(
        self,
        request: EvolutionRequest,
        context: EvolutionContext | None = None,
    ) -> EvolutionSummary:
        start = datetime.now(timezone.utc)

        if context is None:
            context = EvolutionContext()

        plan = self.planner.plan(
            targets=request.targets,
            category=request.context,
            context=context,
        )

        planning_metrics = self._build_planning_metrics(plan, context)
        execution_metrics = ExecutionMetrics()

        uow = EvolutionUnitOfWork()
        if hasattr(self.knowledge_repository, "snapshot"):
            uow.attach(self.knowledge_repository, self.evolution_repository)

        uow.begin()
        tx_start = datetime.now(timezone.utc)

        try:
            record = self.executor.execute(plan, context)
            uow.commit()
            tx_end = datetime.now(timezone.utc)
            execution_metrics = replace(execution_metrics,
                executed_operations=record.operations_count,
                successful_operations=record.operations_count,
                failed_operations=0,
                rolled_back=False,
                optimistic_conflicts=0,
                transaction_duration=tx_end - tx_start,
            )
            overall_success = True
        except OptimisticConcurrencyError as e:
            uow.rollback()
            tx_end = datetime.now(timezone.utc)
            execution_metrics = replace(execution_metrics,
                executed_operations=0,
                successful_operations=0,
                failed_operations=0,
                rolled_back=True,
                optimistic_conflicts=1,
                transaction_duration=tx_end - tx_start,
            )
            overall_success = False
        except Exception:
            uow.rollback()
            tx_end = datetime.now(timezone.utc)
            execution_metrics = replace(execution_metrics,
                executed_operations=0,
                successful_operations=0,
                failed_operations=0,
                rolled_back=True,
                optimistic_conflicts=0,
                transaction_duration=tx_end - tx_start,
            )
            overall_success = False

        end = datetime.now(timezone.utc)

        return EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=overall_success,
            evolution_duration=end - start,
            planning=planning_metrics,
            execution=execution_metrics,
        )

    def _build_planning_metrics(
        self,
        plan: object,
        context: EvolutionContext,
    ) -> PlanningMetrics:
        quarantined = 0
        for key, value in plan.metadata:
            if key == "quarantined_skipped":
                quarantined = int(value)
        return PlanningMetrics(
            planned_operations_count=len(plan.operations),
            affected_targets_count=len(plan.affected_targets),
            quarantined_skipped=quarantined,
        )
